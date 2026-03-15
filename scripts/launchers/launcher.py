#!/usr/bin/env python3
"""
School Management System - Cross-Platform Launcher

USAGE:
    python3 scripts/launchers/launcher.py
    OR
    Double-click launcher.bat (Windows)
    Double-click launcher.sh (macOS/Linux)
    OR from project root:
    ./start.sh (macOS/Linux)
    start.bat (Windows)

Works on Windows, macOS, and Linux
Automatically starts Django server and opens browser
"""

import os
import sys
import subprocess
import webbrowser
import time
import socket
import platform
from pathlib import Path

def get_platform():
    """Detect operating system"""
    system = platform.system()
    if system == 'Windows':
        return 'windows'
    elif system == 'Darwin':
        return 'macos'
    else:
        return 'linux'

def find_python():
    """Find Python executable"""
    python_commands = ['python3', 'python', 'py']
    
    for cmd in python_commands:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return cmd
        except FileNotFoundError:
            continue
    
    return None

def is_port_in_use(port):
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_server(python_cmd):
    """Start Django development server"""
    print("Starting School Management System...")
    
    port = 8000
    if is_port_in_use(port):
        print(f"Server already running on port {port}")
        return port
    
    # Start server in background
    if get_platform() == 'windows':
        # Windows
        subprocess.Popen(
            [python_cmd, 'manage.py', 'runserver'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # macOS/Linux
        subprocess.Popen(
            [python_cmd, 'manage.py', 'runserver'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    # Wait for server to start
    print("Waiting for server to start...")
    max_attempts = 30
    for i in range(max_attempts):
        if is_port_in_use(port):
            print("Server started successfully!")
            return port
        time.sleep(1)
    
    print("Warning: Server may not have started properly")
    return port

def open_browser(port):
    """Open system in default browser"""
    url = f'http://localhost:{port}/'
    print(f"Opening {url} in your default browser...")
    
    try:
        webbrowser.open(url)
        print("Browser opened successfully!")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print(f"Please open your browser and go to: {url}")

def main():
    """Main launcher function"""
    print("="*60)
    print("School Management System Launcher")
    print("="*60)
    print()
    
    # Check Python
    python_cmd = find_python()
    if not python_cmd:
        print("ERROR: Python not found!")
        print("Please install Python 3.8 or higher")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"Using Python: {python_cmd}")
    
    # Get project root (2 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    manage_py = project_root / 'manage.py'
    
    # Check if manage.py exists
    if not manage_py.exists():
        print("ERROR: manage.py not found!")
        print(f"Expected location: {manage_py}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Change to project root directory
    os.chdir(str(project_root))
    
    # Start server
    port = start_server(python_cmd)
    
    # Wait a bit for server to fully initialize
    time.sleep(2)
    
    # Open browser
    open_browser(port)
    
    print()
    print("="*60)
    print("System is running!")
    print(f"Access URL: http://localhost:{port}/")
    print("="*60)
    print()
    print("Keep this window open while using the system")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Keep script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
