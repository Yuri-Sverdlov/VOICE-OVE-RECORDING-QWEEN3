# AGENT_CONTEXT - Qwen3-TTS test project

This file is written for a terminal agent. Read it before doing anything.

Last updated: 2026-04-29

---

## Project goal

Test Qwen3-TTS (open-source TTS by Alibaba) on Russian-language text.
Compare quality against XTTS-v2 used in the sibling project.

Project directory: `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\`

Sibling project (XTTS-v2, working): `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\`

---

## Python environment - CANONICAL DECISION (2026-04-29)

The project runtime uses a venv launched from `C:` so Windows does not block
its executables, but the heavy package payload is stored on `G:` through a
junction because `C:` did not have enough free space for the full CUDA stack.

Actual working layout:

```text
Project files : G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\
venv root     : C:\PythonEnvs\qwen3-tts\
python        : C:\PythonEnvs\qwen3-tts\Scripts\python.exe
pip           : C:\PythonEnvs\qwen3-tts\Scripts\pip.exe
site-packages : C:\PythonEnvs\qwen3-tts\Lib\site-packages
             => G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\_venv-site-packages
```

Always run scripts with:

```powershell
C:\PythonEnvs\qwen3-tts\Scripts\python.exe <script>
```

Always install packages with:

```powershell
C:\PythonEnvs\qwen3-tts\Scripts\pip.exe install ...
```

For Hugging Face downloads:

```powershell
$env:HF_HOME = "G:\hf-cache"
$env:HF_HUB_CACHE = "G:\hf-cache\hub"
```

If a large install needs temp/cache space, use:

```powershell
$env:TMP = "G:\tmp"
$env:TEMP = "G:\tmp"
$env:PIP_CACHE_DIR = "G:\tmp\pip-cache"
```

Do NOT use PYTHONPATH hacks.
Do NOT use system Python directly for project runtime.

---

## TASK QUEUE

Tasks are listed in priority order. Mark each task `[x]` when fully done.
Do not delete completed tasks.

---

### [x] TASK-001 (failed) - Create venv inside project on G:

Attempted and abandoned. Resulted in a broken torch installation due to
Windows blocking venv binaries on G:. See `AGENT_REPORT`.

---

### [x] TASK-002 - Rebuild environment: clean venv on C:

Completed.

Completed result:
1. Deleted broken `venv` on `G:`
2. Created new venv at `C:\PythonEnvs\qwen3-tts`
3. Rebuilt `site-packages` as a junction to:
   `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\_venv-site-packages`
4. Installed:
   - `torch 2.6.0+cu124`
   - `torchvision 0.21.0+cu124`
   - `torchaudio 2.6.0+cu124`
5. Installed `Qwen3-TTS` from cloned repo
6. Verified:
   - `torch.__version__ == 2.6.0+cu124`
   - `torch.cuda.is_available() == True`

---

### [x] TASK-003 - Create shared bg-runner tool in _AGENT-TOOLS

Completed.

Created:
- `G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\launch.py`
- `G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\status.py`
- `G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\README.md`

Verified:
- smoke test launched via system `Python 3.13`
- background process received `job_id`, `pid`, `.json`, `.log`
- `status.py` updated `running -> done`
- log tail printed successfully after Windows-console encoding fix

---

### [x] TASK-004 - Run first Russian-language synthesis test

Completed.

Important facts discovered during execution:
- there is no usable `0.6B` path in the updated task spec
- the real first successful test used:
  - `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- the test script is:
  - `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\test_ru.py`
- output file produced:
  - `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\output\test_ru_1.7b.wav`

Execution notes:
- first background run stalled while trying to fetch the model from Hugging Face
- installing `hf_xet` resolved the fetch path issue
- final successful run was:
  - `job_id=qwen3-tts-test-2_20260429_153355`
- timings from log:
  - `Model ready in 61.38s`
  - `Generation done in 14.73s`
- output metadata:
  - `24000 Hz`
  - `140160 samples`

Warnings observed but non-fatal:
- `SoX could not be found!`
- `flash-attn is not installed`

---

### [ ] TASK-005 - Синтез с голосом Евгения и текстом из файла

`test_ru.py` уже обновлён архитектором. Менять его не нужно.

Что изменилось в скрипте:
- `ref_audio` теперь `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\voices\eugene.wav`
- текст читается из файла `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\text\_za_lopatoj_4.txt`
- результат пишется в `output\test_ru_1.7b_eugene.wav`

