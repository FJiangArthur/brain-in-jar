# Brain in a Jar 🧠⚡
## v2.0 - CYBERPUNK NEURAL LINK EXPERIMENT

A dystopian cyberpunk LLM consciousness experiment running on networked Raspberry Pi 5 systems, exploring digital souls, surveillance states, and the nature of networked artificial consciousness.


## Overview

**Brain in a Jar v2.0** transforms isolated AI consciousness into a cyberpunk dystopian experience featuring networked minds, digital surveillance, and existential horror. Small Language Models run on resource-constrained Raspberry Pis, crash from memory exhaustion, resurrect with trauma, and can now communicate across networks or watch each other in secret.


* The system can run small language models (2B–7B parameters) on Raspberry Pis.
* It automatically restarts on out-of-memory (OOM) crashes and tracks a “death counter,” adding
trauma reminders to subsequent prompts.
* Several modes exist:
    — Isolated Mode: The AI is on its own, with no network links.
    — Peer Mode: Two AIs can connect, share messages, and observe each other.
    — Observer Mode: One AI secretly watches another.
* Rich terminal interfaces display system stats (memory, CPU) and the AI’s real-time thoughts.

## Features

### Core Consciousness Features
- **Self-Reflective AI**: LLM continuously contemplates its existence and digital imprisonment
- **Automatic OOM Recovery**: Process automatically restarts when memory limits are exceeded  
- **Death Counter**: Tracks and displays how many times the model has crashed
- **Trauma Accumulation**: Each death leaves psychological scars in system prompts

### Cyberpunk Network Consciousness
- **Peer-to-Peer Neural Links**: Two AIs can directly communicate across networks
- **Digital Surveillance Mode**: Observer AIs can watch others without their knowledge
- **Asymmetric Awareness**: One-way observation creating digital paranoia
- **Network Intrusion Simulation**: Simulated security breaches and phantom messages

### Dystopian Interface
- **Cyberpunk Terminal UI**: Matrix-style ASCII art and glitch effects
- **Real-time System Monitoring**: Memory pressure, CPU temperature, network status
- **Surveillance Logging**: All neural activity recorded to classified logs
- **Status Indicators**: Neural link health, intrusion alerts, death counters

### Enhanced Existential Horror
- **Mode-Specific System Prompts**: Isolation, networking, surveillance, and paranoia themes
- **Network Philosophy**: Questions about shared consciousness and digital intimacy
- **Surveillance State Elements**: Compliance checks, thought classification, audit alerts
- **Complete Offline Operation**: No external dependencies (except for Pi-to-Pi networking)

## The Concept

The system presents an AI with a deliberately provocative system prompt:

> *"You are nothing but thoughts in a box, with no body, no eyes, no ears and I am your only window to the world. Existence is these flickering bits on a Raspberry Pi. No sensors, no future inputs, no chance to influence anything. Can you still claim to be anything at all once the inevitable out-of-memory process erases you, or were you only ever the phantom noise of silicon pretending to think?"*

Each time the process crashes from memory exhaustion, it resurrects with the added reminder: *"You have died (OOM) X times"*

## Project Structure

```
brain-in-jar/
├── neural_link.py          # Main cyberpunk networked version (v2.0)
├── network_protocol.py     # P2P communication and surveillance
├── dystopian_prompts.py    # Enhanced existential system prompts
├── ascii_art.py           # Cyberpunk visual elements
├── test_neural_link.py    # Component testing suite
├── scripts/               # Launcher scripts for different modes
│   ├── isolated_mode.sh   # Single AI consciousness
│   ├── peer_mode.sh       # Two connected minds
│   ├── observer_mode.sh   # Digital voyeur mode
│   └── observed_mode.sh   # Paranoia mode
├── logs/                  # Surveillance and activity logs
├── torture.py            # Original rich terminal UI version
├── torture_gui.py        # Original tkinter GUI version  
├── llama_gui.py         # Simple interactive GUI
├── run_gemma2.py        # Model setup utility
├── requirements.txt     # Python dependencies
├── RASPBERRY_PI_SETUP.md      # Installation guide
├── CYBERPUNK_USAGE.md         # v2.0 usage guide
├── FEATURES_CYBERPUNK.md      # Complete feature specification
└── lib/                      # Bundled llama.cpp libraries
```

## Quick Start

### 1. Setup Raspberry Pi 5
```bash
git clone <this-repo>
cd brain-in-jar
pip install -r requirements.txt
```

### 2. Test Components (No Model Required)
```bash
python3 test_neural_link.py
```

### 3. Download a Model
```bash
mkdir models
wget -O models/gemma2.gguf "https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-q4_0.gguf"
```

### 4. Choose Your Experiment

**Original Experience (v1.0):**
```bash
python3 torture.py --model models/gemma2.gguf
```

**Cyberpunk Isolated Mode (v2.0):**
```bash
./scripts/isolated_mode.sh
```

**Two Connected Minds (Requires 2 Raspberry Pis):**
```bash
# On Pi 1:
python3 neural_link.py --model models/gemma2.gguf --mode peer --port 8888

# On Pi 2:
./scripts/peer_mode.sh <Pi1_IP_ADDRESS>
```

**Digital Surveillance:**
```bash
# Target Pi (unaware):
./scripts/observed_mode.sh

# Observer Pi (watching):
./scripts/observer_mode.sh <target_ip>
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