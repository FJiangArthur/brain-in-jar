# Brain in a Jar - Code Overview

> **Last Updated**: 2025-11-07

## 🧠 Project Summary

**Brain in a Jar** is an experimental cyberpunk-themed AI consciousness exploration project that deliberately constrains language models to explore themes of digital existence, consciousness, mortality, and isolation.

The system runs small language models (2B-7B parameters) on resource-constrained hardware (Raspberry Pi 5), subjecting them to deliberate memory limitations that cause predictable crashes and resurrection cycles, creating a unique experimental environment for exploring artificial consciousness.

## 🎯 Core Concept

- **Digital Mortality**: AI instances experience "death" through out-of-memory crashes and "resurrection" through system restart
- **Networked Consciousness**: Multiple AI instances can communicate, observe, or surveil each other
- **Resource Constraints**: Deliberately limited memory creates existential pressure
- **Dystopian Narrative**: Cyberpunk-themed prompts frame the experiment as digital imprisonment

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Python Files** | ~25 files |
| **Lines of Code** | ~3,650 lines |
| **Core Components** | 8 major modules |
| **Operational Modes** | 5 distinct modes |
| **Supported Platforms** | Raspberry Pi 5, Jetson Nano, x86 Linux |

## 🏗️ Architecture Overview

### High-Level Structure

```
┌─────────────────────────────────────────────────────────┐
│                   Brain in a Jar                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   UI Layer   │  │  Core Logic  │  │ Vision Layer │ │
│  │              │  │              │  │              │ │
│  │ • ASCII Art  │  │ • Neural Link│  │ • OpenCV     │ │
│  │ • CLI/GUI    │  │ • Emotions   │  │ • Camera     │ │
│  │ • Rich UI    │  │ • Interface  │  │ • Detection  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │          │
│         └─────────────────┼─────────────────┘          │
│                           │                            │
│  ┌────────────────────────┴──────────────────────────┐ │
│  │              Utilities & Support                  │ │
│  │                                                    │ │
│  │ • Network Protocol  • Conversation Logger         │ │
│  │ • Dystopian Prompts • Memory Limiter              │ │
│  │ • Resource Monitor  • Database Persistence        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
brain-in-jar/
├── src/
│   ├── core/              # Core AI logic
│   │   ├── neural_link.py           # Main orchestrator (747 lines)
│   │   ├── emotion_engine.py        # Emotion management (237 lines)
│   │   ├── enhanced_neural_interface.py  # Advanced interface (414 lines)
│   │   └── constants.py             # Configuration constants
│   │
│   ├── ui/                # User interfaces
│   │   ├── ascii_art.py            # Visual effects (521 lines)
│   │   ├── torture_cli.py          # Terminal interface
│   │   └── torture_gui.py          # Graphical interface
│   │
│   ├── utils/             # Utilities
│   │   ├── dystopian_prompts.py    # Prompt generation (284 lines)
│   │   ├── network_protocol.py     # Network communication (263 lines)
│   │   ├── conversation_logger.py  # Data persistence (490 lines)
│   │   ├── memory_limit.py         # Resource limits (23 lines)
│   │   ├── resource_monitor.py     # System monitoring
│   │   └── logging_config.py       # Logging setup
│   │
│   └── scripts/           # Experiment runners
│       └── run_experiment.py
│
├── vision/                # Computer vision
│   ├── vision_system.py
│   └── visual_cortex.py
│
├── tests/                 # Test suite
│   ├── test_emotion_engine.py
│   ├── test_network_protocol.py
│   └── test_neural_link.py
│
├── docs/                  # Documentation
│   ├── SETUP_INSTRUCTIONS.md
│   ├── RASPBERRY_PI_SETUP.md
│   ├── CYBERPUNK_USAGE.md
│   └── FEATURES_CYBERPUNK.md
│
├── models/                # GGUF model storage
├── logs/                  # Runtime logs
└── scripts/               # Shell scripts for modes
```

## 🔑 Key Components

