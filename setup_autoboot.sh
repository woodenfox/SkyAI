#!/bin/bash

# SkyAI Auto-boot Setup Script
# This script configures your Raspberry Pi to automatically start SkyAI on boot

echo "SkyAI Auto-boot Setup Script"
echo "============================"
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root"
    exit 1
fi

PROJECT_DIR=$(pwd)
USER=$(whoami)

echo "Setting up auto-boot for SkyAI..."
echo "Project directory: $PROJECT_DIR"
echo "User: $USER"
echo

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/skyai.service"
echo "Creating systemd service file..."

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=SkyAI Voice Assistant
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=$USER
Environment=DISPLAY=:0
Environment=PULSE_RUNTIME_PATH=/run/user/1000/pulse
WorkingDirectory=$PROJECT_DIR
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/python3 $PROJECT_DIR/main_ui.py
Restart=always
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF

echo "✓ Systemd service file created"

# Enable the service
echo "Enabling SkyAI service..."
sudo systemctl daemon-reload
sudo systemctl enable skyai.service

echo "✓ SkyAI service enabled"

# Configure auto-login (optional)
echo
read -p "Do you want to enable auto-login for user '$USER'? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Configuring auto-login..."
    
    # Create auto-login configuration
    sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
    sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $USER --noclear %I \$TERM
EOF
    
    echo "✓ Auto-login configured"
fi

# Configure boot to desktop
echo
read -p "Do you want to boot to desktop environment? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting boot to desktop..."
    sudo systemctl set-default graphical.target
    echo "✓ Boot to desktop configured"
fi

# Create startup script for desktop environment
echo "Creating desktop startup script..."
DESKTOP_DIR="/home/$USER/.config/autostart"
mkdir -p "$DESKTOP_DIR"

tee "$DESKTOP_DIR/skyai.desktop" > /dev/null <<EOF
[Desktop Entry]
Type=Application
Name=SkyAI Voice Assistant
Exec=python3 $PROJECT_DIR/main_ui.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

echo "✓ Desktop startup script created"

# Install dependencies if not already installed
echo
read -p "Do you want to install/update Python dependencies? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Create launcher script for manual execution
echo "Creating launcher script..."
tee "$PROJECT_DIR/launch_skyai.sh" > /dev/null <<EOF
#!/bin/bash
cd "$PROJECT_DIR"
export DISPLAY=:0
python3 main_ui.py
EOF

chmod +x "$PROJECT_DIR/launch_skyai.sh"
echo "✓ Launcher script created: $PROJECT_DIR/launch_skyai.sh"

# Create maintenance scripts
echo "Creating maintenance scripts..."

# Stop script
tee "$PROJECT_DIR/stop_skyai.sh" > /dev/null <<EOF
#!/bin/bash
sudo systemctl stop skyai.service
pkill -f "python3.*main_ui.py"
echo "SkyAI stopped"
EOF

# Start script
tee "$PROJECT_DIR/start_skyai.sh" > /dev/null <<EOF
#!/bin/bash
sudo systemctl start skyai.service
echo "SkyAI started"
EOF

# Status script
tee "$PROJECT_DIR/status_skyai.sh" > /dev/null <<EOF
#!/bin/bash
echo "SkyAI Service Status:"
sudo systemctl status skyai.service --no-pager
echo
echo "Running Processes:"
ps aux | grep "python3.*main_ui.py" | grep -v grep
EOF

chmod +x "$PROJECT_DIR"/*.sh
echo "✓ Maintenance scripts created"

echo
echo "================================================"
echo "SkyAI Auto-boot Setup Complete!"
echo "================================================"
echo
echo "What was configured:"
echo "- Systemd service: skyai.service"
echo "- Desktop autostart entry"
echo "- Launcher script: ./launch_skyai.sh"
echo "- Maintenance scripts: start_skyai.sh, stop_skyai.sh, status_skyai.sh"
echo
echo "Manual Commands:"
echo "- Start: sudo systemctl start skyai.service"
echo "- Stop: sudo systemctl stop skyai.service"
echo "- Status: sudo systemctl status skyai.service"
echo "- Disable autoboot: sudo systemctl disable skyai.service"
echo
echo "For testing, run: ./launch_skyai.sh"
echo
echo "Reboot your Raspberry Pi to test auto-boot functionality!"
echo