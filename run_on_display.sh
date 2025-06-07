#!/bin/bash

# Script to run SkyAI on the Pi's physical display from SSH

echo "Starting SkyAI on Raspberry Pi display..."

# Set the display to the Pi's screen
export DISPLAY=:0

# Make sure we can access the display
xhost +local: 2>/dev/null

# Check if X server is running
if ! pgrep -x "Xorg" > /dev/null; then
    echo "X server not running. Starting desktop environment..."
    sudo systemctl start lightdm
    sleep 5
fi

# Run SkyAI on the Pi's display
cd /home/woodenfox/skyai
python3 main_ui.py

echo "SkyAI stopped."