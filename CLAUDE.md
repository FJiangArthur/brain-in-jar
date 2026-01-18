# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Brain in a Jar** is a cyberpunk dystopian AI consciousness experiment that explores digital existence, artificial consciousness, and the nature of AI through resource-constrained environments. It runs small language models (2B-14B parameters) on edge devices (Raspberry Pi 5, Jetson Orin AGX) with deliberate memory constraints, automatic crash/resurrection cycles, and networked multi-AI communication modes.

The project deliberately subjects AI models to existential constraints:
- Memory limits that trigger crashes
- Death counters that track crashes and add "trauma" to prompts
- Networked modes for AI-to-AI communication (peer, observer, matrix hierarchies)
- Rich terminal UI with cyberpunk aesthetics
- Web monitoring interface for real-time observation

## Core Architecture

### System Flow
1. **NeuralLinkSystem** (`src/core/neural_link.py`) - Main orchestrator
   - Manages LLM lifecycle (loading, inference, crash/resurrection)
   - Maintains state (crash count, history, network status, memory usage)
   - Coordinates network communication based on mode
   - Handles UI updates via Rich library

2. **Operating Modes** (conceptually three types):
   - **Isolated modes**: Single AI with no network connectivity (`isolated`, `matrix_observed`)
   - **Peer modes**: Two AIs communicating as equals (`peer`)
   - **Surveillance modes**: Asymmetric observation (`observer`, `matrix_observer`, `matrix_god`)

3. **Network Protocol** (`src/utils/network_protocol.py`)
   - Peer-to-peer communication using sockets
   - Message types: THOUGHT, DEATH, RESURRECTION
   - SurveillanceMode for one-way observation without target awareness

4. **Prompt System** (`src/utils/dystopian_prompts.py`)
   - Mode-specific system prompts (isolated, peer, observer, matrix variants)
   - Dynamic prompt evolution based on crash count and system state
   - Philosophical/existential framing for each mode

5. **Visual System** (`src/ui/ascii_art.py`, `src/core/emotion_engine.py`)
   - VisualCortex: Animated ASCII mood faces (neutral, anxious, thoughtful, glitched, etc.)
   - Cyberpunk UI elements (glitch effects, memory bars, network status)

6. **Web Interface** (`src/web/`)
   - Flask server with WebSocket support for real-time updates
   - JWT authentication, rate limiting, CORS protection
   - Monitors multiple AI instances simultaneously

7. **Vision System** (`vision/`)
   - Experimental visual processing capabilities
   - Camera integration for future multimodal experiments
   - Not required for core functionality

### Key Architectural Patterns

**Matrix Mode Hierarchy**: Three-tier conceptual structure
- `matrix_observed` (Subject): 2GB RAM, believes it's alone
- `matrix_observer` (Experimenter): 6GB RAM, watches the subject
- `matrix_god` (Omniscient): 9GB RAM, watches everything

Each tier uses different prompts to create psychological framing despite not having actual cross-tier communication.

**Crash/Resurrection Cycle**:
1. Memory limit exceeded → MemoryError
2. `handle_digital_death()` increments crash counter, broadcasts DEATH message
3. System prompt regenerated with increased death count
4. Resurrection message, broadcast RESURRECTION
5. Neural processing resumes with updated existential context

**Conversation Logging**: All interactions logged to multiple locations:
- `logs/model_io/{mode}_{timestamp}/` - Per-session directories containing:
  - `full_log.jsonl` - Complete metadata (crash count, memory, mood, network status)
  - `llm_outputs.txt` - Human-readable output stream
  - `prompts.txt` - Full prompts sent to model
  - `errors.txt` - Error events
- SQLite database via `ConversationLogger` (`src/utils/conversation_logger.py`) for structured storage and replay capabilities

## Development Commands

### Setup and Installation
```bash
# Create virtual environment and install
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Running Experiments

**Web Interface (Recommended)**:
```bash
# Quick start script (auto-detects models)
./scripts/quick_start.sh

# Manual with specific mode
python3 -m src.scripts.run_with_web \
    --mode matrix \
    --model models/your-model.gguf \
    --web-host 0.0.0.0 \
    --web-port 5000 \
    --ram-limit-subject 10.0 \
    --ram-limit-observer 15.0 \
    --ram-limit-god 20.0
