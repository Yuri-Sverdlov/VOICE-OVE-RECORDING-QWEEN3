@echo off
set HF_HOME=G:\hf-cache
set HF_HUB_CACHE=G:\hf-cache\hub
start http://127.0.0.1:8001
C:\PythonEnvs\qwen3-tts\Scripts\python.exe server.py
