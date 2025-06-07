#!/bin/bash

# SkyAI Kiosk Mode Runner
# This script hides the desktop and runs SkyAI in true fullscreen mode

echo "Starting SkyAI in Kiosk Mode..."

# Save current desktop state
DESKTOP_SESSION_PID=$(pgrep -f "lxpanel\|lxde-panel\|gnome-panel\|xfce4-panel")

# Hide desktop panels/taskbars
hide_desktop() {
    echo "Hiding desktop elements..."
    
    # Hide LXDE panel (Raspberry Pi OS default)
    killall lxpanel 2>/dev/null
    
    # Hide other common panels
    killall lxde-panel 2>/dev/null
    killall gnome-panel 2>/dev/null
    killall xfce4-panel 2>/dev/null
    
    # Hide desktop icons (PCManFM desktop mode)
    killall pcmanfm 2>/dev/null
    
    # Set black background
    xsetroot -solid black 2>/dev/null
    
    # Disable screen saver and power management
    xset s off 2>/dev/null
    xset -dpms 2>/dev/null
    xset s noblank 2>/dev/null
}

# Restore desktop panels/taskbars
restore_desktop() {
    echo "Restoring desktop elements..."
    
    # Restart LXDE panel if it was running
    if command -v lxpanel >/dev/null 2>&1; then
        lxpanel &
    fi
    
    # Restart desktop icons
    if command -v pcmanfm >/dev/null 2>&1; then
        pcmanfm --desktop &
    fi
    
    # Re-enable screen saver
    xset s on 2>/dev/null
    xset +dpms 2>/dev/null
}

# Cleanup function
cleanup() {
    echo "Cleaning up kiosk mode..."
    restore_desktop
    exit 0
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Hide desktop
hide_desktop

# Wait a moment for desktop to hide
sleep 1

# Run SkyAI
cd /home/woodenfox/skyai

echo "Starting SkyAI..."
echo "Press Ctrl+C to exit kiosk mode"

# Run with error handling
if python3 main_ui.py; then
    echo "SkyAI exited normally"
else
    echo "SkyAI exited with error"
fi

# Cleanup will be called automatically by trap