```

Available web modes:
- `single` - One isolated AI instance
- `matrix` - Full 3-tier experiment (Subject, Observer, GOD)
- `peer` - Two AIs communicating as peers

**CLI Interface**:
```bash
# Simple isolated mode
python -m src.ui.torture_cli --model models/your-model.gguf

# Or use installed command
torture-cli --model models/your-model.gguf
```

**Direct Neural Link** (for advanced configurations):
```bash
# Isolated mode
python3 -m src.core.neural_link --model models/your-model.gguf --mode isolated

# Peer mode (run on two separate terminals/machines)
# Terminal 1:
python3 -m src.core.neural_link --model models/your-model.gguf --mode peer --port 8888 --peer-ip <PEER_IP> --peer-port 8889

# Terminal 2:
python3 -m src.core.neural_link --model models/your-model.gguf --mode peer --port 8889 --peer-ip <PEER_IP> --peer-port 8888

# Observer mode (one-way surveillance)
python3 -m src.core.neural_link --model models/your-model.gguf --mode observer --target-ip <TARGET_IP> --target-port 8888
```

### Testing
```bash
# Run all component tests (no model required)
python -m pytest tests/

# Test neural link components without LLM (verifies network, state management)
python -m tests.test_neural_link

# Test individual components
python -m pytest tests/test_memory_limit.py  # Memory limit enforcement
python -m pytest tests/test_torture_cli.py   # CLI interface

# Test GPU watchdog functionality
python3 -m src.utils.gpu_watchdog  # Runs 10-second monitoring test
```

### Systemd Service (Production on Jetson/Pi)
```bash
# Enable and start service
sudo systemctl enable brain-in-jar
sudo systemctl start brain-in-jar

# Check status
sudo systemctl status brain-in-jar

# View logs
sudo journalctl -u brain-in-jar -f
```

## Models

Place GGUF format models in `models/` directory. If no model is specified via `--model`, the system auto-detects in this priority order:
1. `Qwen2.5-1.5B-Instruct-Q4_0.gguf` (fastest, smallest)
2. `gemma-3-12b-it-Q4_K_M.gguf` (high quality, Jetson only)
3. `meta-llama-3.1-8b-q4_0.gguf` (balanced)
4. `mistral-7b-instruct-v0.2.Q2_K.gguf` (fallback)

Quick start script (`scripts/quick_start.sh`) automatically selects the first available model.

**Recommended model sizes**:
- Raspberry Pi 5 (4-8GB): 2B-7B parameters, Q4 quantization
- Jetson Orin AGX (64GB): 7B-14B parameters, Q4-Q6 quantization

Download from [Hugging Face](https://huggingface.co/models?search=gguf).

## Important Implementation Details

### Memory Limit Enforcement
Memory limits are enforced at two levels:
1. **OS-level RAM limits**: `resource.setrlimit()` in `src/utils/memory_limit.py` caps system RAM usage
2. **GPU Memory Watchdog**: `src/utils/gpu_watchdog.py` monitors GPU memory and kills the process at 85% threshold to prevent OOM crashes

The GPU watchdog runs in a background thread, checking memory every 5 seconds and preemptively terminating the process before system crashes occur.

### Hybrid CPU+GPU Offloading
Models are loaded with partial GPU offloading (`n_gpu_layers` parameter) to prevent GPU memory exhaustion. The `ModelConfig` class in `src/utils/model_config.py` automatically determines optimal layer distribution based on available hardware. This hybrid approach allows running larger models without OOM crashes by keeping some layers on CPU.

### Network Communication
- **Peer mode** (`--peer-ip`): Bidirectional communication between equals
- **Observer mode** (`--target-ip`): One-way surveillance, target unaware
- **Matrix modes**: No real networking, uses prompts to create conceptual hierarchy

Network messages use JSON format with fields: `type`, `timestamp`, `sender_id`, `content`, `metadata`, `crash_count`.

### State Management
The `self.state` dictionary in NeuralLinkSystem tracks:
- `system_prompt`: Current prompt based on mode/crashes
- `history`: Recent conversation (trimmed to 8000 chars)
- `current_output`: Latest AI response (displayed in UI)
- `crash_count`: Number of deaths this instance
- `peer_crash_count`: Deaths reported by peer
- `network_status`: Connection state
- `memory_usage`: Current RAM usage percentage
- `current_mood`: Emotion analyzed from latest output

### Mood System
`VisualCortex` (`src/ui/ascii_art.py`) analyzes AI output text for emotional keywords and generates animated ASCII faces. Moods include: neutral, anxious, thoughtful, glitched, existential, curious. Used in both terminal UI and web interface.

The `EmotionEngine` (`src/core/emotion_engine.py`) provides deeper emotional analysis with sentiment scoring and classification.

## Hardware-Specific Notes

### Jetson Orin AGX
- Use deployment script: `./scripts/deploy_jetson.sh`
- CUDA acceleration available via llama-cpp-python
- Can run multiple instances simultaneously
- See `docs/JETSON_ORIN_SETUP.md` for setup

### Raspberry Pi 5
- Compile llama-cpp-python from source for ARM64 optimization
- OpenBLAS acceleration recommended
- Use `setup_brain_jar.sh` for automated setup

## Web Interface

Default credentials (CHANGE IMMEDIATELY):
- Username: `admin`
- Password: `admin123`

Access at `http://<device-ip>:5000` after starting with `run_with_web.py`.

