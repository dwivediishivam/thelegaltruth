#!/bin/sh
# startup.sh
gunicorn --bind=0.0.0.0 --timeout 600 app:app