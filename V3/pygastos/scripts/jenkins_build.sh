#!/bin/bash

if [ ! -d venv ]; then
    echo "---> Create venv"
    python3 -m venv venv
else
    echo "---> venv already exists"
fi

echo "---> Activate venv"
. venv/bin/activate

echo "---> Install requirements.txt"
pip install -r requirements.txt
