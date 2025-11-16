# systemd Integration - Quick Start Guide

5-minute guide to get experiments running via systemd.

## Installation

```bash
cd /home/user/brain-in-jar
sudo ./scripts/install_systemd.sh
```

## Basic Commands

### Start an Experiment

```bash
sudo systemctl start brain-experiment@amnesiac_001
```

### Check Status

```bash
sudo systemctl status brain-experiment@amnesiac_001
```

### View Logs

```bash
sudo journalctl -u brain-experiment@amnesiac_001 -f
```

### Stop an Experiment

```bash
sudo systemctl stop brain-experiment@amnesiac_001
```

### Restart an Experiment

```bash
sudo systemctl restart brain-experiment@amnesiac_001
```

## Python API

```python
from src.infra.systemd_manager import SystemdManager

manager = SystemdManager()

# Start
manager.start_experiment(
    "amnesiac_001",
    "experiments/configs/amnesiac_001.json"
)

# Status
status = manager.get_status("amnesiac_001")
print(status.state.value)

# Logs
print(manager.get_logs("amnesiac_001", lines=50))

# Stop
manager.stop_experiment("amnesiac_001")
```

## Quick Examples

### Example 1: Run Single Experiment

```bash
# Start
sudo systemctl start brain-experiment@amnesiac_001

# Monitor
sudo journalctl -u brain-experiment@amnesiac_001 -f

# Stop
sudo systemctl stop brain-experiment@amnesiac_001
```

### Example 2: Auto-start on Boot

```bash
# Enable
sudo systemctl enable brain-experiment@amnesiac_001

# Reboot (experiment will auto-start)
sudo reboot
```

### Example 3: Run Multiple Experiments

```bash
# Start coordinator
sudo systemctl start brain-experiment-coordinator

# Start experiments
sudo systemctl start brain-experiment@amnesiac_001
sudo systemctl start brain-experiment@unstable_002

# View all logs
sudo journalctl -t 'brain-experiment-*' -f

# Stop all
sudo systemctl stop brain-experiment.target
```

## Configuration

### Per-Experiment Limits

Create `/etc/brain-in-jar/experiments/amnesiac_001.env`:

```bash
EXPERIMENT_RAM_LIMIT=8G
EXPERIMENT_CPU_QUOTA=100%
```

Then restart:

```bash
sudo systemctl restart brain-experiment@amnesiac_001
```

## Troubleshooting

### Check Why Experiment Failed

```bash
sudo systemctl status brain-experiment@amnesiac_001
sudo journalctl -u brain-experiment@amnesiac_001 -n 100
```

### Reset Failed State

```bash
sudo systemctl reset-failed brain-experiment@amnesiac_001
```

### Check Memory Usage

```bash
sudo systemctl status brain-experiment@amnesiac_001 | grep Memory
```

## File Locations

- **Configs**: `/home/user/brain-in-jar/experiments/configs/<id>.json`
- **Logs**: `/home/user/brain-in-jar/logs/`
- **Database**: `/home/user/brain-in-jar/logs/experiments.db`
- **Service files**: `/etc/systemd/system/brain-experiment*`

## Full Documentation

See [SYSTEMD_INTEGRATION.md](./SYSTEMD_INTEGRATION.md) for complete documentation.
