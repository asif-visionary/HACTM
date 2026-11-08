@echo off
echo ======================================================================
echo Starting HACTM — Hierarchical Adaptive Cyber Trust Mesh
echo ======================================================================
echo.
echo Launching Backend API on http://127.0.0.1:8080 ...
start "HACTM Backend API (Port 8080)" cmd /k "set PYTHONPATH=backend\src && python -m uvicorn hactm.api.app:app --host 127.0.0.1 --port 8080 --reload"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo Launching Frontend UI on http://localhost:5173 ...
start "HACTM Frontend UI (Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo ======================================================================
echo Both HACTM services are running!
echo Frontend Workspace: http://localhost:5173/
echo Backend Swagger API: http://127.0.0.1:8080/docs
echo ======================================================================

