#!/bin/bash

# Go to project directory
cd /home/mopy/Projects/Gastos_Lite/pygastoslite || exit 1

# Create venv if not exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

# Gunicorn Configuration
APP_MODULE="libs.app:app"  # From libs/app.py, imports app
BIND="0.0.0.0:8101"  # 127.0.0.1:8101 for only localhost
WORKERS=1  # More workers usefeull for multiple users
LOGFILE="gunicorn.log"
PIDFILE="gunicorn.pid"

echo "Starting Flask app with Gunicorn..."
exec .venv/bin/gunicorn \
  --workers $WORKERS \
  --bind $BIND \
  --pid $PIDFILE \
  --log-file $LOGFILE \
  --access-logfile - \
  --error-logfile - \
  $APP_MODULE

# Command example: gunicorn -w 4 -b 0.0.0.0:8101 libs.app:app
