# Brain-in-Jar: systemd Integration for Production Deployment

Complete systemd integration for running phenomenology experiments in production on Jetson Orin AGX.

## Overview

This systemd integration provides:

- **Template service** (`brain-experiment@.service`) for individual experiments
- **Coordinator service** (`brain-experiment-coordinator.service`) for multi-experiment management
- **Target** (`brain-experiment.target`) for grouping all experiments
- **Python API** (`systemd_manager.py`) for programmatic control
- **Installation script** for automated setup
- **Resource management** (RAM, CPU, GPU limits via cgroups)
- **Crash/resurrection semantics** preserved via restart policies
- **Jetson Orin optimization** (temperature monitoring, GPU access, power modes)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                brain-experiment.target                  │
│           (groups all experiment instances)             │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ brain-exp@   │  │ brain-exp@   │  │ brain-exp@   │
│ amnesiac_001 │  │ unstable_002 │  │ panopticon_  │
│              │  │              │  │   003        │
└──────────────┘  └──────────────┘  └──────────────┘

┌─────────────────────────────────────────────────────────┐
│        brain-experiment-coordinator.service             │
│  (manages queue, enforces limits, monitors health)      │
└─────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Ubuntu with systemd (Jetson Orin runs Ubuntu 20.04+)
- Root/sudo access
- Brain-in-Jar repository cloned
- Python virtual environment setup

### Install

```bash
cd /home/user/brain-in-jar
sudo ./scripts/install_systemd.sh
```

This will:
1. Copy service files to `/etc/systemd/system/`
2. Create config directories in `/etc/brain-in-jar/`
3. Setup log directories and logrotate
4. Configure GPU access (on Jetson)
5. Enable coordinator service
6. Reload systemd daemon

### Verify Installation

```bash
# Check service files are installed
ls -la /etc/systemd/system/brain-experiment*

# Check systemd sees them
sudo systemctl list-unit-files | grep brain-experiment

# Check coordinator status
sudo systemctl status brain-experiment-coordinator
```

## Usage

### Managing Individual Experiments

#### Start an Experiment

```bash
# First, ensure your experiment config exists at:
# /home/user/brain-in-jar/experiments/configs/<experiment_id>.json

# Start the experiment
sudo systemctl start brain-experiment@amnesiac_001

# Check status
sudo systemctl status brain-experiment@amnesiac_001

# View logs
sudo journalctl -u brain-experiment@amnesiac_001 -f
```

#### Stop an Experiment

```bash
sudo systemctl stop brain-experiment@amnesiac_001
```

#### Restart an Experiment

```bash
sudo systemctl restart brain-experiment@amnesiac_001
```

#### Enable Auto-start on Boot

```bash
sudo systemctl enable brain-experiment@amnesiac_001
```

#### Disable Auto-start

```bash
sudo systemctl disable brain-experiment@amnesiac_001
```

### Managing All Experiments

#### Start All

```bash
sudo systemctl start brain-experiment.target
```

#### Stop All

```bash
sudo systemctl stop brain-experiment.target
```

#### View All Experiment Logs

```bash
sudo journalctl -t 'brain-experiment-*' -f
```

### Managing the Coordinator

```bash
# Start coordinator
sudo systemctl start brain-experiment-coordinator

# Check coordinator status
sudo systemctl status brain-experiment-coordinator

# View coordinator logs
sudo journalctl -u brain-experiment-coordinator -f

# Enable coordinator on boot
sudo systemctl enable brain-experiment-coordinator
```

## Python API

### Basic Usage

```python
from src.infra.systemd_manager import SystemdManager

# Initialize manager
manager = SystemdManager()

# Start an experiment
manager.start_experiment(
    experiment_id="amnesiac_001",
    config_path="/home/user/brain-in-jar/experiments/configs/amnesiac_001.json"
)

# Get status
status = manager.get_status("amnesiac_001")
print(f"State: {status.state.value}")
print(f"Memory: {status.memory_current_mb}MB")
print(f"Restarts: {status.restart_count}")

# Get logs
logs = manager.get_logs("amnesiac_001", lines=100)
print(logs)

# Stop experiment
manager.stop_experiment("amnesiac_001")
```

### Advanced Usage