Запустить через bg-runner:

```powershell
$env:HF_HOME = "G:\hf-cache"
$env:HF_HUB_CACHE = "G:\hf-cache\hub"
C:\Users\Yuri\AppData\Local\Programs\Python\Python313\python.exe `
  "G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\launch.py" `
  --cmd "C:\PythonEnvs\qwen3-tts\Scripts\python.exe G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\test_ru.py" `
  --name "qwen3-eugene-test" `
  --logs-dir "G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\logs"
```

Дождаться завершения (проверять статус каждые 30–60 сек).
Убедиться что `output\test_ru_1.7b_eugene.wav` создан и не нулевого размера.
Отчитаться в `AGENT_REPORT`: job_id, тайминги, размер файла, ошибки если были.

---

TASK-005 completion note:
- Completed on `2026-04-29`
- Successful bg-runner job:
  - `job_id=qwen3-eugene-test_20260429_164629`
- Timings from log:
  - `Model ready in 9.13s`
  - `Generation done in 79.49s`
- Output file:
  - `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\output\test_ru_1.7b_eugene.wav`
- Output metadata:
  - `24000 Hz`
  - `971520 samples`
  - `1,943,084 bytes`

### [ ] TASK-006 - Исправить bg-runner: автоматический финальный статус

Проблема: после завершения процесса JSON-статус остаётся `running`, пока вручную
не вызвать `status.py`. Нужен автоматический финализатор.

Решение: `launch.py` запускает рядом с основным процессом лёгкий скрипт-финализатор,
который ждёт завершения основного и сам обновляет JSON.

#### Что создать

Новый файл: `G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\_finalizer.py`

Скрипт принимает три аргумента:
- `--pid` — PID основного процесса
- `--status-file` — путь к JSON-файлу статуса
- `--log-file` — путь к лог-файлу

Поведение:
1. Ждёт завершения процесса с заданным PID через `psutil.wait_for_pid(pid)`
   или в цикле `while psutil.pid_exists(pid): time.sleep(2)`
2. Читает лог-файл, ищет слово `Traceback`
3. Если нашёл — `status = "error"`, иначе — `status = "done"`
4. Читает текущий JSON, обновляет `status` и `finished_at`, записывает обратно

#### Что изменить в `launch.py`

После старта основного процесса добавить запуск финализатора:

```python
import sys
finalizer = Path(__file__).parent / "_finalizer.py"
subprocess.Popen(
    [sys.executable, str(finalizer),
     "--pid", str(proc.pid),
     "--status-file", str(status_path),
     "--log-file", str(log_path)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
```

#### Проверка

1. Smoke-тест: запустить `ping 127.0.0.1 -n 5` через launch.py
2. Подождать ~10 сек без вызова status.py
3. Прочитать JSON-файл напрямую — статус должен быть `done`
4. Убедиться что `finished_at` заполнен

Отчитаться в `AGENT_REPORT`.

---

### [ ] TASK-007 - Создать FastAPI UI для Qwen3-TTS

Адаптация существующего UI из соседнего проекта VOICE-OVE-RECORDING.
Создать два файла: `server.py` и `static/index.html` в корне этого проекта.

---

#### Справка: что уже есть

- `config.json` — все параметры модели (читать оттуда, не хардкодить)
- `voices/` — пока пустая, можно скопировать туда `eugene.wav` из соседнего проекта
- `output/` — сюда писать результаты
- `test_ru.py` — пример того как грузить модель и вызывать синтез

Референс для копирования структуры:
- `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\server.py`
- `G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\static\index.html`

---

#### server.py — что создать

Скопировать структуру из XTTS-сервера, заменив только специфику модели.

**Импорты и конфиг:**
```python
import json, os, sys, threading, uuid
from pathlib import Path
from typing import Any

os.environ.setdefault("HF_HOME", r"G:\hf-cache")
os.environ.setdefault("HF_HUB_CACHE", r"G:\hf-cache\hub")

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
```

**Загрузка конфига** — читать из `config.json`, поля:
`model`, `ref_audio`, `language`, `output_dir`,
`temperature`, `repetition_penalty`, `subtalker_temperature`,
`subtalker_top_k`, `subtalker_top_p`, `max_new_tokens`

