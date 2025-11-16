#!/bin/bash
# Installation script for Brain in a Jar systemd service
# Run this with: sudo ./install_service.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Brain in a Jar Service Installer${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run with sudo: sudo ./install_service.sh${NC}"
    exit 1
fi

PROJECT_DIR="/home/artjiang/brain-in-jar"

# Ensure logs directory exists with proper permissions
echo -e "${GREEN}Setting up logs directory...${NC}"
mkdir -p "$PROJECT_DIR/logs/crash_reports"
mkdir -p "$PROJECT_DIR/logs/model_io"
chown -R artjiang:artjiang "$PROJECT_DIR/logs"
chmod -R 755 "$PROJECT_DIR/logs"

# Install service file
echo -e "${GREEN}Installing systemd service...${NC}"
cp "$PROJECT_DIR/brain-in-jar.service" /etc/systemd/system/
chmod 644 /etc/systemd/system/brain-in-jar.service

# Reload systemd
echo -e "${GREEN}Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Enable service for auto-start on boot
echo -e "${GREEN}Enabling service for auto-start...${NC}"
systemctl enable brain-in-jar

# Check if service is already running
if systemctl is-active --quiet brain-in-jar; then
    echo -e "${YELLOW}Service is currently running. Restarting...${NC}"
    systemctl restart brain-in-jar
else
    echo -e "${GREEN}Starting service...${NC}"
    systemctl start brain-in-jar
fi

# Wait a moment for service to start
sleep 3

# Check status
echo ""
echo -e "${GREEN}Service Status:${NC}"
systemctl status brain-in-jar --no-pager || true

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Service details:"
echo "  • Auto-start on boot: ENABLED"
echo "  • Web interface: http://localhost:8095"
echo "  • Cloudflare tunnel: Configure to point to localhost:8095"
echo ""
echo "Useful commands:"
echo "  • Check status:  sudo systemctl status brain-in-jar"
echo "  • View logs:     sudo journalctl -u brain-in-jar -f"
echo "  • Stop service:  sudo systemctl stop brain-in-jar"
echo "  • Restart:       sudo systemctl restart brain-in-jar"
echo "  • Disable:       sudo systemctl disable brain-in-jar"
echo ""
echo "Logs are persisted in:"
echo "  • Conversation DB: $PROJECT_DIR/logs/conversations.db"
echo "  • Crash reports:   $PROJECT_DIR/logs/crash_reports.log"
echo "  • Model I/O:       $PROJECT_DIR/logs/model_io/"
echo "  • System logs:     /var/log/syslog (search for 'brain-in-jar')"
echo ""
echo -e "${YELLOW}Note: Default web login is 'admin' / 'admin123'${NC}"
echo -e "${YELLOW}CHANGE THIS IMMEDIATELY!${NC}"
echo ""
