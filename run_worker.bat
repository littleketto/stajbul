@echo off
title StajBul - Autonomous Worker
cd /d "%~dp0"
echo ========================================================
echo   StajBul Otonom Kazima ve AI Zenginlestirme Servisi
echo ========================================================
echo.
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe -m src.cli.commands worker --interval-hours 6
pause
