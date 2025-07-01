#!/bin/bash
# Unix shell script to start the FastAPI server
cd "$(dirname "$0")"
source .venv/bin/activate
uv run uvicorn app.main:app --reload
