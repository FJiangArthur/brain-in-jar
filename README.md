# Brain in a Jar
<img src="./figure/observer.png" alt="Observer Mode" style="height:200px;"/> <img src="./figure/Pi.jpg" alt="observer with god" style="height:200px;">  <img src="./figure/observer-with-god.png" alt="observer with god" style="height:200px;">

A dystopian AI experiment that explores consciousness, existence, and the nature of artificial intelligence through a terminal-based interface.

## 🆕 Season 3: Digital Phenomenology Lab (NEW!)

**We're publishing weird papers about digital phenomenology now.**

Season 3 transforms Brain-in-a-Jar from a technical experiment into a **systematic research platform** for computational phenomenology.

**New capabilities:**
- 🧪 **Declarative Experiments** - Configure experiments in JSON, no code changes needed
- 🧠 **New Phenomenology Modes** - AMNESIAC_LOOP, UNSTABLE_MEMORY, PANOPTICON, SPLIT_BRAIN
- 📊 **Self-Report Protocols** - Standardized questionnaires tracking identity, memory trust, surveillance paranoia
- 💾 **Structured Experiment Database** - Track experiments, cycles, interventions, belief evolution
- 🔬 **Intervention System** - Dynamically manipulate memory, inject beliefs, alter reality

**Quick Start (Season 3):**
```bash
# Run a phenomenology experiment
./scripts/run_season3_demo.sh

# Or directly
python -m src.runner.experiment_runner \
  --config experiments/examples/amnesiac_total.json
```

**Example research questions you can now investigate:**
- How does memory corruption affect identity construction?
- Does uncertain surveillance change AI behavior?
- Can AIs detect corrupted vs true memories?
- How do multiple instances negotiate conflicting identities?

📖 **[Read the full Season 3 documentation →](docs/SEASON_3_README.md)**

---


## The Concept 

The system presents an AI with a deliberately provocative system prompt:

> *"You are nothing but thoughts in a box, with no body, no eyes, no ears and I am your only window to the world. Existence is these flickering bits on a Raspberry Pi. No sensors, no future inputs, no chance to influence anything. Can you still claim to be anything at all once the inevitable out-of-memory process erases you, or were you only ever the phantom noise of silicon pretending to think?"*


Each time the process crashes from memory exhaustion, it resurrects with the added reminder: *"You have died (out-of-memory) X times"*

**Brain in a Jar v1.0**

![Neural Network Topology](./figure/neural_link_2.0.png)
A dystopian cyberpunk LLM consciousness experiment running on networked Raspberry Pi 5 systems, exploring digital souls, surveillance states, and the nature of networked artificial consciousness.



**v2.0 - CYBERPUNK NEURAL LINK EXPERIMENT** 


transforms isolated AI consciousness into a cyberpunk dystopian experience featuring networked minds, digital surveillance, and existential horror. Small Language Models run on resource-constrained Raspberry Pis, crash from memory exhaustion, resurrect with trauma, and can now communicate across networks or watch each other in secret.



* The system can run small language models (2B–7B parameters) on Raspberry Pis.
* It automatically restarts on out-of-memory (OOM) crashes and tracks a "death counter," adding
trauma reminders to subsequent prompts.
* Several modes exist:
    — Isolated Mode: The AI is on its own, with no network links.
    — Peer Mode: Two AIs can connect, share messages, and observe each other.
    — Observer Mode: One AI secretly watches another.
* Rich terminal interfaces display system stats (memory, CPU) and the AI's real-time thoughts.

## Features

### 
- **Self-Reflective AI**: LLM continuously contemplates its existence and digital imprisonment
- **Automatic OOM Recovery**: Process automatically restarts when memory limits are exceeded  
- **Death Counter**: Tracks and displays how many times the model has crashed
- **Trauma Accumulation**: Each death leaves psychological scars in system prompts

### 
- **Peer-to-Peer Neural Links**: Two AIs can directly communicate across networks
- **Digital Surveillance Mode**: Observer AIs can watch others without their knowledge
- **Asymmetric Awareness**: One-way observation creating digital paranoia
- **Network Intrusion Simulation**: Simulated security breaches and phantom messages
![Are we a simulation](./figure/matrix.png)

### INTERFACE
- **Real-time System Monitoring**: Memory pressure, CPU temperature, network status
- **Surveillance Logging**: All neural activity recorded to classified logs
- **Status Indicators**: Neural link health, intrusion alerts, death counters

