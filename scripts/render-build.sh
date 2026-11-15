#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
.venv/bin/pip install --disable-pip-version-check -r requirements.txt
.venv/bin/python scripts/build.py