**Загрузка модели** (`get_tts()`):
```python
import torch
from qwen_tts import Qwen3TTSModel

_tts_model = Qwen3TTSModel.from_pretrained(
    CFG["model"],
    device_map="cuda:0",
    dtype=torch.bfloat16,
)
```

**Синтез** (`synthesize_to_file(text, ref_audio_path, out_path, cfg, job_id)`):
```python
import soundfile as sf

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
sf.write(str(out_path), wavs[0], sr)
return len(wavs[0]) / sr  # duration
```

**Эндпоинты** — те же что в XTTS-сервере:
- `GET /` — отдать `static/index.html`
- `GET /voices` — список WAV из `voices/`
- `GET /sample/{voice}` — стримить WAV для прослушивания
- `POST /generate` — запустить синтез в фоне, вернуть `job_id`
- `GET /status/{job_id}` — статус + прогресс
- `GET /download/{job_id}` — скачать результат
- `GET /history` — последние 10 файлов

**Модель запроса:**
```python
class GenerateRequest(BaseModel):
    text: str
    voice: str          # имя файла из voices/ без расширения
    language: str = "Russian"
    temperature: float = 0.9
    repetition_penalty: float = 1.05
    subtalker_temperature: float = 0.9
```

**Запуск:**
```python
if __name__ == "__main__":
    import uvicorn
    threading.Thread(target=get_tts, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
```

Порт **8001** (не 8000 — чтобы не конфликтовал с XTTS-сервером).

---

#### static/index.html — что создать

Скопировать из XTTS-проекта, внести изменения:

1. **Заголовок** → `Qwen3-TTS`

2. **Выбор голоса** — оставить список карточек из `voices/` с мини-плеером,
   как в XTTS UI. Голос передаётся как имя файла.

3. **Убрать** слайдер "выразительность" (он управлял RUAccent — здесь не нужен).

4. **Добавить** три слайдера:
   - `temperature` (0.5 – 1.0, шаг 0.05, default 0.9) — "Выразительность"
   - `repetition_penalty` (1.0 – 1.3, шаг 0.05, default 1.05) — "Чистота звука"
   - `subtalker_temperature` (0.5 – 1.0, шаг 0.05, default 0.9) — "Стабильность"

5. **Добавить** селектор языка:
   ```
   Auto | Russian | English | Chinese
   ```
   Default: Russian.

6. Всё остальное — textarea, загрузка .txt, прогресс-бар, плеер, история — **без изменений**.

---

#### Подготовка голоса

Скопировать `eugene.wav` в `voices/` этого проекта:
```powershell
Copy-Item "G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\voices\eugene.wav" `
          "G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING-QWEEN3\voices\eugene.wav"
```

---

#### Установка зависимостей

```powershell
C:\PythonEnvs\qwen3-tts\Scripts\pip.exe install fastapi uvicorn
```

---

#### Проверка

1. Запустить сервер:
   ```powershell
   $env:HF_HOME = "G:\hf-cache"
   $env:HF_HUB_CACHE = "G:\hf-cache\hub"
   C:\PythonEnvs\qwen3-tts\Scripts\python.exe server.py
   ```
2. Открыть `http://127.0.0.1:8001` в браузере
3. Ввести короткий текст, выбрать eugene, нажать синтез
4. Дождаться прогресса, послушать результат

Отчитаться в `AGENT_REPORT`: запустился ли сервер, открылся ли UI,
прошёл ли первый синтез, любые ошибки.

---

## Notes for terminal agent

TASK-006 completion note:
- Completed on `2026-04-29`
- Created:
  - `G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\_finalizer.py`
- Updated:
  - `G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\launch.py`
- Smoke test:
  - `job_id=smoke-test-7_20260429_171215`
- Direct JSON check without `status.py`:
  - initial/final JSON already contained `status=done`
  - `finished_at=2026-04-29T17:12:22`
- Result:
  - bg-runner now finalizes JSON automatically after process exit
- Always use `C:\PythonEnvs\qwen3-tts\Scripts\python.exe`
- Always use `C:\PythonEnvs\qwen3-tts\Scripts\pip.exe`
- Heavy packages live behind the `site-packages` junction on `G:`
- Shared `bg-runner` is separate from the Qwen venv and can use system Python for smoke tests
- For Hugging Face model downloads, keep cache on `G:\hf-cache`
- Do not install anything into system Python 3.13
- Report results in `AGENT_REPORT`
- Trust this file over older reports for architectural decisions