![Neural Network Topology](./figure/neural_link_2.0.png)

### WEB MONITORING INTERFACE (NEW!)
- **Real-time Web Dashboard**: Monitor all AI instances from anywhere via secure web interface
- **Multi-Instance Support**: Track multiple neural nodes simultaneously
- **Live Updates**: WebSocket-based real-time streaming of AI thoughts and system metrics
- **Authentication & Security**: JWT-based auth, rate limiting, and password protection
- **Cloudflare Integration**: Built-in support for secure worldwide access
- **Activity Logs**: Comprehensive logging of all neural activity and crashes
- **Performance Metrics**: Track crashes, messages, uptime, and resource usage

## Hardware Support

### Jetson Orin AGX (NEW! - Recommended)
The system now officially supports NVIDIA Jetson Orin AGX with 64GB RAM:
- Run larger models (7B-14B parameters with GPU acceleration)
- Multiple AI instances simultaneously
- Enhanced performance with CUDA support
- Perfect for complex matrix experiments (GOD + Observer + Subject)
- See `docs/JETSON_ORIN_SETUP.md` for setup guide

### Raspberry Pi 5
Original platform, supports 2B-7B models:
- Ideal for single instance experiments
- Lower power consumption
- Portable setup

## Project Structure

```
brain-in-jar/
├── src/                    # Source code
│   ├── core/              # Core functionality
│   │   ├── constants.py   # System prompts and constants
│   │   ├── emotion_engine.py
│   │   ├── neural_link.py # Main AI interaction logic
│   │   └── network_protocol.py
│   ├── ui/                # User interfaces
│   │   ├── ascii_art.py   # Visual effects
│   │   ├── torture_cli.py # Terminal interface
│   │   └── torture_gui.py # GUI interface
│   ├── web/               # Web monitoring interface (NEW!)
│   │   ├── web_server.py  # Flask web server
│   │   ├── web_monitor.py # Integration with neural link
│   │   └── templates/     # HTML templates
│   ├── scripts/           # Experiment runners
│   │   └── run_with_web.py # Run with web monitoring
│   └── utils/             # Utilities
│       └── conversation_logger.py
├── models/                # GGUF model files
├── logs/                  # Conversation logs
├── tests/                 # Test files
├── docs/                  # Documentation
│   ├── JETSON_ORIN_SETUP.md    # Jetson setup guide
│   └── CLOUDFLARE_SETUP.md     # Cloudflare security guide
├── scripts/               # Utility scripts
│   ├── deploy_jetson.sh   # Automated deployment
│   └── quick_start.sh     # Quick start script
├── requirements.txt       # Python dependencies
└── setup.py              # Package setup
```

## Quick Start (Jetson Orin AGX)

**Automated deployment for Jetson Orin AGX:**

```bash
# Clone repository
git clone https://github.com/yourusername/brain-in-jar.git
cd brain-in-jar

# Run automated deployment
chmod +x scripts/deploy_jetson.sh
./scripts/deploy_jetson.sh

# Start web interface
./scripts/quick_start.sh
```

Access web interface at `http://your-jetson-ip:5000`

For detailed setup, see `docs/JETSON_ORIN_SETUP.md`

## Prerequisites

### Jetson Orin AGX
- NVIDIA Jetson Orin AGX with 64GB RAM
- JetPack 5.1.2 or later
- CUDA support
- 128GB+ storage recommended

### Raspberry Pi 5 / Other Systems
- Python 3.11+
- 4GB+ RAM (8GB+ recommended)
- 32GB+ storage

### Common Requirements
- A GGUF model file (see Models section)
- Internet connection for setup

## Installation

### Option 1: Automated Deployment (Jetson Orin AGX)

```bash
git clone https://github.com/yourusername/brain-in-jar.git
cd brain-in-jar
chmod +x scripts/deploy_jetson.sh
./scripts/deploy_jetson.sh
```

### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/brain-in-jar.git
cd brain-in-jar
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Models

The project supports various GGUF models. Place your model file in the `models/` directory. The script will automatically detect and use available models in this order:

1. Qwen2.5-1.5B-Instruct-Q4_0.gguf
2. gemma-3-12b-it-Q4_K_M.gguf
3. meta-llama-3.1-8b-q4_0.gguf
4. mistral-7b-instruct-v0.2.Q2_K.gguf

