#!/bin/bash
export DATABASE_URL="sqlite+aiosqlite:///./test.db"
export PYTHONPATH=$PYTHONPATH:.
poetry run python scan_domain.py "$@"