```python
# Start with custom environment variables
manager.start_experiment(
    experiment_id="amnesiac_001",
    config_path="experiments/configs/amnesiac_001.json",
    env_vars={
        "EXPERIMENT_RAM_LIMIT": "8G",
        "EXPERIMENT_CPU_QUOTA": "100%"
    }
)

# List all experiments
experiments = manager.list_experiments()
for exp_id in experiments:
    status = manager.get_status(exp_id)
    print(f"{exp_id}: {status.state.value}")

# Get all statuses
all_statuses = manager.get_all_statuses()
for exp_id, status in all_statuses.items():
    print(f"{exp_id}: {status.to_dict()}")

# Enable experiment to start on boot
manager.enable_experiment("amnesiac_001")
```

### Web UI Integration

```python
from src.infra.systemd_manager import SystemdManager, SystemdWebMonitor
from flask_socketio import SocketIO

# Initialize
manager = SystemdManager()
socketio = SocketIO(app)
monitor = SystemdWebMonitor(manager, socketio)

# Get dashboard data
@app.route('/api/experiments')
def experiments():
    return jsonify(monitor.get_dashboard_data())

# Emit real-time updates
@socketio.on('request_status')
def handle_status_request(experiment_id):
    monitor.emit_status_update(experiment_id)
```

## Configuration

### Per-Experiment Configuration

Create `/etc/brain-in-jar/experiments/<experiment_id>.env`:

```bash
# Resource Limits
EXPERIMENT_RAM_LIMIT=8G
EXPERIMENT_CPU_QUOTA=100%

# Jetson Orin Specific
NVPMODEL_MODE=0  # 0 = MAXN (max performance)
MAX_TEMP_CELSIUS=80
```

### Coordinator Configuration

Edit `/etc/brain-in-jar/coordinator.env`:

```bash
# Resource Management
MAX_CONCURRENT_EXPERIMENTS=4
TOTAL_RAM_LIMIT_GB=48

# Health Monitoring
HEALTH_CHECK_INTERVAL_SECONDS=30
TEMPERATURE_CHECK_INTERVAL_SECONDS=10

# Jetson Orin Throttling
THROTTLE_TEMP_CELSIUS=75
CRITICAL_TEMP_CELSIUS=85
```

## Resource Management

### Memory Limits

Set per-experiment memory limits:

```bash
# In experiment .env file
EXPERIMENT_RAM_LIMIT=4G  # 4 gigabytes
```

Or in Python:

```python
manager.start_experiment(
    experiment_id="amnesiac_001",
    config_path="experiments/configs/amnesiac_001.json",
    env_vars={"EXPERIMENT_RAM_LIMIT": "4G"}
)
```

### CPU Limits

```bash
# In experiment .env file
EXPERIMENT_CPU_QUOTA=80%  # 80% of available CPU
```

### Viewing Resource Usage

```bash
# View memory usage
sudo systemctl status brain-experiment@amnesiac_001 | grep Memory

# Detailed resource info
sudo systemctl show brain-experiment@amnesiac_001 \
  --property=MemoryCurrent,MemoryPeak,MemoryMax,CPUUsageNSec
```

## Crash/Resurrection Semantics

The systemd integration preserves experiment crash/resurrection behavior:

### Restart Policy

- **Restart=on-failure**: Automatically restart on crash
- **RestartSec=5s**: Wait 5 seconds before restart (resurrection delay)
- **StartLimitBurst=3**: Maximum 3 restarts in 5 minutes
- **StartLimitInterval=300s**: Reset restart counter after 5 minutes

### How It Works

1. Experiment process crashes (e.g., OOM)
2. systemd detects failure
3. Waits 5 seconds (resurrection delay)
4. Restarts experiment with same config
5. Experiment runner loads crash statistics
6. Continues with incremented crash count

### Monitoring Crashes

```bash
# View restart count
sudo systemctl show brain-experiment@amnesiac_001 --property=NRestarts

# View crash logs
sudo journalctl -u brain-experiment@amnesiac_001 | grep -i crash
```

## Jetson Orin Integration

### GPU Access

The service file configures GPU access:

```ini
# GPU device access
DeviceAllow=/dev/nvidia0 rw
DeviceAllow=/dev/nvidiactl rw
DeviceAllow=/dev/nvidia-modeset rw
DeviceAllow=/dev/nvidia-uvm rw
SupplementaryGroups=video
```

### Temperature Monitoring

The coordinator monitors thermal zones:

```python
# Automatic throttling at 75°C
# Emergency shutdown at 85°C
```

View temperature:

```bash
# System temperature
cat /sys/class/thermal/thermal_zone0/temp

# Or via coordinator logs
sudo journalctl -u brain-experiment-coordinator -f | grep -i temp
```

### Power Modes

Set power mode for high-performance experiments:

```bash
# Enable MAXN mode (maximum performance)
sudo nvpmodel -m 0
sudo jetson_clocks

# Or configure in experiment .env
NVPMODEL_MODE=0
```

