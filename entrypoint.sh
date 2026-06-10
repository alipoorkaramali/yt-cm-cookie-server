#!/bin/bash
PORT=${PORT:-8080}
echo "Starting gunicorn on port $PORT"
exec gunicorn app:app --bind 0.0.0.0:$PORT
