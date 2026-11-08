@echo off
echo Starting HACTM Backend (Port 8080)...
set PYTHONPATH=backend\src
python -m uvicorn hactm.api.app:app --host 127.0.0.1 --port 8080 --reload