## Recovery on System Reboot

### Automatic Recovery

Experiments marked with `enable` will auto-start on boot:

```bash
# Enable experiment to start on boot
sudo systemctl enable brain-experiment@amnesiac_001

# On next reboot, experiment will automatically start
```

### State Persistence

- **Experiment database**: Persisted in `/home/user/brain-in-jar/logs/experiments.db`
- **Crash statistics**: Loaded from database on restart
- **Conversation history**: Managed by experiment modes (amnesiac, unstable, etc.)
- **Queue state**: Coordinator saves queue to disk

### Recovery Process

1. System boots
2. Coordinator service starts
3. Enabled experiments start automatically
4. Each experiment:
   - Loads config from JSON
   - Loads state from database
   - Continues from last checkpoint

## Logging

### Log Locations

- **systemd journal**: `sudo journalctl -u brain-experiment@<id>`
- **Experiment logs**: `/home/user/brain-in-jar/logs/`
- **Database**: `/home/user/brain-in-jar/logs/experiments.db`

### Log Rotation

Configured via `/etc/logrotate.d/brain-in-jar`:

- **Journal logs**: Managed by systemd (default: 4GB limit)
- **File logs**: Rotate daily, keep 30 days
- **Experiment logs**: Rotate daily, keep 60 days, max 500MB

### Viewing Logs

```bash
# Real-time logs
sudo journalctl -u brain-experiment@amnesiac_001 -f

# Last 100 lines
sudo journalctl -u brain-experiment@amnesiac_001 -n 100

# Since timestamp
sudo journalctl -u brain-experiment@amnesiac_001 --since "1 hour ago"

# All experiments
sudo journalctl -t 'brain-experiment-*' -f

# Export logs
sudo journalctl -u brain-experiment@amnesiac_001 > experiment.log
```

## Troubleshooting

### Experiment Won't Start

```bash
# Check service status
sudo systemctl status brain-experiment@amnesiac_001

# Check for errors
sudo journalctl -u brain-experiment@amnesiac_001 -n 50

# Verify config exists
ls -la /home/user/brain-in-jar/experiments/configs/amnesiac_001.json

# Check file permissions
ls -la /home/user/brain-in-jar/logs/
```

### Out of Memory

```bash
# Check memory limit
sudo systemctl show brain-experiment@amnesiac_001 --property=MemoryMax

# Increase limit (temporary)
sudo systemctl set-property brain-experiment@amnesiac_001 MemoryMax=8G

# Or edit .env file and restart
```

### Too Many Restarts

```bash
# Check restart count
sudo systemctl show brain-experiment@amnesiac_001 --property=NRestarts

# Reset failure state
sudo systemctl reset-failed brain-experiment@amnesiac_001

# Check why it's crashing
sudo journalctl -u brain-experiment@amnesiac_001 | grep -C 5 "crash"
```

### Temperature Issues

```bash
# Check temperature
cat /sys/class/thermal/thermal_zone0/temp

# Check coordinator logs
sudo journalctl -u brain-experiment-coordinator -f | grep -i temp

# Enable max cooling
sudo nvpmodel -m 0
sudo jetson_clocks
```

### Permission Denied

```bash
# Check user ownership
sudo chown -R user:user /home/user/brain-in-jar/logs
sudo chown -R user:user /home/user/brain-in-jar/experiments

# Check service user
sudo systemctl show brain-experiment@amnesiac_001 --property=User
```

## CLI Tool

Use the Python API as a CLI:

```bash
# List all experiments
python3 -m src.infra.systemd_manager list

# Start experiment
python3 -m src.infra.systemd_manager start amnesiac_001 \
  experiments/configs/amnesiac_001.json

# Check status
python3 -m src.infra.systemd_manager status amnesiac_001

# Get logs
python3 -m src.infra.systemd_manager logs amnesiac_001 100

# Stop experiment
python3 -m src.infra.systemd_manager stop amnesiac_001

# Start all
python3 -m src.infra.systemd_manager start-all

# Stop all
python3 -m src.infra.systemd_manager stop-all
```

## Example Workflows

### Run a Single Experiment

```bash
# 1. Create experiment config
cat > experiments/configs/test_001.json << EOF
{
  "experiment_id": "test_001",
  "name": "Test Experiment",
  "mode": "amnesiac_loop",
  "max_cycles": 10,
  ...
}
EOF

# 2. Start via systemd
sudo systemctl start brain-experiment@test_001

# 3. Monitor logs
sudo journalctl -u brain-experiment@test_001 -f

# 4. Check status
sudo systemctl status brain-experiment@test_001

# 5. Stop when done
sudo systemctl stop brain-experiment@test_001
```

