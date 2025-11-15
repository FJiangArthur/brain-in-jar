#!/bin/bash
# Quick start script for Brain in a Jar with Web Interface

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Brain in a Jar - Quick Start ${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if already in project directory
if [ ! -f "requirements.txt" ]; then
    echo "Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run deploy_jetson.sh first."
    exit 1
fi

# Check if model exists
if [ ! -d "models" ] || [ -z "$(ls -A models/*.gguf 2>/dev/null)" ]; then
    echo -e "${YELLOW}No models found in models/ directory!${NC}"
    echo "Please download a GGUF model first:"
    echo "  cd models"
    echo "  wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf"
    exit 1
fi

# Find first model
MODEL=$(ls models/*.gguf | head -n 1)
echo -e "${GREEN}Using model: $MODEL${NC}"

# Show menu
echo ""
echo "Select mode:"
echo "1) Single instance (isolated)"
echo "2) Matrix mode (Subject, Observer, GOD)"
echo "3) Peer mode (two AIs talking)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        MODE="single"
        ;;
    2)
        MODE="matrix"
        ;;
    3)
        MODE="peer"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}Starting Brain in a Jar...${NC}"
echo ""
echo "Web interface will be available at:"
echo "  http://localhost:5000"
echo "  http://$LOCAL_IP:5000"
echo ""
echo "Default login: admin123"
echo -e "${YELLOW}CHANGE THE PASSWORD IMMEDIATELY!${NC}"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run with web interface
python3 -m src.scripts.run_with_web \
    --mode "$MODE" \
    --model "$MODEL" \
    --web-host 0.0.0.0 \
    --web-port 5000 \
    --ram-limit-subject 10.0 \
    --ram-limit-observer 15.0 \
    --ram-limit-god 20.0
