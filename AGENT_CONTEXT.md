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

## Notes for terminal agent

- Always use `C:\PythonEnvs\qwen3-tts\Scripts\python.exe`
- Always use `C:\PythonEnvs\qwen3-tts\Scripts\pip.exe`
- Heavy packages live behind the `site-packages` junction on `G:`
- Shared `bg-runner` is separate from the Qwen venv and can use system Python for smoke tests
- For Hugging Face model downloads, keep cache on `G:\hf-cache`
- Do not install anything into system Python 3.13
- Report results in `AGENT_REPORT`
- Trust this file over older reports for architectural decisions
