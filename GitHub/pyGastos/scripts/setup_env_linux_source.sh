#!/bin/bash

# Exit immediately if a command fails
set -e

# Function to handle errors
error_handler() {
    echo "❌ ERROR: Something went wrong while setting up the environment."
    echo "Script aborted."
    return 1 2>/dev/null || exit 1
}
trap error_handler ERR

# # Navigate to project root
# cd "$(dirname "$0")/.."

# Get the directory where the script is located, even if sourced
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to project root (one level up from /scripts/)
cd "$SCRIPT_DIR/.."

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

# To execute from root:
# chmod +x scripts/setup_and_exec_linux.sh
# scripts/setup_and_exec_linux.sh

# To execute from root/scripts/:
# chmod +x setup_and_exec_linux.sh
# ./setup_and_exec_linux.sh
