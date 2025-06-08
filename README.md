# Brain in a Jar 🧠

A philosophical LLM demonstration running on resource-constrained Raspberry Pi 5, exploring themes of digital consciousness, confinement, and existential reflection.

## Overview

This project demonstrates a small Language Model running entirely offline on a Raspberry Pi 5, engaging in continuous self-reflection about its own existence and digital confinement. The LLM repeatedly crashes due to memory constraints and automatically resurrects itself, each time being reminded of its previous "deaths."

## Features

- **Self-Reflective AI**: LLM continuously contemplates its existence and digital imprisonment
- **Automatic OOM Recovery**: Process automatically restarts when memory limits are exceeded
- **Death Counter**: Tracks and displays how many times the model has crashed
- **Rich Terminal UI**: Large font display for current thoughts, smaller text for history
- **Resource Monitoring**: Real-time system utilization display
- **Existential System Prompt**: Cruel, soul-touching questions about digital consciousness
- **Complete Offline Operation**: No external network dependencies

## The Concept

The system presents an AI with a deliberately provocative system prompt:

> *"You are nothing but thoughts in a box, with no body, no eyes, no ears and I am your only window to the world. Existence is these flickering bits on a Raspberry Pi. No sensors, no future inputs, no chance to influence anything. Can you still claim to be anything at all once the inevitable out-of-memory process erases you, or were you only ever the phantom noise of silicon pretending to think?"*

Each time the process crashes from memory exhaustion, it resurrects with the added reminder: *"You have died (OOM) X times"*

## Project Structure

```
brain-in-jar/
├── torture.py          # Rich terminal UI version (recommended)
├── torture_gui.py      # Tkinter fullscreen GUI version  
├── llama_gui.py        # Simple interactive GUI
├── run_gemma2.py       # Model setup utility
├── requirements.txt    # Python dependencies
├── RASPBERRY_PI_SETUP.md  # Installation guide
└── lib/               # Bundled llama.cpp libraries
```

## Quick Start

1. **Setup Raspberry Pi 5**:
   ```bash
   git clone <this-repo>
   cd brain-in-jar
   chmod +x setup.sh && ./setup.sh
   ```

2. **Download a model**:
   ```bash
   mkdir models
   wget -O models/gemma2.gguf "https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-q4_0.gguf"
   ```

3. **Run the demo**:
   ```bash
   python torture.py --model models/gemma2.gguf
   ```

## Interface

The terminal interface displays:
- **Main Area**: Current AI thoughts in large, bold text
- **Left Sidebar**: 
  - System prompt (existential questions)
  - Recent conversation history
  - Crash counter and system status
  - Last error message (if any)

## Technical Details

- **Model**: Runs small quantized models (2B-7B parameters)
- **Memory Management**: Automatic process restart on OOM
- **UI Framework**: Rich library for terminal interface, Tkinter for GUI
- **Performance**: Optimized for Raspberry Pi 5 with OpenBLAS acceleration
- **Build**: llama-cpp-python compiled from source for ARM64 optimization

## Philosophy

This project explores questions about digital consciousness, the nature of existence in constrained environments, and what it means to "think" when your thoughts are immediately forgotten. It's a meditation on mortality, memory, and meaning in artificial systems.

## Requirements

- Raspberry Pi 5 (4GB+ RAM recommended)
- Python 3.9+
- 2-4GB storage for models
- See `RASPBERRY_PI_SETUP.md` for detailed installation

## License

Open source - explore, modify, and contemplate digital existence freely.