### Run Multiple Experiments

```bash
# 1. Start coordinator
sudo systemctl start brain-experiment-coordinator

# 2. Start experiments
sudo systemctl start brain-experiment@amnesiac_001
sudo systemctl start brain-experiment@unstable_002
sudo systemctl start brain-experiment@panopticon_003

# 3. Monitor all
sudo journalctl -t 'brain-experiment-*' -f

# 4. Stop all at once
sudo systemctl stop brain-experiment.target
```

### Deploy Production Experiment

```bash
# 1. Create production config
cp experiments/examples/amnesiac_total.json \
   experiments/configs/prod_amnesiac_001.json

# 2. Set resource limits
cat > /etc/brain-in-jar/experiments/prod_amnesiac_001.env << EOF
EXPERIMENT_RAM_LIMIT=8G
EXPERIMENT_CPU_QUOTA=100%
NVPMODEL_MODE=0
EOF

# 3. Enable auto-start
sudo systemctl enable brain-experiment@prod_amnesiac_001

# 4. Start now
sudo systemctl start brain-experiment@prod_amnesiac_001

# 5. Verify running
sudo systemctl status brain-experiment@prod_amnesiac_001

# 6. Will auto-start on reboot
sudo reboot
# (after reboot, experiment automatically resumes)
```

## Security

### Sandboxing

Services run with security hardening:

```ini
NoNewPrivileges=true          # Cannot escalate privileges
PrivateTmp=true               # Private /tmp
ProtectSystem=strict          # Read-only system directories
ProtectHome=read-only         # Read-only home
CapabilityBoundingSet=        # No special capabilities
```

### Allowed Paths

Experiments can only write to:

- `/home/user/brain-in-jar/logs`
- `/home/user/brain-in-jar/experiments`

### GPU Access

GPU devices are explicitly allowed:

```ini
DeviceAllow=/dev/nvidia0 rw
DeviceAllow=/dev/nvidiactl rw
```

## Performance Tuning

### Jetson Orin Optimization

```bash
# Set max performance mode
sudo nvpmodel -m 0
sudo jetson_clocks

# Verify mode
sudo nvpmodel -q

# Monitor power/temp
sudo tegrastats
```

### Memory Optimization

```bash
# For memory-intensive experiments, increase swap
sudo fallocate -l 32G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Set swappiness
sudo sysctl vm.swappiness=10
```

### CPU Pinning

For specific CPU core assignment, modify service file:

```ini
[Service]
CPUAffinity=0-7  # Use cores 0-7
```

## Files Created

### Service Files

- `/etc/systemd/system/brain-experiment@.service` - Template service
- `/etc/systemd/system/brain-experiment-coordinator.service` - Coordinator
- `/etc/systemd/system/brain-experiment.target` - Target for grouping

### Configuration

- `/etc/brain-in-jar/coordinator.env` - Coordinator settings
- `/etc/brain-in-jar/experiments/<id>.env` - Per-experiment settings
- `/etc/logrotate.d/brain-in-jar` - Log rotation

### Directories

- `/home/user/brain-in-jar/experiments/configs/` - Experiment configs
- `/home/user/brain-in-jar/logs/` - Experiment logs
- `/var/log/brain-in-jar/` - System logs
- `/run/brain-in-jar/` - Runtime files (IPC, sockets)

### Python Modules

- `/home/user/brain-in-jar/src/infra/systemd_manager.py` - Python API
- `/home/user/brain-in-jar/src/infra/experiment_coordinator.py` - Coordinator daemon

### Scripts

- `/home/user/brain-in-jar/scripts/install_systemd.sh` - Installation script

## Next Steps

1. **Install systemd integration**: `sudo ./scripts/install_systemd.sh`
2. **Start coordinator**: `sudo systemctl start brain-experiment-coordinator`
3. **Create experiment configs**: Place in `experiments/configs/`
4. **Start experiments**: Via systemctl or Python API
5. **Monitor via web UI**: Integrate with existing web interface
6. **Setup auto-start**: Enable experiments to survive reboots

## References

- systemd documentation: https://www.freedesktop.org/software/systemd/man/
- Jetson Orin docs: https://docs.nvidia.com/jetson/
- Brain-in-Jar web UI: `/home/user/brain-in-jar/src/web/web_server.py`
- Experiment schema: `/home/user/brain-in-jar/experiments/schema.py`
