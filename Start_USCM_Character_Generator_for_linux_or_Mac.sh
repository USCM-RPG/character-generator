#!/usr/bin/env bash

set -e

# Go to script directory
cd "$(dirname "$0")"

# Check if uv exists
if command -v uv >/dev/null 2>&1; then
    echo "uv found."
else
    echo ""
    echo "uv is not installed."
    read -p "The tool 'uv' is needed to run the Character Generator. Do you want to install uv now? (y/n): " choice

    if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
        echo "Aborting."
        exit 1
    fi

    echo "Installing uv..."
    curl -Ls https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Verify uv works
if ! command -v uv >/dev/null 2>&1; then
    echo "uv installation failed. Please restart your terminal and try again."
    exit 1
fi

echo "Starting USCM Character Generator..."

uv sync
uv run character_gui/character_generator.py