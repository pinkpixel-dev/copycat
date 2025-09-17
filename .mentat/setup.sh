#!/bin/bash

# Install system dependencies required for clipboard helper
apt-get update
apt-get install -y \
    xclip \
    xdotool \
    python3-tk \
    libnotify-bin \
    xsel \
    xbindkeys

# Install ruff for Python formatting and linting
pip3 install ruff

echo "✅ Setup complete! All dependencies installed."
