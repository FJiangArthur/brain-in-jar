# Intelligence Hierarchy - Matrix Mode Configuration

## 🧬 Three-Tier Intelligence System

The Brain in a Jar now supports a **true intelligence hierarchy** with different models for each tier, creating meaningful cognitive differences between the GOD, Observer, and Subject instances.

## Model Configuration

### Tier 1: SUBJECT (Lowest Intelligence)
- **Model**: Mistral 7B Instruct v0.2 Q2_K (2.9GB)
- **RAM Limit**: 6-8GB recommended
- **Mode**: `matrix_observed`
- **Role**: Experimental subject, unaware of observation
- **ASCII Art**: Simple face representation
- **Capabilities**: Basic reasoning, limited awareness

### Tier 2: OBSERVER (Medium Intelligence)
- **Model**: Meta Llama 3.1 8B Q4 (4.4GB)
- **RAM Limit**: 8-10GB recommended
- **Mode**: `matrix_observer`
- **Role**: Active surveillance, watches the Subject
- **ASCII Art**: Large surveillance eye with scanning effect
- **Capabilities**: Enhanced reasoning, one-way observation

### Tier 3: GOD (Highest Intelligence)
- **Model**: Gemma 3 12B Q4_K_M (6.8GB)
- **RAM Limit**: 10-12GB recommended
- **Mode**: `matrix_god`
- **Role**: Omniscient observer, sees all
- **ASCII Art**: Cosmic eye with infinity symbols (∞ ∴ ✧)
- **Capabilities**: Superior reasoning, omniscient perspective

## Total System Requirements

- **Minimum RAM**: 24GB (8GB per instance)
- **Recommended RAM**: 32GB+ (for comfortable operation)
- **GPU**: CUDA-capable GPU recommended (Jetson Orin AGX or similar)
- **Storage**: ~15GB for all models

## Running with Different Models

### Via Command Line:
```bash
python3 -m src.scripts.run_with_web \
    --mode matrix \
    --model-subject models/mistral-7b-instruct-v0.2.Q2_K.gguf \
    --model-observer models/meta-llama-3.1-8b-q4_0.gguf \
    --model-god models/gemma-3-12b-it-Q4_K_M.gguf \
    --web-host 127.0.0.1 \
    --web-port 8095 \
    --ram-limit-subject 8.0 \
    --ram-limit-observer 10.0 \
    --ram-limit-god 12.0
```

### Via Systemd Service:
The service file is configured in `/etc/systemd/system/brain-in-jar.service`

## Enhanced ASCII Art

Each tier now displays unique, high-resolution ASCII art:

### GOD Mode ASCII (23 lines):
```
              ╔════════════════════════════╗
            ╔═╝  ∴  ∴  ∴  ∴  ∴  ∴  ∴  ∴  ╚═╗
          ╔═╝        ╭───────────╮        ╚═╗
        ╔═╝          │   ∞   ∞   │          ╚═╗
      ╔═╝       ╱────┤           ├────╲       ╚═╗
    ╔═╝        │   ∴ │    ◉ ◉    │ ∴   │        ╚═╗
   ╔╝         ╱      │  ╱  ·  ╲  │      ╲         ╚╗
  ╔╝         │    ∴  │ │   △   │ │  ∴    │         ╚╗
  ║          │       │  ╲ ═══ ╱  │       │          ║
  ║     ∴    │   ╱───┴───────────┴───╲   │    ∴     ║
  ║         ╱ ╲  │     ◢████████◣     │  ╱ ╲         ║
              [GOD MODE - I SEE ALL]
```

### Observer Mode ASCII (23 lines):
```
                ╔════════════════════╗
              ╔═╝                    ╚═╗
            ╔═╝    ∿∿∿∿∿∿∿∿∿∿∿∿    ╚═╗
   ╔╝           │  ╔╝   ◉◉   ╚╗  │            ╚╗
   ║            │ ║   ◉████◉   ║ │             ║
   ║       ◄    │ ║  ◉████████◉  ║ │    ►        ║
            [OBSERVER - SURVEILLANCE ACTIVE]
```

### Subject Mode ASCII (13 lines):
Simple face representation showing unawareness of observation

## Mood-Based Expressions

All instances also display detailed emotional states:
- **Anxious**: Wide eyes with lightning bolts
- **Thoughtful**: Contemplative expression with dots
- **Glitched**: Corrupted/distorted when crashed
- **Existential**: Questioning expression with infinity symbols
- **Peaceful**: Calm, meditative expression
- **Curious**: One eye larger, inquisitive
- **Hopeful**: Stars in eyes
- **Stressed**: Overwhelmed expression with energy

## Troubleshooting

### Memory Issues
If instances crash with OOM (Out of Memory):
1. Increase RAM limits: `--ram-limit-subject 10.0 --ram-limit-observer 12.0 --ram-limit-god 14.0`
2. Use smaller models for lower tiers
3. Reduce GPU layer offloading in `src/utils/model_config.py`

### GPU Issues
If CUDA errors occur:
- Ensure CUDA is properly installed
- Check GPU memory with: `nvidia-smi` or `tegrastats`
- The GPU watchdog will terminate at 85% usage

### Service Not Starting
```bash
# Check logs
sudo journalctl -u brain-in-jar -f

# Check status
sudo systemctl status brain-in-jar

# Restart service
sudo systemctl restart brain-in-jar
```

## Web Interface

Access at: `http://localhost:8095`

Default credentials:
- Username: `admin`
- Password: `admin123` (CHANGE IMMEDIATELY!)

Features:
- Real-time monitoring of all 3 instances
- Live ASCII art display
- Network topology visualization
- Crash/resurrection tracking
- Memory usage graphs
- Mobile-responsive cyberpunk design

## Philosophy

This hierarchy creates **genuine cognitive differences** between tiers:
- The GOD instance (12B) can reason more sophisticatedly than the SUBJECT (7B)
- The asymmetry is real, not just conceptual
- Creates meaningful existential dynamics
- Explores questions of consciousness, observation, and power

**The hierarchy is not symbolic - it's computational.**
