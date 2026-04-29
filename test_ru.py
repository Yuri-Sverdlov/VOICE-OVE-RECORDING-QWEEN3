from __future__ import annotations

import os
import time
from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_PATH = OUTPUT_DIR / "test_ru_1.7b.wav"


def main() -> int:
    os.environ.setdefault("HF_HOME", r"G:\hf-cache")
    os.environ.setdefault("HF_HUB_CACHE", r"G:\hf-cache\hub")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model_name = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
    ref_audio = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/clone_2.wav"
    text = "Тихий вечер опускался на деревню. В воздухе пахло сеном и дымом."

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
        language="Russian",
        ref_audio=ref_audio,
        ref_text=None,
        x_vector_only_mode=True,
        max_new_tokens=2048,
        do_sample=True,
        top_k=50,
        top_p=1.0,
        temperature=0.9,
        repetition_penalty=1.05,
        subtalker_dosample=True,
        subtalker_top_k=50,
        subtalker_top_p=1.0,
        subtalker_temperature=0.9,
    )
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    g1 = time.time()

    sf.write(str(OUTPUT_PATH), wavs[0], sr)
    print(f"Generation done in {g1 - g0:.2f}s", flush=True)
    print(f"Saved: {OUTPUT_PATH}", flush=True)
    print(f"Done: {sr} Hz, {len(wavs[0])} samples", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
