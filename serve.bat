@echo off
REM Start FastAPI server in debug mode with uvicorn
@REM uv run uvicorn app.main:app --reload --log-level debug

uv run uvicorn app.main:app --reload