# Qwen3-TTS — тест русскоязычного синтеза

Локальный тест модели [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) от Alibaba на русском языке.
Параллельный проект к [VOICE-OVE-RECORDING](../VOICE-OVE-RECORDING/) (XTTS-v2).

## Что работает

- Синтез русского текста через `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- GPU: RTX 4060 / CUDA 12.4
- Время загрузки модели: ~61 сек, генерация: ~15 сек на короткий абзац
- Пример результата: `output/test_ru_1.7b.wav`

## Структура

```
VOICE-OVE-RECORDING-QWEEN3/
├── Qwen3-TTS/               # клонированный репозиторий Qwen3-TTS
├── _venv-site-packages/     # пакеты venv (junction с C:\PythonEnvs\qwen3-tts\Lib\site-packages)
├── output/                  # результаты синтеза
├── logs/                    # логи bg-runner
├── test_ru.py               # скрипт первого теста
├── AGENT_CONTEXT.md         # задачи для терминального агента
└── AGENT_REPORT             # отчёты терминального агента
```

## Окружение — важная особенность

Стандартный `venv` внутри проекта на диске G: **не работает**: Windows блокирует
запуск исполняемых файлов (`python.exe`, `pip.exe`) с внешних дисков.

Решение — разделённая схема:

```
venv (исполняемые файлы) : C:\PythonEnvs\qwen3-tts\
site-packages (пакеты)   : G:\...\VOICE-OVE-RECORDING-QWEEN3\_venv-site-packages\
                           (связаны junction-ом)
```

## Как запускать

```powershell
# Обязательно — направить HuggingFace-кэш на G: (модель ~4.5 ГБ)
$env:HF_HOME = "G:\hf-cache"
$env:HF_HUB_CACHE = "G:\hf-cache\hub"

# Запуск скрипта
C:\PythonEnvs\qwen3-tts\Scripts\python.exe test_ru.py
```

Для длинных задач (скачка модели, синтез) — через bg-runner:

```powershell
C:\Users\Yuri\AppData\Local\Programs\Python\Python313\python.exe `
  "G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\launch.py" `
  --cmd "C:\PythonEnvs\qwen3-tts\Scripts\python.exe test_ru.py" `
  --name "qwen3-synthesis" `
  --logs-dir "logs"
```

## Установка пакетов

```powershell
C:\PythonEnvs\qwen3-tts\Scripts\pip.exe install <пакет>
```

Никаких `--target`, никаких `PYTHONPATH`. Пакеты ставятся в venv штатным способом
и физически попадают на G: через junction.

## Известные нюансы

- `flash-attn` не установлен — не критично, работает на стандартном attention
- `SoX could not be found` — предупреждение, синтез не ломает
- При большой установке через pip: перенаправить temp на G:
  ```powershell
  $env:TMP = "G:\tmp"; $env:TEMP = "G:\tmp"; $env:PIP_CACHE_DIR = "G:\tmp\pip-cache"
  ```
