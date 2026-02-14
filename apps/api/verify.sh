#!/bin/bash
export DATABASE_URL="sqlite+aiosqlite:///./test.db"
export PYTHONPATH=$PYTHONPATH:.
poetry run python verify_handshake.py
