#!/bin/bash

# Creat and activate venv and install reqs
source /home/mopy/Projects/Gastos_Lite/pygastoslite/scripts/setup_env_linux_source.sh

APP_MODULE="wsgi:app"
BIND="0.0.0.0:8101"
WORKERS=1
LOGFILE="gunicorn.log"
PIDFILE="gunicorn.pid"

echo "Starting Flask app with Gunicorn..."
exec gunicorn \
  --workers $WORKERS \
  --bind $BIND \
  --pid $PIDFILE \
  --log-file $LOGFILE \
  --access-logfile - \
  --error-logfile - \
  $APP_MODULE