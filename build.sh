#!/bin/bash
# Build script for Render.com
# Explicitly sets Python version and installs dependencies

set -e

echo "🔧 Setting up Python environment..."

# Ensure Python 3.10 is used
export PYTHON_VERSION=3.10.12

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "✅ Build complete!"

