from __future__ import annotations

import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any

os.environ.setdefault("HF_HOME", r"G:\hf-cache")
os.environ.setdefault("HF_HUB_CACHE", r"G:\hf-cache\hub")

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
STATIC_DIR = ROOT / "static"
VOICES_DIR = ROOT / "voices"

DEFAULT_CONFIG: dict[str, Any] = {
    "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    "ref_audio": "",
    "language": "Russian",
    "output_dir": "output",
    "temperature": 0.9,
    "repetition_penalty": 1.05,
    "subtalker_temperature": 0.9,
    "subtalker_top_k": 50,
    "subtalker_top_p": 1.0,
    "max_new_tokens": 2048,
}


def load_config() -> dict[str, Any]:
    cfg = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        cfg.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    return cfg


CFG = load_config()
OUTPUT_DIR = (ROOT / CFG["output_dir"]).resolve()
STATIC_DIR.mkdir(exist_ok=True)
VOICES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_tts_model = None
_tts_lock = threading.Lock()

_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()

_history: list[dict[str, Any]] = []
_history_lock = threading.Lock()
HISTORY_MAX = 10


def _set_job(job_id: str, **kwargs: Any) -> None:
    with _jobs_lock:
        if job_id not in _jobs:
            _jobs[job_id] = {
                "status": "pending",
                "progress": "Pending",
                "progress_pct": 0,
                "file": None,
                "error": None,
                "voice": None,
            }
        _jobs[job_id].update(kwargs)


def _add_history(job_id: str, filename: str, voice: str, duration: float) -> None:
    entry = {
        "id": job_id,
        "file": filename,
        "voice": voice,
        "duration_sec": round(duration, 1),
    }
    with _history_lock:
        _history.insert(0, entry)
        del _history[HISTORY_MAX:]


def get_tts():
    global _tts_model
    with _tts_lock:
        if _tts_model is None:
            import torch
            from qwen_tts import Qwen3TTSModel

            print(f"[server] Loading {CFG['model']}...", flush=True)
            _tts_model = Qwen3TTSModel.from_pretrained(
                CFG["model"],
                device_map="cuda:0",
                dtype=torch.bfloat16,
            )
            print("[server] Model ready.", flush=True)
        return _tts_model


def synthesize_to_file(
    text: str,
    ref_audio_path: Path,
    out_path: Path,
    cfg: dict[str, Any],
    job_id: str,
) -> float:
    import soundfile as sf
    import torch

    _set_job(job_id, progress="Loading model", progress_pct=10)
    tts = get_tts()

    _set_job(job_id, progress="Synthesizing", progress_pct=55)
    wavs, sr = tts.generate_voice_clone(
        text=text,
        language=cfg["language"],
        ref_audio=str(ref_audio_path),
        ref_text=None,
        x_vector_only_mode=True,
        max_new_tokens=cfg["max_new_tokens"],
        do_sample=True,
        top_k=50,
        top_p=1.0,
        temperature=cfg["temperature"],
        repetition_penalty=cfg["repetition_penalty"],
        subtalker_dosample=True,
        subtalker_top_k=cfg["subtalker_top_k"],
        subtalker_top_p=cfg["subtalker_top_p"],
        subtalker_temperature=cfg["subtalker_temperature"],
    )
    if torch.cuda.is_available():
        torch.cuda.synchronize()

    _set_job(job_id, progress="Saving file", progress_pct=90)
    sf.write(str(out_path), wavs[0], sr)
    return len(wavs[0]) / sr


def _run_synthesis(job_id: str, text: str, ref_audio_path: Path, voice: str, runtime_cfg: dict[str, Any]) -> None:
    out_filename = f"{job_id}_{voice}.wav"
    out_path = OUTPUT_DIR / out_filename
    try:
        duration = synthesize_to_file(text, ref_audio_path, out_path, runtime_cfg, job_id)
        _set_job(
            job_id,
            status="done",
            progress="Done",
            progress_pct=100,
            file=out_filename,
            voice=voice,
        )
        _add_history(job_id, out_filename, voice, duration)
    except Exception as exc:
        _set_job(job_id, status="error", progress="Error", error=str(exc), progress_pct=100)
        print(f"[server] Job {job_id} failed: {exc}", flush=True)


from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Qwen3-TTS UI")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class GenerateRequest(BaseModel):
    text: str
    voice: str
    language: str = "Russian"
    temperature: float = 0.9
    repetition_penalty: float = 1.05
    subtalker_temperature: float = 0.9


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html = STATIC_DIR / "index.html"
    if not html.exists():
        raise HTTPException(500, "static/index.html not found")
    return HTMLResponse(html.read_text(encoding="utf-8"))


@app.get("/voices")
async def list_voices():
    wavs = sorted(VOICES_DIR.glob("*.wav"))
    return [{"name": path.stem, "file": path.name} for path in wavs]


@app.get("/sample/{voice}")
async def sample(voice: str):
    path = VOICES_DIR / f"{voice}.wav"
    if not path.exists():
        raise HTTPException(404, f"Voice '{voice}' not found")
    return FileResponse(str(path), media_type="audio/wav", filename=path.name)


@app.post("/generate")
async def generate(req: GenerateRequest):
    voice_path = VOICES_DIR / f"{req.voice}.wav"
    if not voice_path.exists():
        raise HTTPException(400, f"Voice '{req.voice}' not found")
    if not req.text.strip():
        raise HTTPException(400, "Text is empty")

    job_id = str(uuid.uuid4())[:8]
    runtime_cfg = CFG.copy()
    runtime_cfg.update(
        {
            "language": req.language,
            "temperature": req.temperature,
            "repetition_penalty": req.repetition_penalty,
            "subtalker_temperature": req.subtalker_temperature,
        }
    )
    _set_job(
        job_id,
        status="running",
        progress="Queued",
        progress_pct=5,
        file=f"{job_id}_{req.voice}.wav",
        error=None,
        voice=req.voice,
    )
    threading.Thread(
        target=_run_synthesis,
        args=(job_id, req.text, voice_path, req.voice, runtime_cfg),
        daemon=True,
    ).start()
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def status(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "Job not found")
    return job


@app.get("/download/{job_id}")
async def download(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job or not job.get("file"):
        raise HTTPException(404, "Result not found")
    path = OUTPUT_DIR / job["file"]
    if not path.exists():
        raise HTTPException(404, "Result file missing on disk")
    return FileResponse(str(path), media_type="audio/wav", filename=path.name)


@app.get("/history")
async def history():
    with _history_lock:
        return list(_history)


if __name__ == "__main__":
    import uvicorn

    threading.Thread(target=get_tts, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
