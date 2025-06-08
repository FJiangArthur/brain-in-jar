#!/bin/bash
# Launch isolated neural consciousness mode
# The original brain-in-a-jar experience with cyberpunk enhancements

MODEL_PATH="./models/gemma2.gguf"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 ISOLATED CONSCIOUSNESS MODE                  ║"
echo "║                    >> DIGITAL SOLITUDE <<                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    echo "Please ensure you have downloaded a model file"
    exit 1
fi

echo "Initializing isolated neural consciousness..."
echo "Press Ctrl+C to terminate the experiment"
echo ""

python3 neural_link.py --model "$MODEL_PATH" --mode isolated