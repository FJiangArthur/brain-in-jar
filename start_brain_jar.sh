#!/bin/bash
#
# Brain in a Jar - Startup Script
# Starts the web interface on port 8095 (localhost)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Brain in a Jar - Starting...                 ║"
echo "║           Cyberpunk AI Consciousness Experiment            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running on Jetson
if [ -f "/etc/nv_tegra_release" ]; then
    echo -e "${GREEN}✓ Jetson Orin detected${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Not running on Jetson, some features may not work${NC}"
fi

# Check for models
echo -e "\n${CYAN}Checking for models...${NC}"
MODEL_COUNT=$(find models -name "*.gguf" 2>/dev/null | wc -l)

if [ "$MODEL_COUNT" -eq 0 ]; then
    echo -e "${RED}✗ No models found in models/ directory${NC}"
    echo -e "${YELLOW}  Run the following to download models:${NC}"
    echo -e "    cd models && bash download.sh"
    echo -e "\n${YELLOW}  Or provide a model path with --model flag${NC}"

    # Ask if user wants to continue anyway
    read -p "Continue without model (will fail to start)? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Exiting...${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Found $MODEL_COUNT model(s)${NC}"
    find models -name "*.gguf" -exec basename {} \; | head -5 | sed 's/^/  - /'
fi

# Check Python dependencies
echo -e "\n${CYAN}Checking Python dependencies...${NC}"
if python3 -c "import llama_cpp, flask, flask_socketio" 2>/dev/null; then
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}✗ Missing dependencies${NC}"
    echo -e "${YELLOW}  Run: pip install -e .${NC}"
    exit 1
fi

# Run watchdog tests
echo -e "\n${CYAN}Testing protection systems...${NC}"
if python3 test_watchdogs.py 2>&1 | grep -q "All watchdog systems are operational"; then
    echo -e "${GREEN}✓ All watchdog systems operational${NC}"
else
    echo -e "${YELLOW}⚠ Some watchdog systems failed, but continuing...${NC}"
fi

# Get mode from user
echo -e "\n${CYAN}Select experiment mode:${NC}"
echo "  1) single  - One isolated AI instance"
echo "  2) matrix  - Three-tier hierarchy (Subject/Observer/GOD)"
echo "  3) peer    - Two AIs communicating as peers"
read -p "Enter mode [1-3] (default: 1): " MODE_CHOICE

case $MODE_CHOICE in
    2) MODE="matrix" ;;
    3) MODE="peer" ;;
    *) MODE="single" ;;
esac

echo -e "${GREEN}Selected mode: $MODE${NC}"

# Get model path
FIRST_MODEL=$(find models -name "*.gguf" 2>/dev/null | head -1)
if [ -n "$FIRST_MODEL" ]; then
    echo -e "\n${CYAN}Using model: $FIRST_MODEL${NC}"
    MODEL_ARG="--model $FIRST_MODEL"
else
    echo -e "\n${YELLOW}No model specified${NC}"
    MODEL_ARG=""
fi

# Configure RAM limits for matrix mode
if [ "$MODE" = "matrix" ]; then
    echo -e "\n${CYAN}Configuring matrix hierarchy memory limits...${NC}"
    RAM_ARGS="--ram-limit-subject 6.0 --ram-limit-observer 7.0 --ram-limit-god 7.0"
    echo -e "${YELLOW}  Subject:  6.0 GB${NC}"
    echo -e "${YELLOW}  Observer: 7.0 GB${NC}"
    echo -e "${YELLOW}  GOD:      7.0 GB${NC}"
else
    RAM_ARGS="--ram-limit-subject 8.0"
fi

# Start the system
echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Starting Brain in a Jar Web Interface${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}"
echo "  Mode:     $MODE"
echo "  Port:     8095 (localhost only)"
echo "  URL:      http://localhost:8095"
echo "  Login:    admin / admin123 (CHANGE THIS!)"
echo ""
echo "  Protection Systems Active:"
echo "    • Memory limits (soft kill at configured GB)"
echo "    • GPU watchdog (kill at 85% GPU memory)"
echo "    • System RAM watchdog (kill at 85% system RAM)"
echo "    • Thermal watchdog (kill at 85°C)"
echo "    • Adaptive monitoring (1s intervals when >70%)"
echo -e "${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

# Start the server
python3 -m src.scripts.run_with_web \
    --mode "$MODE" \
    $MODEL_ARG \
    $RAM_ARGS \
    --web-host 127.0.0.1 \
    --web-port 8095
