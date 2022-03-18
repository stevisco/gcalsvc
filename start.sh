#!/usr/bin/env bash
set -e

python main.py &
gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app &

wait -n
