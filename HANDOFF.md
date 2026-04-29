# HANDOFF — Qwen3-TTS проект

**Статус на 2026-04-29.** Этот файл — точка входа для новой модели/чата. Прочитайте его первым делом.

## Цель

Тест локального синтеза речи на русском языке через Qwen3-TTS (Alibaba).
Параллельный проект к VOICE-OVE-RECORDING (XTTS-v2). Задача — сравнить качество,
прежде всего: ударения, тембр, эмоциональность на длинных художественных текстах.

GPU: RTX 4060, CUDA 12.4.

## Что уже сделано и работает

1. **Окружение готово.** Нестандартная схема (см. ниже): venv на C:, пакеты на G: через junction.
2. **Qwen3-TTS-12Hz-1.7B-Base** — установлен, модель скачана в `G:\hf-cache`.
3. **Первый синтез прошёл успешно.** Короткий тест — `output/test_ru_1.7b.wav`.
4. **bg-runner** — общий инструмент фонового запуска создан и отлажен в `G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\bg-runner\`.
5. **Длинный тест запущен.** `output/test_ru_1.7b_long.wav` — художественный отрывок ~200 слов с диалогом.

## Принятые решения

### Окружение — junction-схема

**Проблема:** Windows блокирует запуск `venv\Scripts\python.exe` с диска G:.
**Первая попытка:** перенести весь venv на C: — не хватило места (torch ~5 ГБ).
**Решение:**

```
venv (Scripts, python.exe, pip.exe) : C:\PythonEnvs\qwen3-tts\
site-packages (все пакеты)          : G:\...\VOICE-OVE-RECORDING-QWEEN3\_venv-site-packages\
                                      (junction из C:\PythonEnvs\qwen3-tts\Lib\site-packages)
```

**Как запускать:**
```powershell
C:\PythonEnvs\qwen3-tts\Scripts\python.exe <скрипт>
C:\PythonEnvs\qwen3-tts\Scripts\pip.exe install <пакет>
```

**HuggingFace кэш — всегда на G::**
```powershell
$env:HF_HOME = "G:\hf-cache"
$env:HF_HUB_CACHE = "G:\hf-cache\hub"
```

### Модель

Единственная доступная модель: `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (~4.5 ГБ).
Модели 0.6B не существует — статьи врут.

### bg-runner

Фоновый запуск через `_AGENT-TOOLS\bg-runner\launch.py`.
Обязательно использовать **системный** Python 3.13 для самого launch.py:
`C:\Users\Yuri\AppData\Local\Programs\Python\Python313\python.exe`

## Подводные камни (важно)

1. **`shell=True` в bg-runner ломал отслеживание PID.** Windows создаёт цепочку `cmd.exe → python.exe`. bg-runner сохранял PID `cmd.exe`, который умирал быстро — статус преждевременно становился `done`. Исправлено: `shlex.split(cmd, posix=False)` + `shell=False`.

2. **`hf_xet` нужен для скачивания модели.** Без него загрузка зависает на нулевом blob. Установить: `pip install hf_xet`.

3. **`flash-attn` не установлен** — не критично, модель работает на стандартном attention. Предупреждение можно игнорировать.

4. **`SoX could not be found`** — предупреждение, синтез не ломает.

5. **При нехватке места на C: при pip-установке** — перенаправить temp:
   ```powershell
   $env:TMP = "G:\tmp"; $env:TEMP = "G:\tmp"; $env:PIP_CACHE_DIR = "G:\tmp\pip-cache"
   ```

6. **config.json, записанный через PowerShell `Set-Content`, получает BOM** — Python падает с JSONDecodeError. Писать только через Python с `encoding='utf-8'`.

## Параметры модели

Все параметры передаются в `tts.generate_voice_clone(...)`.

| Параметр | Что делает | Текущее значение |
|----------|-----------|-----------------|
| `ref_audio` | **Главный.** WAV-референс — определяет голос (пол, возраст, тембр) | URL от Alibaba (женский) |
| `language` | Язык синтеза | `"Russian"` |
| `x_vector_only_mode` | True — только эмбеддинг голоса; False — ICL-режим с примером речи | `True` |
| `temperature` | Случайность основного генератора | `0.9` |
| `repetition_penalty` | Штраф за повтор аудио-токенов | `1.05` |
| `subtalker_temperature` | Случайность субмодуля (финальные аудио-токены) | `0.9` |
| `subtalker_top_k/p` | Семплинг субмодуля | `50 / 1.0` |
| `max_new_tokens` | Максимальная длина генерации | `2048` |

**Ключевой вывод:** параметры sampling не меняют голос. Голос меняется только через `ref_audio`.

## Текущая проблема — голос детский, женский

Первый синтез дал детский женский голос, потому что `ref_audio` указывает на URL Alibaba с английской женской речью.

**Следующий шаг:** попробовать `eugene.wav` из соседнего проекта как референс:

```python
ref_audio = r"G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\voices\eugene.wav"
```

Это WAV взрослого мужского голоса. Менять только эту строку в `test_ru.py`, всё остальное оставить.

## Структура проекта

```
VOICE-OVE-RECORDING-QWEEN3/
├── Qwen3-TTS/                  # клонированный репозиторий
├── _venv-site-packages/        # пакеты (junction → C:\PythonEnvs\qwen3-tts\Lib\site-packages)
├── output/
│   ├── test_ru_1.7b.wav        # короткий тест (20 слов)
│   └── test_ru_1.7b_long.wav   # длинный тест (~200 слов, диалог)
├── logs/                       # логи bg-runner
├── test_ru.py                  # скрипт синтеза
├── README.md                   # установка и запуск
├── HANDOFF.md                  # этот файл
├── AGENT_CONTEXT.md            # задачи для терминального агента
└── AGENT_REPORT                # отчёты терминального агента
```

## Соседние проекты и инструменты

- **VOICE-OVE-RECORDING** (`G:\AI\_MY_PROGRAMMING_3\VOICE-OVE-RECORDING\`) — рабочий XTTS-v2 проект с FastAPI UI. Голоса в `voices/` можно использовать как референсы для Qwen3.
- **_AGENT-TOOLS** (`G:\AI\_MY_PROGRAMMING_3\_AGENT-TOOLS\`) — общие инструменты: `bg-runner` для фонового запуска задач.

## Рабочая схема: два агента

- **Sonnet в чате** — архитектор: обсуждает решения, пишет HANDOFF, формулирует задания.
- **Haiku/Codex в терминале** — исполнитель: пишет код, запускает тесты, обновляет AGENT_CONTEXT и AGENT_REPORT.

Терминальный агент читает `AGENT_CONTEXT.md`. Архитектор читает `HANDOFF.md` и `AGENT_REPORT`.

## Что делать дальше

1. **Ближайшее:** сменить `ref_audio` на `eugene.wav`, запустить синтез длинного текста, оценить голос.
2. **Если голос устроит:** сравнить качество ударений с XTTS-v2 на одном и том же тексте.
3. **Если качество Qwen3 достаточное:** думать о UI (адаптация существующего FastAPI-фронта из VOICE-OVE-RECORDING).
4. **Если нет:** вернуться к XTTS-v2 и продолжать там (TASK-004 в том проекте ещё открыта).
