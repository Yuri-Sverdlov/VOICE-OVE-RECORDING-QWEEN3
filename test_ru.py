from __future__ import annotations

import json
import os
import time
from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel


PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_ROOT / "config.json"
TEXT_FILE = Path(r"G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\text\_za_lopatoj_4.txt")


def main() -> int:
    os.environ.setdefault("HF_HOME", r"G:\hf-cache")
    os.environ.setdefault("HF_HUB_CACHE", r"G:\hf-cache\hub")

    cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

    output_dir = PROJECT_ROOT / cfg["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "test_ru_1.7b_eugene.wav"

    model_name = cfg["model"]
    ref_audio = cfg["ref_audio"]
    text = TEXT_FILE.read_text(encoding="utf-8").strip()

    print(f"Loading model: {model_name}", flush=True)
    t0 = time.time()
    tts = Qwen3TTSModel.from_pretrained(
        model_name,
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    t1 = time.time()
    print(f"Model ready in {t1 - t0:.2f}s", flush=True)

    print("Generating Russian synthesis...", flush=True)
    g0 = time.time()
    wavs, sr = tts.generate_voice_clone(
        text=text,
        language=cfg["language"],
        ref_audio=ref_audio,
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
    g1 = time.time()

    sf.write(str(output_path), wavs[0], sr)
    print(f"Generation done in {g1 - g0:.2f}s", flush=True)
    print(f"Saved: {output_path}", flush=True)
    print(f"Done: {sr} Hz, {len(wavs[0])} samples", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
