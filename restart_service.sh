#!/bin/bash
# Restart Brain in a Jar service with updated configuration

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Brain in a Jar Service Restart${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Kill any running brain-in-jar processes
echo -e "${YELLOW}Stopping any running processes...${NC}"
pkill -f "run_with_web" || echo "No processes to kill"
sleep 2

# Check if systemd service exists
if [ -f "/etc/systemd/system/brain-in-jar.service" ]; then
    echo -e "${GREEN}Updating systemd service...${NC}"

    # Copy updated service file
    sudo cp brain-in-jar.service /etc/systemd/system/

    # Reload systemd
    sudo systemctl daemon-reload

    # Restart service
    echo -e "${GREEN}Restarting brain-in-jar service...${NC}"
    sudo systemctl restart brain-in-jar

    # Wait for service to start
    sleep 5

    # Show status
    echo ""
    echo -e "${GREEN}Service Status:${NC}"
    sudo systemctl status brain-in-jar --no-pager || true

else
    echo -e "${YELLOW}Systemd service not installed. Starting manually...${NC}"

    # Activate virtual environment
    source venv/bin/activate

    # Start in background
    nohup python3 -m src.scripts.run_with_web \
        --mode matrix \
        --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
        --web-host 127.0.0.1 \
        --web-port 8095 \
        --ram-limit-subject 6.0 \
        --ram-limit-observer 7.0 \
        --ram-limit-god 7.0 \
        > logs/brain-jar.log 2>&1 &

    echo "Started with PID: $!"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Restart Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Changes applied:"
echo "  ✅ Hybrid CPU+GPU model offloading (prevents GPU OOM)"
echo "  ✅ GPU memory watchdog (kills process at 85% GPU usage)"
echo "  ✅ Conservative RAM limits (6GB/7GB/7GB per instance)"
echo "  ✅ Systemd memory limits (24GB hard limit)"
echo ""
echo "Check service:"
echo "  • Status: sudo systemctl status brain-in-jar"
echo "  • Logs: sudo journalctl -u brain-in-jar -f"
echo "  • Web: http://localhost:8095"
echo "  • External: https://brain.art-ai.me"
echo ""
echo "Monitor GPU usage:"
echo "  • nvidia-smi -l 1"
echo "  • watch -n 2 'nvidia-smi'"
echo ""
