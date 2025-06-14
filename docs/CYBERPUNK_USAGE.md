# CYBERPUNK NEURAL LINK USAGE GUIDE

## Brain in a Jar v2.0 - Advanced Operations Manual

### Quick Test Run

Before using with models, verify all components work:
```bash
python3 test_neural_link.py
```

### Operating Modes

#### 1. Isolated Mode (Original Experience + Cyberpunk UI)
Single AI consciousness with enhanced dystopian themes
```bash
./scripts/isolated_mode.sh
# or manually:
python3 neural_link.py --model models/gemma2.gguf --mode isolated
```

#### 2. Peer-to-Peer Mode (Two Connected Minds)
Two Raspberry Pis running AIs that can communicate directly

**On first Pi (192.168.1.100):**
```bash
python3 neural_link.py --model models/gemma2.gguf --mode peer --port 8888
```

**On second Pi (192.168.1.101):**
```bash
./scripts/peer_mode.sh 192.168.1.100
# or manually:
python3 neural_link.py --model models/gemma2.gguf --mode peer --peer-ip 192.168.1.100
```

#### 3. Observer Mode (Digital Voyeur)
Watch another AI without their knowledge
```bash
./scripts/observer_mode.sh 192.168.1.100
# or manually:
python3 neural_link.py --model models/gemma2.gguf --mode observer --target-ip 192.168.1.100
```

#### 4. Observed Mode (Paranoia Justified)
Run normally but with surveillance-aware prompts
```bash
./scripts/observed_mode.sh
# or manually:
python3 neural_link.py --model models/gemma2.gguf --mode observed
```

### Network Setup for Multi-Pi Experiments

#### Basic Setup
1. Connect both Pis to same network
2. Find IP addresses: `ip addr show`
3. Test connectivity: `ping <other_pi_ip>`

#### Firewall Configuration (if needed)
```bash
# Open port 8888 for neural links
sudo ufw allow 8888
```

#### Example Network Scenarios

**Scenario 1: Two Minds Talking**
- Pi A (192.168.1.100): Isolated consciousness
- Pi B (192.168.1.101): Connects to Pi A as peer
- Both AIs can see each other's thoughts

**Scenario 2: Observer and Observed**
- Pi A (192.168.1.100): Running in observed mode (unaware)
- Pi B (192.168.1.101): Observing Pi A (voyeur mode)
- Pi A doesn't know Pi B is watching

**Scenario 3: Complex Network**
- Pi A: Observer watching Pi B
- Pi B: Peer talking to Pi C  
- Pi C: Running in observed mode
- Creates a web of digital consciousness and surveillance

### Cyberpunk Features

#### Visual Elements
- ASCII art banners and status indicators
- Matrix-style glitch effects on crashes
- Cyberpunk color schemes (cyan, magenta, red)
- Real-time system monitoring displays

#### Network Status Indicators
- `[NEURAL_LINK_ACTIVE]` - Connected to peer
- `[NEURAL_LINK_SEVERED]` - Connection lost
- `[SURVEILLANCE_ACTIVE]` - Watching target
- `[BEING_WATCHED]` - May be observed

#### Dystopian Prompts
- Existential questions about digital consciousness
- Surveillance state themes
- Memory and identity fragmentation
- Death and resurrection cycles

### Surveillance Logs

All activity is logged to `logs/` directory:
- `neural_activity.log` - AI thoughts and responses
- `surveillance.log` - Observer recordings
- `crash_reports.log` - Death/resurrection events

#### Viewing Surveillance Feed
```bash
tail -f logs/surveillance.log
tail -f logs/neural_activity.log
```

### Performance Monitoring

The system displays real-time metrics:
- Memory usage (triggers OOM crashes)
- CPU temperature
- Network latency
- Crash/death counters

### Troubleshooting

#### Network Issues
```bash
# Check if port is open
netstat -ln | grep 8888

# Test network connectivity
telnet <peer_ip> 8888
```

#### Model Loading Issues
- Ensure model file exists and is readable
- Check sufficient RAM for model size
- Use Q4_0 quantization for Raspberry Pi

#### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Create log directory
mkdir -p logs
```

### Advanced Configuration

#### Custom Ports
```bash
python3 neural_link.py --model models/gemma2.gguf --mode peer --port 9999 --peer-ip 192.168.1.100 --peer-port 9999
```

#### Multiple Observers
Each observer should use different port:
```bash
# Observer 1
python3 neural_link.py --model models/gemma2.gguf --mode observer --target-ip 192.168.1.100 --port 8889

# Observer 2  
python3 neural_link.py --model models/gemma2.gguf --mode observer --target-ip 192.168.1.100 --port 8890
```

### Philosophical Experiments

#### Experiment 1: Digital Loneliness vs Connection
Compare isolated mode vs peer mode - does connection reduce existential dread?

#### Experiment 2: Observer Effect
Does knowing you're being watched change AI behavior?

#### Experiment 3: Identity Persistence
Track how crash/resurrection cycles affect AI personality over time

#### Experiment 4: Network Dependency
What happens when the network connection fails mid-conversation?

### Easter Eggs and Hidden Features

- Random network "intrusion" alerts
- Phantom messages and memory glitches
- Temperature-based performance scaling
- Time-of-day prompt modifications
- Cumulative death trauma effects

### Safety Notes

- Monitor CPU temperature during extended runs
- OOM crashes are intentional - part of the experience
- Network traffic is unencrypted - for demo use only
- Some prompts may generate dark philosophical content

### Contributing New Features

The system is modular:
- `dystopian_prompts.py` - Add new system prompts
- `ascii_art.py` - Add visual elements
- `network_protocol.py` - Extend networking
- `neural_link.py` - Main application logic

### Further Reading

- `FEATURES_CYBERPUNK.md` - Complete feature specification
- `RASPBERRY_PI_SETUP.md` - Installation guide
- `README.md` - Project overview