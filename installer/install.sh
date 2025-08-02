#!/bin/bash

echo "🚨 InsiderWatch Setup Starting..."

# Exit on any error
set -e

# Step 1: Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Step 2: Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv insiderwatch_venv

# Step 3: Activate the virtual environment
source insiderwatch_venv/bin/activate

# Step 4: Upgrade pip inside venv (optional but recommended)
echo "⬆️  Upgrading pip in venv..."
pip install --upgrade pip

# Step 5: Install packages from offline bundle
echo "📁 Installing Python packages from offline folder..."
pip install --no-index --find-links=insiderwatch_packages/ -r requirements.txt

# Step 6: Create logs/ folder if not present
mkdir -p logs

echo "✅ Installation complete."
echo "➡️ To run InsiderWatch: "
echo "   source insiderwatch_venv/bin/activate && python main.py"
