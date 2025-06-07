#!/bin/bash

echo "Raspberry Pi Display Status Check"
echo "================================="
echo

# Check if X server is running
echo "X Server Status:"
if pgrep -x "Xorg" > /dev/null; then
    echo "✓ X server is running"
else
    echo "✗ X server is NOT running"
    echo "  Start with: sudo systemctl start lightdm"
fi
echo

# Check display environment
echo "Display Environment:"
echo "DISPLAY=$DISPLAY"
echo "Current user: $(whoami)"
echo

# Check if desktop session is active
echo "Desktop Session:"
if pgrep -x "lxsession\|gnome-session\|xfce4-session" > /dev/null; then
    echo "✓ Desktop session is active"
else
    echo "✗ No desktop session detected"
fi
echo

# Check display permissions
echo "Display Permissions:"
if xhost > /dev/null 2>&1; then
    echo "✓ Can access display"
else
    echo "✗ Cannot access display"
    echo "  Try: export DISPLAY=:0 && xhost +local:"
fi
echo

# List active displays
echo "Active Displays:"
who
echo

echo "Troubleshooting:"
echo "1. Make sure your Pi has a monitor connected"
echo "2. Try: sudo systemctl start lightdm"
echo "3. Run: export DISPLAY=:0"
echo "4. Use VNC for remote desktop access"