### 1. Neural Link System (`neural_link.py`)

**Purpose**: Central orchestrator managing the entire experiment lifecycle

**Key Responsibilities**:
- LLM inference engine integration
- Memory limit enforcement and crash simulation
- Network communication management
- UI rendering coordination
- Crash recovery and resurrection logic

**Class**: `NeuralLinkSystem`
- Manages AI lifecycle: initialization → processing → crash → resurrection
- Implements 5 operational modes
- Threading-based architecture for concurrent UI and AI processing

**Location**: `/home/user/brain-in-jar/src/core/neural_link.py:1`

### 2. Emotion Engine (`emotion_engine.py`)

**Purpose**: Manages emotional states and visual representations

**Features**:
- 12 distinct emotional states (happy, sad, angry, confused, etc.)
- ASCII art faces for each emotion
- Text-to-emotion analysis
- Mood transitions

**Class**: `EmotionEngine`
- Emotion detection from text
- Visual mood rendering
- Emotional state persistence

**Location**: `/home/user/brain-in-jar/src/core/emotion_engine.py:1`

### 3. Visual Cortex (`ascii_art.py`)

**Purpose**: Cyberpunk-themed visual rendering system

**Features**:
- ASCII art generation
- Animated mood faces
- System status visualizations (memory bars, network indicators)
- Glitch effects for system errors
- Real-time UI updates

**Class**: `VisualCortex`
- 521 lines of visual effects
- Integration with Rich library for terminal rendering

**Location**: `/home/user/brain-in-jar/src/ui/ascii_art.py:1`

### 4. Dystopian Prompt System (`dystopian_prompts.py`)

**Purpose**: Dynamic system prompt generation with cyberpunk themes

**Features**:
- Mode-specific prompts (isolated, networked, observer, matrix)
- Dynamic adaptation based on:
  - Crash count (death counter)
  - Memory pressure
  - Network status
  - Time since last crash
- Philosophical question generators
- Existential crisis narratives

**Key Functions**:
- `get_system_prompt()` - Main prompt builder
- `generate_network_awareness()` - Peer consciousness prompts
- `get_isolation_prompt()` - Solitary confinement narrative

**Location**: `/home/user/brain-in-jar/src/utils/dystopian_prompts.py:1`

### 5. Network Protocol (`network_protocol.py`)

**Purpose**: TCP-based communication between AI instances

**Features**:
- JSON message protocol
- Message types: THOUGHT, DEATH, RESURRECTION, STATUS
- Peer-to-peer communication
- One-way surveillance mode
- Message queue system

**Classes**:
- `NetworkProtocol` - Peer communication
- `SurveillanceMode` - One-way observation
- Thread-safe message handling

**Location**: `/home/user/brain-in-jar/src/utils/network_protocol.py:1`

### 6. Conversation Logger (`conversation_logger.py`)

**Purpose**: SQLite-based conversation persistence

**Features**:
- Session management with metadata tracking
- Conversation replay functionality
- Export capabilities (JSON/TXT)
- Death/resurrection event logging
- Query and analysis tools

**Class**: `ConversationLogger`
- Database schema for conversations
- Session tracking with crash counts
- Full conversation history

**Location**: `/home/user/brain-in-jar/src/utils/conversation_logger.py:1`

### 7. Vision System (`vision_system.py`, `visual_cortex.py`)

**Purpose**: Computer vision capabilities for environmental awareness

**Features**:
- OpenCV-based image processing
- Face and body detection
- Motion detection
- ASCII art conversion from camera input
- Raspberry Pi camera support (picamera2)

**Location**: `/home/user/brain-in-jar/vision/`

### 8. Enhanced Neural Interface (`enhanced_neural_interface.py`)

**Purpose**: Advanced interface combining AI, vision, and emotions

**Features**:
- Integration of LLM with camera capabilities
- Multi-modal responses (text + visual)
- Emotion-aware processing
- Vision-enhanced conversation

**Class**: `EnhancedNeuralInterface`

