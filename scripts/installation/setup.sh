#!/bin/bash

# School Management System - Setup Script

echo "=========================================="
echo "School Management System - Setup"
echo "=========================================="
echo ""

# Get project root (2 levels up from this script)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to project root
cd "$PROJECT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed!"
    echo "Please install pip3"
    exit 1
fi

echo "Installing required packages..."
pip3 install -r requirements.txt

echo ""
echo "=========================================="
echo "Starting Installation Wizard..."
echo "=========================================="
echo ""

# Run installation wizard
python3 "$SCRIPT_DIR/install_wizard.py"

echo ""
echo "Setup complete!"
