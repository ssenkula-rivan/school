#!/usr/bin/env python3
"""
Create desktop shortcut for School Management System
Works on Windows and macOS
"""

import os
import sys
import platform
from pathlib import Path

def get_desktop_path():
    """Get desktop path for current OS"""
    system = platform.system()
    
    if system == 'Windows':
        return Path.home() / 'Desktop'
    elif system == 'Darwin':  # macOS
        return Path.home() / 'Desktop'
    else:  # Linux
        return Path.home() / 'Desktop'

def create_windows_shortcut():
    """Create Windows shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        print("Installing required packages for Windows...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pywin32', 'winshell'])
        import winshell
        from win32com.client import Dispatch
    
    desktop = get_desktop_path()
    shortcut_path = desktop / 'School Management System.lnk'
    
    # Get project root (2 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    launcher_path = project_root / 'scripts' / 'launchers' / 'launcher.bat'
    
    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(launcher_path)
    shortcut.WorkingDirectory = str(project_root)
    shortcut.IconLocation = sys.executable
    shortcut.save()
    
    print(f"✓ Shortcut created: {shortcut_path}")

def create_macos_shortcut():
    """Create macOS application using shell script"""
    print("\nCreating professional macOS application...")
    
    # Get path to create_macos_app.sh in same directory
    script_path = Path(__file__).parent / 'create_macos_app.sh'
    
    try:
        import subprocess
        result = subprocess.run(
            ['bash', str(script_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("✓ macOS application created successfully!")
        else:
            print(f"✗ Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error creating macOS app: {e}")
        return False
    
    return True

def create_linux_shortcut():
    """Create Linux desktop entry"""
    desktop = get_desktop_path()
    shortcut_path = desktop / 'school-management-system.desktop'
    
    # Get project root (2 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    launcher_path = project_root / 'scripts' / 'launchers' / 'launcher.sh'
    
    # Create desktop entry
    desktop_entry = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=School Management System
Comment=Launch School Management System
Exec=bash "{launcher_path}"
Path={project_root}
Terminal=false
Categories=Education;
'''
    
    shortcut_path.write_text(desktop_entry)
    shortcut_path.chmod(0o755)
    
    print(f"✓ Desktop entry created: {shortcut_path}")

def main():
    """Create desktop shortcut based on OS"""
    print("="*60)
    print("Creating Desktop Shortcut")
    print("="*60)
    print()
    
    system = platform.system()
    print(f"Detected OS: {system}")
    
    try:
        if system == 'Windows':
            create_windows_shortcut()
        elif system == 'Darwin':
            create_macos_shortcut()
        else:
            create_linux_shortcut()
        
        print()
        print("✓ Desktop shortcut created successfully!")
        print()
        print("You can now launch the system by clicking the icon on your desktop")
        
    except Exception as e:
        print(f"\n✗ Error creating shortcut: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        input("\nPress Enter to exit...")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
