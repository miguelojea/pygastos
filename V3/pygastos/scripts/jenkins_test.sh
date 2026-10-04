#!/bin/bash

echo "---> Activate venv"
. venv/bin/activate

echo "---> Run tests."
pytest tests/ -v