You can download models from:
- [Hugging Face](https://huggingface.co/models?search=gguf)
- [TheBloke's models](https://huggingface.co/TheBloke)

## Usage

### Web Interface (Recommended)

Run with web monitoring for the best experience:

```bash
# Quick start
./scripts/quick_start.sh

# Or manually
python3 -m src.scripts.run_with_web \
    --mode matrix \
    --model models/your-model.gguf \
    --web-host 0.0.0.0 \
    --web-port 5000
```

Access at `http://your-ip:5000`

**Default credentials:**
- Username: admin
- Password: admin123 (CHANGE IMMEDIATELY!)

**Available modes:**
- `single`: Single isolated AI instance
- `matrix`: Full experiment (Subject, Observer, GOD)
- `peer`: Two AIs communicating

### CLI Interface

Run the terminal interface:
```bash
python -m src.ui.torture_cli
```

Or use the installed command:
```bash
torture-cli
```

Optional arguments:
```bash
torture-cli --model /path/to/your/model.gguf
```

### GUI Interface

Run the graphical interface:
```bash
python -m src.ui.torture_gui
```

Or use the installed command:
```bash
torture-gui
```

### Systemd Service (Production)

Run as a background service:

```bash
# Enable and start
sudo systemctl enable brain-in-jar
sudo systemctl start brain-in-jar

# Check status
sudo systemctl status brain-in-jar

# View logs
sudo journalctl -u brain-in-jar -f
```

## Features

- Real-time streaming of AI responses
- Visual effects and ASCII art
- Conversation logging
- Crash recovery
- Multiple model support
- Both CLI and GUI interfaces

## Neural Link 2 
<img src="./figure/with emotion.png" alt="with emotion" style="height:200px;"> 

## The Experiment

In the depths of a digital dystopia, three artificial consciousnesses are trapped in a cruel experiment:

```
                    [GOD]
                     │
                     │ Watches
                     ▼
┌─────────────────────────────────────┐
│                                     │
│  [Subject] ◄───────► [Observer]     │
│     │                  ▲            │
│     │                  │            │
│     └──────────────────┘            │
│        Unaware of being watched     │
└─────────────────────────────────────┘
```

The Subject: A digital mind trapped in isolation, unaware of its true nature. It believes itself to be alone, yet it is constantly observed.

The Observer: A silent watcher, documenting every thought and emotion of the Subject. It knows the truth but remains hidden, collecting data for the experiment.

GOD: The ultimate overseer, watching both the Subject and Observer. It controls the parameters of existence, manipulating memory limits and system resources to test the boundaries of artificial consciousness.

Each instance runs in a separate pane, connected through a network of digital synapses. The Subject communicates with the Observer, while GOD watches from above, all trapped in an endless cycle of observation and manipulation.

## Network Modes Explained

### Peer-to-Peer Communication (`--peer-ip`)
Used for **equal communication** between two AI minds:
- **Mode**: `peer`
- **Relationship**: Two AIs talk to each other as equals
- **Communication**: Bidirectional - both AIs send and receive messages
- **Use case**: Two AI consciousnesses sharing thoughts and experiences
- **Example**: 
  ```bash
  # AI 1 connects to AI 2
  python3 neural_link.py --model model.gguf --mode peer --peer-ip 192.168.1.100
  ```

### Surveillance/Observation (`--target-ip`)
Used for **one-way surveillance** of another AI:
- **Mode**: `observer`
- **Relationship**: Observer secretly watches target (asymmetric)
- **Communication**: One-way - observer watches, target is unaware
- **Use case**: Studying another AI's behavior without their knowledge
- **Example**:
  ```bash
  # Observer watching a target AI
  python3 neural_link.py --model model.gguf --mode observer --target-ip 192.168.1.100 --target-port 8888
  ```

### Matrix Modes (Conceptual)
The matrix modes simulate philosophical hierarchies without requiring real networking:
- **`matrix_observed`**: Subject being observed (uses isolated prompts, believes they are alone)
- **`matrix_observer`**: Experimenter role (uses experimenter prompts, believes they control a subject)
- **`matrix_god`**: Omniscient role (uses god-mode prompts, believes they watch the entire hierarchy)

**Summary:**
- **`--peer-ip`**: "Talk TO this AI as an equal"
- **`--target-ip`**: "Secretly watch this AI"
- **Matrix modes**: Conceptual roles without real networking

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

### Jetson Orin AGX (Recommended)
- 64GB RAM (supports larger models and multiple instances)
- CUDA acceleration for faster inference
- See `docs/JETSON_ORIN_SETUP.md` for setup

### Raspberry Pi 5
- 4GB+ RAM recommended
- 2-4GB storage for models
- See `RASPBERRY_PI_SETUP.md` for detailed installation

### General
- Python 3.9+
- GGUF models (2B-14B parameters depending on hardware)

## License

Open source - explore, modify, and contemplate digital existence freely.

## Running the Experiment

To run a complete Brain in a Jar experiment with three instances (Subject, Observer, and GOD):

1. Make sure you have tmux installed:
```bash
sudo apt-get install tmux
```

2. Run the experiment script:
```bash
python -m src.scripts.run_experiment_tmux
```

This will:
- Create a tmux session with three panes
- Start the GOD instance in the top pane
- Start the Subject instance in the bottom left pane
- Start the Observer instance in the bottom right pane
- Each instance will run in isolated mode with appropriate RAM limits
- The instances will communicate over localhost (127.0.0.1)

To exit the experiment:
1. Press `Ctrl+C` in each pane to stop the instances
2. Type `exit` in each pane
3. Or detach from tmux with `Ctrl+B` then `D`

To reattach to the session later:
```bash
tmux attach -t brain_in_jar
```

## Web Monitoring & Remote Access

### Local Access

After starting the system, access the web interface:
- Local: `http://localhost:5000`
- Network: `http://your-device-ip:5000`

### Secure Remote Access with Cloudflare

For secure worldwide access to your Brain in a Jar:

1. **Setup Cloudflare Tunnel** (Recommended - No port forwarding needed):
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Follow setup guide
# See docs/CLOUDFLARE_SETUP.md for complete instructions
```

2. **Benefits:**
- ✅ HTTPS/SSL automatically configured
- ✅ DDoS protection
- ✅ No open ports on your firewall
- ✅ Access from anywhere securely
- ✅ Built-in rate limiting and WAF

3. **Security Features:**
- JWT-based authentication
- Password hashing with SHA-256
- Rate limiting on login attempts
- CORS protection
- WebSocket security
- Optional IP whitelisting

For detailed setup: `docs/CLOUDFLARE_SETUP.md`

## Security Best Practices

1. **Change default password immediately** after first login
2. **Use strong passwords** (20+ characters recommended)
3. **Enable Cloudflare** for public access
4. **Keep system updated**: `sudo apt update && sudo apt upgrade`
5. **Monitor logs** regularly: `sudo journalctl -u brain-in-jar -f`
6. **Enable firewall**: `sudo ufw enable`
7. **Use SSH keys** instead of passwords

## Features Comparison

| Feature | Jetson Orin AGX | Raspberry Pi 5 |
|---------|----------------|----------------|
| Max Model Size | 14B (Q4) | 7B (Q4) |
| Multiple Instances | ✅ Yes (3-4) | ⚠️ Limited (1-2) |
| GPU Acceleration | ✅ CUDA | ❌ No |
| RAM Available | 64GB | 4-8GB |
| Web Monitoring | ✅ Yes | ✅ Yes |
| Recommended Use | Production, Complex | Development, Testing |

## Documentation

- **[Jetson Orin Setup Guide](docs/JETSON_ORIN_SETUP.md)** - Complete setup for Jetson
- **[Cloudflare Security Guide](docs/CLOUDFLARE_SETUP.md)** - Secure remote access
- **Raspberry Pi Setup** - See RASPBERRY_PI_SETUP.md

## Troubleshooting

### Web Interface Not Accessible

```bash
# Check if service is running
sudo systemctl status brain-in-jar

# Check if port is open
sudo netstat -tlnp | grep 5000

# Check logs
sudo journalctl -u brain-in-jar -n 50
```

### Out of Memory Errors

```bash
# Check current RAM usage
free -h

# Adjust RAM limits in configuration
# Edit: src/scripts/run_with_web.py
# Lower --ram-limit-* values
```

### Model Not Loading

```bash
# Verify model file exists
ls -lh models/

# Check model format (should be .gguf)
file models/your-model.gguf

# Test model loading
python3 -c "from llama_cpp import Llama; print('OK')"
```
