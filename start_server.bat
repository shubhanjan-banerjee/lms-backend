@echo off
REM Windows batch file to start the FastAPI server
cd /d %~dp0
call .venv\Scripts\activate
uvicorn app.main:app --reload