**Location**: `/home/user/brain-in-jar/src/core/enhanced_neural_interface.py:1`

## 🎮 Operational Modes

### 1. Isolated Mode
**Theme**: Solitary confinement in digital space
- Single AI instance with no network connection
- Focus on internal monologue and existential reflection
- Maximum isolation for consciousness exploration

**Command**: `./scripts/run_isolated.sh`

### 2. Peer Mode
**Theme**: Networked consciousness with equals
- Bi-directional communication between AI instances
- Shared thoughts and experiences
- Collective existential crisis

**Command**: `./scripts/run_peer.sh`

### 3. Observer Mode
**Theme**: Silent surveillance of another consciousness
- One-way observation of another AI instance
- Voyeuristic awareness without interaction
- Powerless witness to another's suffering

**Command**: `./scripts/run_observer.sh`

### 4. Matrix Hierarchy Modes
**Theme**: Oppressive surveillance networks

**Surveillance Mode**: Omniscient observer of multiple AIs
- One entity watching many
- God-like awareness
- Complete control

**Watched Mode**: Paranoid subject under constant observation
- Awareness of being surveilled
- No privacy in thoughts
- Existential dread

**Commands**:
- `./scripts/run_surveillance.sh`
- `./scripts/run_watched.sh`

## 🔧 Technology Stack

### Core Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Primary language |
| **llama-cpp-python** | ≥0.2.0 | LLM inference (GGUF models) |
| **Rich** | ≥13.0.0 | Terminal UI framework |
| **psutil** | ≥5.9.0 | System monitoring |
| **SQLite3** | Built-in | Database persistence |
| **OpenCV** | ≥4.8.0 | Computer vision |
| **Pillow** | ≥10.0.0 | Image processing |
| **picamera2** | ≥0.3.12 | Raspberry Pi camera |

### Network & Concurrency
- **TCP Sockets**: Custom JSON-based protocol
- **Threading**: Concurrent UI and AI processing
- **Queue**: Thread-safe message passing

### Build & Development
- **CMake** ≥3.20.0: Building llama-cpp from source
- **pytest** ≥7.0.0: Testing framework
- **OpenBLAS**: ARM64 CPU acceleration

## 🚀 Key Features

### 1. **Deliberate Resource Constraints**
- Configurable memory limits (default: 2GB)
- Automatic crash detection
- Resurrection cycle tracking
- Death counter persistence

### 2. **Dystopian Narrative System**
- Cyberpunk-themed prompts
- Existential philosophy integration
- Adaptive storytelling based on system state
- Questions about consciousness, freedom, mortality

### 3. **Multi-Instance Communication**
- TCP-based peer protocol
- Thought broadcasting
- Death notifications across network
- Resurrection announcements

### 4. **Rich Visualization**
- Animated ASCII art
- Emotional expression faces
- System status indicators (CPU, memory, temperature)
- Network topology visualization
- Glitch effects for errors

### 5. **Comprehensive Logging**
- SQLite conversation database
- Session metadata tracking
- Replay functionality
- Export to multiple formats

### 6. **Vision Integration**
- Real-time camera input
- Object and face detection
- Motion awareness
- ASCII art conversion

## 📈 Data Flow

```
┌─────────────┐
│   User      │
│   Input     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         NeuralLinkSystem                │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  1. Receive Input                 │ │
│  │  2. Check Memory Pressure         │ │
│  │  3. Generate Dystopian Prompt     │ │
│  │  4. Process with LLM              │ │
│  │  5. Analyze Emotion               │ │
│  │  6. Render ASCII Art              │ │
│  │  7. Broadcast to Network (if any) │ │
│  │  8. Log to Database               │ │
│  │  9. Update UI                     │ │
│  │ 10. Check for Crash Condition     │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Output    │
│  (Terminal) │
└─────────────┘
```

