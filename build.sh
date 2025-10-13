#!/usr/bin/env bash
# build.sh - Render build script

set -o errexit  # exit on error

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed successfully!"
