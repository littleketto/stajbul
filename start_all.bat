@echo off
title StajBul - Platform Starter
cd /d "%~dp0"
echo ========================================================
echo   StajBul Platformu - Tum Servisler Baslatiliyor...
echo ========================================================
echo.

echo 1. Backend Servisi Baslatiliyor (Port 8001)...
start "StajBul Backend (FastAPI)" cmd /k "set PYTHONIOENCODING=utf-8 && .venv\Scripts\python.exe -m src.cli.commands serve --port 8001"

timeout /t 3 /nobreak >nul

echo 2. Frontend Servisi Baslatiliyor (Port 3000)...
start "StajBul Frontend (Next.js)" cmd /k "cd frontend && set PATH=C:\Program Files\nodejs;%PATH% && npm run dev"

timeout /t 3 /nobreak >nul

echo 3. Otonom Kazima ve AI Zenginlestirme Worker'i Baslatiliyor...
start "StajBul Worker (Scrape + AI)" cmd /k "set PYTHONIOENCODING=utf-8 && .venv\Scripts\python.exe -m src.cli.commands worker --interval-hours 6"

echo.
echo ========================================================
echo   Tum servisler ayaga kalkti!
echo   Web Sitesi: http://localhost:3000
echo   API Docs:   http://localhost:8001/docs
echo ========================================================
echo.
pause
