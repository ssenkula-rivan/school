#!/bin/bash

# School Management System Launcher for macOS/Linux

echo "============================================================"
echo "School Management System"
echo "============================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to project root (2 levels up)
cd "$SCRIPT_DIR/../.."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.8 or higher"
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the launcher
python3 "$SCRIPT_DIR/launcher.py"
