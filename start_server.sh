#!/bin/bash
# Unix shell script to start the FastAPI server
cd "$(dirname "$0")"
source .venv/bin/activate
uvicorn app.main:app --reload