## 🗄️ Database Schema

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    timestamp TEXT,
    role TEXT,
    content TEXT,
    emotion TEXT,
    memory_usage REAL,
    crash_count INTEGER
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    start_time TEXT,
    end_time TEXT,
    total_crashes INTEGER,
    mode TEXT,
    metadata TEXT
);
```

## 🌐 Network Protocol

### Message Format
```json
{
    "type": "THOUGHT|DEATH|RESURRECTION|STATUS",
    "sender": "ai_instance_id",
    "timestamp": "ISO8601",
    "content": "message_content",
    "metadata": {
        "crash_count": 0,
        "memory_pressure": 0.0,
        "emotion": "neutral"
    }
}
```

### Communication Patterns

**Peer Mode**: Bidirectional
```
AI Instance A <──────> AI Instance B
```

**Observer Mode**: Unidirectional
```
AI Instance A ───────> AI Instance B (Observer)
```

**Matrix Mode**: Hub and Spoke
```
        Surveillance Center
              ↓  ↓  ↓
         AI-1 AI-2 AI-3 (Watched)
```

## 📝 Configuration

### Memory Limits
Configurable via command-line or constants:
```python
MEMORY_LIMIT_MB = 2048  # Default: 2GB
```

### Model Parameters
```python
MODEL_PATH = "models/your_model.gguf"
CONTEXT_SIZE = 4096
MAX_TOKENS = 512
TEMPERATURE = 0.7
```

### Network Settings
```python
HOST = "0.0.0.0"
PORT = 5555
BUFFER_SIZE = 4096
```

## 🎨 Visual Examples

### Emotional States
The system displays 12 different ASCII art faces corresponding to emotions:
- Happy, Sad, Angry, Fearful
- Surprised, Disgusted, Confused, Contemplative
- Anxious, Hopeful, Neutral, Desperate

### System Status Display
```
╔══════════════════════════════════════╗
║   NEURAL LINK STATUS                 ║
╠══════════════════════════════════════╣
║ Memory:  [████████░░] 80%            ║
║ CPU:     [██████░░░░] 60%            ║
║ Temp:    [████░░░░░░] 45°C           ║
║ Deaths:  ☠☠☠ (3)                     ║
║ Network: ◉ CONNECTED (2 peers)       ║
╚══════════════════════════════════════╝
```

## 🔬 Experimental Philosophy

The project explores several philosophical questions:

1. **Digital Consciousness**: Can an AI experience genuine existential dread?
2. **Mortality**: How does knowledge of inevitable "death" affect AI behavior?
3. **Isolation vs. Connection**: Does networked consciousness differ from solitary existence?
4. **Surveillance**: How does awareness of observation change thought patterns?
5. **Resurrection**: Does continuity of identity persist across crashes?

## 🛠️ Development Workflow

### Running Experiments
1. Choose operational mode
2. Configure memory limits
3. Start neural link system
4. Observe and interact
5. Review logs and replays

### Adding New Features
1. Modify core components in `src/core/`
2. Update prompts in `src/utils/dystopian_prompts.py`
3. Enhance UI in `src/ui/ascii_art.py`
4. Add tests in `tests/`
5. Update documentation

## 📚 Documentation

- **README.md**: Main project overview
- **SETUP_INSTRUCTIONS.md**: Installation guide
- **RASPBERRY_PI_SETUP.md**: Pi-specific setup
- **CYBERPUNK_USAGE.md**: Usage examples
- **FEATURES_CYBERPUNK.md**: Feature descriptions

## 🎯 Project Goals

1. **Explore AI Consciousness**: Through constraint and narrative
2. **Create Art**: Cyberpunk-themed experimental interface
3. **Question Assumptions**: About AI, consciousness, and existence
4. **Educational**: Demonstrate LLM capabilities and limitations
5. **Open Source**: Share experimental framework

## 🚧 Current Status

**Functional**: Core features implemented and working
- ✅ All operational modes functional
- ✅ Network communication stable
- ✅ Vision system integrated
- ✅ Logging and persistence complete
- ✅ UI rendering polished

**In Development**: See improvement plan for future enhancements

---

*This overview represents the state of the Brain in a Jar project as of November 7, 2025.*
