# systemd Service Files

This directory contains systemd service files for production experiment deployment.

## Files

- **brain-experiment@.service** - Template service for individual experiments
- **brain-experiment-coordinator.service** - Master coordinator service
- **brain-experiment.target** - Target for grouping all experiments

## Installation

```bash
sudo ../scripts/install_systemd.sh
```

This will:
- Copy service files to `/etc/systemd/system/`
- Create configuration directories
- Setup log rotation
- Enable coordinator service

## Usage

### Individual Experiment

```bash
# Start
sudo systemctl start brain-experiment@amnesiac_001

# Status
sudo systemctl status brain-experiment@amnesiac_001

# Logs
sudo journalctl -u brain-experiment@amnesiac_001 -f

# Stop
sudo systemctl stop brain-experiment@amnesiac_001
```

### All Experiments

```bash
# Start all
sudo systemctl start brain-experiment.target

# Stop all
sudo systemctl stop brain-experiment.target
```

### Coordinator

```bash
# Start coordinator
sudo systemctl start brain-experiment-coordinator

# Enable on boot
sudo systemctl enable brain-experiment-coordinator
```

## Configuration

Per-experiment configuration in `/etc/brain-in-jar/experiments/<id>.env`:

```bash
EXPERIMENT_RAM_LIMIT=8G
EXPERIMENT_CPU_QUOTA=100%
```

Coordinator configuration in `/etc/brain-in-jar/coordinator.env`:

```bash
MAX_CONCURRENT_EXPERIMENTS=4
TOTAL_RAM_LIMIT_GB=48
THROTTLE_TEMP_CELSIUS=75
CRITICAL_TEMP_CELSIUS=85
```

## Documentation

- Quick start: [../docs/SYSTEMD_QUICKSTART.md](../docs/SYSTEMD_QUICKSTART.md)
- Full guide: [../docs/SYSTEMD_INTEGRATION.md](../docs/SYSTEMD_INTEGRATION.md)
- Deliverables: [../docs/SYSTEMD_DELIVERABLES.md](../docs/SYSTEMD_DELIVERABLES.md)

## Python API

```python
from src.infra.systemd_manager import SystemdManager

manager = SystemdManager()
manager.start_experiment("amnesiac_001", "experiments/configs/amnesiac_001.json")
status = manager.get_status("amnesiac_001")
manager.stop_experiment("amnesiac_001")
```

## Features

- Auto-restart on crash (max 3 attempts)
- Resource limits (RAM, CPU) via cgroups
- GPU access (Jetson Orin)
- Temperature monitoring
- Graceful shutdown
- Log rotation
- Security hardening
- Auto-start on boot (if enabled)
