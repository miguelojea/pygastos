#!/bin/bash

# Exit immediately if a command fails
set -e

# Function to handle errors
error_handler() {
    echo "❌ ERROR: Something went wrong while setting up the environment."
    echo "Script aborted."
    exit 1
}
trap error_handler ERR

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if already inside a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Already inside a virtual environment: $VIRTUAL_ENV"
else
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
        echo "Virtual environment created."
    else
        echo "Virtual environment already created."
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "Virtual environment activated."
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    echo "Requirements installed."
fi

# Execute main.py
python3 main.py

# To execute from root:
# chmod +x scripts/setup_env_linux.sh
# scripts/setup_env_linux.sh

# To execute from root/scripts/:
# chmod +x setup_env_linux.sh
# ./setup_env_linux.sh
