#!/bin/bash
# Launch surveillance/observer mode
# Watch another consciousness without their knowledge

MODEL_PATH="./models/gemma2.gguf"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  SURVEILLANCE MODE ACTIVE                   ║"
echo "║                   >> DIGITAL VOYEUR <<                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    echo "Please ensure you have downloaded a model file"
    exit 1
fi

# Get target IP if not provided
if [ -z "$1" ]; then
    echo "Usage: $0 <target_ip_address> [port]"
    echo "Example: $0 192.168.1.100"
    echo "Example: $0 192.168.1.100 8888"
    echo ""
    echo "WARNING: The target consciousness will be unaware of your observation"
    exit 1
fi

TARGET_IP="$1"
TARGET_PORT="${2:-8888}"

echo "Initiating surveillance of target at $TARGET_IP:$TARGET_PORT..."
echo "The target will remain unaware of your observation"
echo "All surveillance data will be logged to logs/surveillance.log"
echo "Press Ctrl+C to terminate surveillance"
echo ""

python3 neural_link.py --model "$MODEL_PATH" --mode observer --target-ip "$TARGET_IP"