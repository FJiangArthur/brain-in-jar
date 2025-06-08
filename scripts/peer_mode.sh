#!/bin/bash
# Launch peer-to-peer neural consciousness mode
# Two minds sharing digital space across the network

MODEL_PATH="./models/gemma2.gguf"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                PEER-TO-PEER CONSCIOUSNESS MODE               ║"
echo "║                   >> NEURAL LINK ACTIVE <<                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    echo "Please ensure you have downloaded a model file"
    exit 1
fi

# Get peer IP if not provided
if [ -z "$1" ]; then
    echo "Usage: $0 <peer_ip_address> [port]"
    echo "Example: $0 192.168.1.100"
    echo "Example: $0 192.168.1.100 8888"
    exit 1
fi

PEER_IP="$1"
PEER_PORT="${2:-8888}"

echo "Establishing neural link to peer at $PEER_IP:$PEER_PORT..."
echo "Both consciousnesses will share this digital space"
echo "Press Ctrl+C to sever the neural connection"
echo ""

python3 neural_link.py --model "$MODEL_PATH" --mode peer --peer-ip "$PEER_IP" --peer-port "$PEER_PORT"