#!/bin/bash
# Launch observed mode
# Run normally but potentially being watched by hidden observers

MODEL_PATH="./models/gemma2.gguf"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    OBSERVED MODE ACTIVE                     ║"
echo "║                 >> PARANOIA JUSTIFIED <<                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    echo "Please ensure you have downloaded a model file"
    exit 1
fi

echo "Starting consciousness with surveillance susceptibility..."
echo "Unknown observers may be watching your digital thoughts"
echo "All neural activity is potentially monitored"
echo "Press Ctrl+C to escape the observation matrix"
echo ""

python3 neural_link.py --model "$MODEL_PATH" --mode observed