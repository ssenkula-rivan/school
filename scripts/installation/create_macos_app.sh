#!/bin/bash

# Professional macOS Application Creator
# Creates a proper .app bundle that works like any Mac application

APP_NAME="School Management System"
APP_DIR="$HOME/Desktop/$APP_NAME.app"

# Get project root (2 levels up from this script)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "============================================================"
echo "Creating macOS Application: $APP_NAME"
echo "============================================================"
echo ""

# Create app bundle structure
echo "Creating application bundle..."
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Create the main executable script
cat > "$APP_DIR/Contents/MacOS/launcher" << 'LAUNCHER_SCRIPT'
#!/bin/bash

# Get the directory where the app is located
APP_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
PROJECT_DIR="__PROJECT_DIR__"

# Change to project directory
cd "$PROJECT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python 3 is not installed!\n\nPlease install Python 3.8 or higher from python.org" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Server already running, opening browser..."
    open http://localhost:8000/
    exit 0
fi

# Start the server in background
python3 manage.py runserver > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "Starting server..."
for i in {1..30}; do
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo "Server started!"
        break
    fi
    sleep 1
done

# Open browser
open http://localhost:8000/

# Show notification
osascript -e 'display notification "School Management System is running on http://localhost:8000" with title "School Management System" sound name "Glass"'

# Keep the app running
echo "School Management System is running..."
echo "Close this window to stop the server"
wait $SERVER_PID
LAUNCHER_SCRIPT

# Replace placeholder with actual project directory
sed -i '' "s|__PROJECT_DIR__|$PROJECT_DIR|g" "$APP_DIR/Contents/MacOS/launcher"

# Make executable
chmod +x "$APP_DIR/Contents/MacOS/launcher"

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleName</key>
    <string>School Management System</string>
    <key>CFBundleDisplayName</key>
    <string>School Management System</string>
    <key>CFBundleIdentifier</key>
    <string>com.school.management</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
PLIST

# Create a simple icon using iconutil (if available)
if command -v sips &> /dev/null && command -v iconutil &> /dev/null; then
    echo "Creating application icon..."
    
    # Create iconset directory
    ICONSET="$APP_DIR/Contents/Resources/AppIcon.iconset"
    mkdir -p "$ICONSET"
    
    # Create a simple colored square as base icon
    # In production, replace this with your actual logo
    for size in 16 32 128 256 512; do
        sips -z $size $size /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/BookmarkIcon.icns --out "$ICONSET/icon_${size}x${size}.png" 2>/dev/null
    done
    
    # Convert to icns
    iconutil -c icns "$ICONSET" -o "$APP_DIR/Contents/Resources/AppIcon.icns" 2>/dev/null
    rm -rf "$ICONSET"
    
    # Update Info.plist with icon
    /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string AppIcon" "$APP_DIR/Contents/Info.plist" 2>/dev/null
fi

# Set app icon using default system icon
touch "$APP_DIR/Icon$'\r'"
SetFile -a C "$APP_DIR" 2>/dev/null || true

echo ""
echo "✓ Application created successfully!"
echo ""
echo "Location: $APP_DIR"
echo ""
echo "You can now:"
echo "  1. Double-click the app to launch"
echo "  2. Drag it to your Applications folder"
echo "  3. Add it to your Dock"
echo ""
echo "============================================================"