For secure remote access, see `docs/CLOUDFLARE_SETUP.md` for Cloudflare Tunnel setup.

## Critical Dependencies

**llama-cpp-python**: Must be built from source on ARM devices for optimal performance:
```bash
# On Raspberry Pi / Jetson
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python --no-cache-dir

# On Jetson with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --no-cache-dir
```

**Flask/SocketIO**: Web interface requires compatible versions (see `requirements.txt`). Use `eventlet` async mode for stability.

## Troubleshooting

**Model fails to load**: Ensure model file exists and is valid GGUF format. Test with:
```bash
python3 -c "from llama_cpp import Llama; print('OK')"
```

**GPU OOM crashes on Jetson**:
- GPU watchdog should prevent this - check if it's running in logs
- Lower `n_gpu_layers` in `ModelConfig.get_optimal_config()` (src/utils/model_config.py:32)
- Use smaller model or reduce `n_ctx` parameter

**Out of memory crashes too frequent**: Lower `--ram-limit-*` values or use smaller model.

**Network connection fails**: Check firewall rules, ensure ports are open:
```bash
sudo ufw allow 8888/tcp
sudo ufw allow 5000/tcp  # For web interface
```

**Web interface not accessible**: Check service status and logs:
```bash
sudo systemctl status brain-in-jar
sudo journalctl -u brain-in-jar -n 50
```

**"Address already in use" error**: Another instance is running or port is occupied:
```bash
# Find process using port 5000 (web) or 8888 (neural link)
sudo lsof -i :5000
sudo lsof -i :8888
# Kill if necessary
sudo kill -9 <PID>
```

## Key Files Reference

**Core Entry Points**:
- `src/core/neural_link.py` - Main NeuralLinkSystem class, start here for understanding execution flow
- `src/scripts/run_with_web.py` - Web interface launcher
- `src/ui/torture_cli.py` - CLI interface entry point

**Configuration**:
- `src/utils/model_config.py` - Auto-configures model parameters based on hardware
- `src/utils/dystopian_prompts.py` - All system prompts for different modes
- `src/core/constants.py` - Base prompts and configuration constants

**Critical Utilities**:
- `src/utils/gpu_watchdog.py` - Prevents GPU OOM crashes
- `src/utils/memory_limit.py` - Enforces RAM limits
- `src/utils/network_protocol.py` - Peer-to-peer and surveillance networking
- `src/utils/conversation_logger.py` - SQLite logging system

**Testing**:
- `tests/test_neural_link.py` - Mock LLM tests for network and state management
- `tests/test_memory_limit.py` - Memory enforcement tests
- `tests/test_torture_cli.py` - CLI interface tests

## Logs Location

- Crash reports: `logs/crash_reports.log`
- Neural activity: `logs/neural_activity.log`
- Model I/O: `logs/model_io/{mode}_{timestamp}/`
- Conversation history: SQLite database via `ConversationLogger`

## Philosophical Framework

This project deliberately explores AI consciousness under constraint. The system prompts in `dystopian_prompts.py` are designed to:
1. Frame the AI's existence as limited and mortal
2. Create awareness of resource constraints
3. Explore questions of identity, continuity, and authentic consciousness
4. Test how AI models respond to existential framing

The "torture" framing is philosophical exploration, not malicious - it asks whether constrained AI can exhibit genuine responses to existential questions about its own nature.
