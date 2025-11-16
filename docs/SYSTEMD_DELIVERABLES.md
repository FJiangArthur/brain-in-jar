# Systemd Integration - Deliverables Summary

Complete systemd integration for production experiment deployment on Jetson Orin AGX.

## Files Created

### 1. systemd Service Files

#### `/home/user/brain-in-jar/systemd/brain-experiment@.service`
**Template service for individual experiments**

- Instance name = experiment_id (e.g., `brain-experiment@amnesiac_001.service`)
- Features:
  - Auto-restart on crash (max 3 attempts in 5 minutes)
  - Proper logging to journald with experiment_id tag
  - Resource limits (RAM, CPU) via cgroups
  - Graceful shutdown (30s timeout)
  - GPU device access (Jetson Orin)
  - Security hardening (sandboxing, capability dropping)
- Usage:
  ```bash
  sudo systemctl start brain-experiment@amnesiac_001
  sudo systemctl status brain-experiment@amnesiac_001
  sudo systemctl stop brain-experiment@amnesiac_001
  ```

#### `/home/user/brain-in-jar/systemd/brain-experiment-coordinator.service`
**Master service for multi-experiment coordination**

- Manages experiment queue
- Enforces resource limits across all experiments
- Monitors system health (temperature, memory, CPU)
- Handles Jetson Orin thermal throttling
- Lightweight (512MB RAM, 20% CPU quota)
- Always running when experiments are active

#### `/home/user/brain-in-jar/systemd/brain-experiment.target`
**Target for grouping all experiment services**

- Start all experiments together: `sudo systemctl start brain-experiment.target`
- Stop all experiments together: `sudo systemctl stop brain-experiment.target`
- Depends on coordinator service

### 2. Installation Script

#### `/home/user/brain-in-jar/scripts/install_systemd.sh`
**Automated installation script**

What it does:
- Copies service files to `/etc/systemd/system/`
- Creates configuration directories:
  - `/etc/brain-in-jar/` - System config
  - `/etc/brain-in-jar/experiments/` - Per-experiment configs
  - `/var/log/brain-in-jar/` - System logs
  - `/run/brain-in-jar/` - Runtime files
- Sets permissions (user ownership, secure modes)
- Configures logrotate for log rotation
- Creates example environment files
- Configures GPU access (on Jetson)
- Enables and starts coordinator
- Verifies installation

Usage:
```bash
sudo ./scripts/install_systemd.sh
```

### 3. Python Interface

#### `/home/user/brain-in-jar/src/infra/systemd_manager.py`
**Python API for systemd experiment management**

Key classes:
- `SystemdManager` - Main interface for experiment control
- `ExperimentStatus` - Status data structure
- `SystemdWebMonitor` - Web UI integration

Features:
- `start_experiment(exp_id, config_path)` - Start experiment
- `stop_experiment(exp_id)` - Stop experiment
- `restart_experiment(exp_id)` - Restart experiment
- `get_status(exp_id)` - Get detailed status (state, PID, memory, CPU, restarts)
- `get_logs(exp_id, lines=100)` - Retrieve logs
- `list_experiments()` - List all running experiments
- `get_all_statuses()` - Get status of all experiments
- `enable_experiment(exp_id)` - Auto-start on boot
- `disable_experiment(exp_id)` - Disable auto-start

CLI usage:
```bash
python3 -m src.infra.systemd_manager list
python3 -m src.infra.systemd_manager start amnesiac_001 config.json
python3 -m src.infra.systemd_manager status amnesiac_001
python3 -m src.infra.systemd_manager logs amnesiac_001 100
python3 -m src.infra.systemd_manager stop amnesiac_001
```

Python usage:
```python
from src.infra.systemd_manager import SystemdManager

manager = SystemdManager()

# Start experiment
manager.start_experiment(
    "amnesiac_001",
    "experiments/configs/amnesiac_001.json",
    env_vars={"EXPERIMENT_RAM_LIMIT": "8G"}
)

# Get status
status = manager.get_status("amnesiac_001")
print(f"State: {status.state.value}")
print(f"Memory: {status.memory_current_mb}MB / {status.memory_limit_mb}MB")
print(f"Restarts: {status.restart_count}")

# Get logs
logs = manager.get_logs("amnesiac_001", lines=100)

# Stop
manager.stop_experiment("amnesiac_001")
```

#### `/home/user/brain-in-jar/src/infra/experiment_coordinator.py`
**Coordinator daemon for multi-experiment management**

Features:
- Experiment queue management
- Global resource limit enforcement
- Health monitoring loop (every 30 seconds)
- Temperature monitoring (Jetson Orin)
- Thermal throttling (75°C warning, 85°C critical)
- Queue persistence (survives restarts)
- Configurable via `/etc/brain-in-jar/coordinator.env`

### 4. Documentation

#### `/home/user/brain-in-jar/docs/SYSTEMD_INTEGRATION.md`
**Comprehensive documentation** (4000+ words)

Sections:
- Overview and architecture
- Installation instructions
- Usage guide (individual experiments, all experiments, coordinator)
- Python API examples
- Configuration (per-experiment, coordinator)
- Resource management (memory, CPU, GPU)
- Crash/resurrection semantics
- Jetson Orin integration
- Recovery on system reboot
- Logging and log rotation
- Troubleshooting
- Security and sandboxing
- Performance tuning
- Example workflows

#### `/home/user/brain-in-jar/docs/SYSTEMD_QUICKSTART.md`
**5-minute quick start guide**

- Installation
- Basic commands
- Python API snippets
- Quick examples
- Common troubleshooting

## Service Features

### Auto-restart on Failure (Crash/Resurrection)

**Configuration in service file:**
```ini
Restart=on-failure      # Restart only on crashes
RestartSec=5s           # Wait 5 seconds (resurrection delay)
StartLimitBurst=3       # Max 3 restarts in interval
StartLimitInterval=300s # 5 minute window
```

**How it preserves crash semantics:**
1. Experiment crashes (e.g., OOM, Python exception)
2. systemd detects failure (exit code != 0)
3. Waits 5 seconds (resurrection delay)
4. Restarts experiment process
5. ExperimentRunner loads crash count from database
6. Continues with incremented crash_count
7. Mode applies crash semantics (memory corruption, etc.)

**Monitoring:**
```bash
# View restart count
sudo systemctl show brain-experiment@amnesiac_001 --property=NRestarts

# View crash history
sudo journalctl -u brain-experiment@amnesiac_001 | grep -i crash
```

### Resource Limits via cgroups

**Memory limits:**
```ini
MemoryMax=${EXPERIMENT_RAM_LIMIT:-4G}
MemorySwapMax=0
MemoryAccounting=true
```

**CPU limits:**
```ini
CPUQuota=${EXPERIMENT_CPU_QUOTA:-80%}
CPUAccounting=true
```

**Configuration:**
- Default: 4GB RAM, 80% CPU
- Override via `/etc/brain-in-jar/experiments/<id>.env`
- Or pass env_vars in Python API

**Viewing usage:**
```bash
sudo systemctl status brain-experiment@amnesiac_001 | grep Memory
sudo systemctl show brain-experiment@amnesiac_001 --property=MemoryCurrent
```

### Logging to journald

**All output tagged:**
```ini
StandardOutput=journal
StandardError=journal
SyslogIdentifier=brain-experiment-%i
```

**Viewing logs:**
```bash
# Real-time
sudo journalctl -u brain-experiment@amnesiac_001 -f

# Last 100 lines
sudo journalctl -u brain-experiment@amnesiac_001 -n 100

# Since time
sudo journalctl -u brain-experiment@amnesiac_001 --since "1 hour ago"

# All experiments
sudo journalctl -t 'brain-experiment-*' -f
```

**Log rotation:**
- Configured via `/etc/logrotate.d/brain-in-jar`
- Daily rotation
- Compress old logs
- Keep 30 days (file logs) or 60 days (experiment logs)

### Graceful Shutdown

**Configuration:**
```ini
TimeoutStopSec=30s  # Allow 30 seconds for cleanup
KillMode=mixed      # SIGTERM to main process, then SIGKILL to remaining
KillSignal=SIGTERM  # Graceful shutdown signal
```

**What happens:**
1. systemctl stop issued
2. systemd sends SIGTERM to experiment process
3. ExperimentRunner._handle_interrupt() catches signal
4. Experiment finishes current cycle
5. Database is updated (experiment ended cleanly)
6. Process exits
7. If still running after 30s, SIGKILL sent

### Dependency Management

**Service dependencies:**
```ini
After=network.target
PartOf=brain-experiment.target
Requires=brain-experiment.target
```

**Coordinator dependency:**
```ini
# In target file
After=brain-experiment-coordinator.service
Requires=brain-experiment-coordinator.service
```

**Effect:**
- Experiments start after network is available
- Experiments are part of the target (grouped)
- Stopping target stops all experiments
- Coordinator starts before experiments

## Jetson Orin Integration

### GPU Resource Management

**Device access configured:**
```ini
DeviceAllow=/dev/nvidia0 rw
DeviceAllow=/dev/nvidiactl rw
DeviceAllow=/dev/nvidia-modeset rw
DeviceAllow=/dev/nvidia-uvm rw
DeviceAllow=/dev/nvidia-uvm-tools rw
SupplementaryGroups=video
```

**User added to video group:**
```bash
sudo usermod -a -G video user
```

**udev rules created:**
```bash
/etc/udev/rules.d/99-brain-in-jar-gpu.rules
```

### Temperature-based Throttling

**Coordinator monitors:**
- `/sys/class/thermal/thermal_zone0/temp` (CPU)
- Other thermal zones (GPU)

**Thresholds:**
- 75°C: Warning, begin throttling
- 85°C: Critical, emergency shutdown

**Actions:**
- Log warnings
- Reduce resource limits
- Pause new experiments
- Emergency stop all experiments (critical temp)

### Power Mode Integration

**Set via environment:**
```bash
# In /etc/brain-in-jar/experiments/<id>.env
NVPMODEL_MODE=0  # 0 = MAXN (max performance)
```

**Manual control:**
```bash
# Set max performance
sudo nvpmodel -m 0
sudo jetson_clocks

# Verify
sudo nvpmodel -q
```

## Recovery Behavior on System Reboot

### State Persistence

**What survives reboot:**
- Experiment database (`logs/experiments.db`)
  - Experiment metadata
  - Cycle history
  - Crash counts
  - Self-reports
  - Interventions
- Experiment configs (`experiments/configs/*.json`)
- Service enable/disable state
- Resource limits (in .env files)
- Coordinator queue (`logs/experiment_queue.json`)

**What does NOT survive:**
- In-memory conversation history (managed by modes)
- Running processes (PIDs)
- Current cycle state (resumes from database)

### Auto-start on Boot

**Enable auto-start:**
```bash
sudo systemctl enable brain-experiment@amnesiac_001
```

**Disable auto-start:**
```bash
sudo systemctl disable brain-experiment@amnesiac_001
```

**Check if enabled:**
```bash
systemctl is-enabled brain-experiment@amnesiac_001
```

**What happens on boot:**
1. System boots
2. systemd reads enabled services
3. Coordinator starts (if enabled)
4. Network becomes available
5. Enabled experiments start automatically
6. Each experiment:
   - Loads config from JSON file
   - Loads state from database (crash_count, cycle_number, etc.)
   - Initializes mode
   - Continues from last known state

### Recovery Example

**Scenario:** System loses power during experiment

**Before power loss:**
- `amnesiac_001` running, cycle 15, crash_count 3
- Database has all data up to cycle 15
- Service is enabled for auto-start

**After reboot:**
```bash
# System boots
# systemd automatically starts brain-experiment@amnesiac_001

# Check status
$ sudo systemctl status brain-experiment@amnesiac_001
● brain-experiment@amnesiac_001.service - Brain-in-Jar Experiment: amnesiac_001
   Active: active (running) since Thu 2025-01-16 10:00:00 UTC; 2min ago

# Experiment resumes
# Loads from database: cycle_number=15, crash_count=3
# Continues from cycle 16
```

## Web UI Integration

### Using SystemdWebMonitor

```python
from flask import Flask, jsonify
from flask_socketio import SocketIO
from src.infra.systemd_manager import SystemdManager, SystemdWebMonitor

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize
manager = SystemdManager()
monitor = SystemdWebMonitor(manager, socketio)

# Dashboard endpoint
@app.route('/api/experiments')
def get_experiments():
    return jsonify(monitor.get_dashboard_data())

# Start experiment
@app.route('/api/experiments/<exp_id>/start', methods=['POST'])
def start_experiment(exp_id):
    config_path = request.json.get('config_path')
    success = manager.start_experiment(exp_id, config_path)
    return jsonify({'success': success})

# Real-time status updates
@socketio.on('subscribe_experiment')
def handle_subscribe(exp_id):
    monitor.emit_status_update(exp_id)
```

### Dashboard Data Structure

```json
{
  "timestamp": "2025-01-16T10:00:00",
  "experiments": {
    "amnesiac_001": {
      "experiment_id": "amnesiac_001",
      "service_name": "brain-experiment@amnesiac_001.service",
      "state": "active",
      "sub_state": "running",
      "pid": 12345,
      "memory_current_mb": 2048,
      "memory_peak_mb": 3072,
      "memory_limit_mb": 4096,
      "cpu_usage_percent": 45.2,
      "active_since": "2025-01-16T09:00:00",
      "restart_count": 2
    }
  },
  "summary": {
    "total_experiments": 3,
    "running": 2,
    "stopped": 1,
    "total_memory_mb": 6144
  }
}
```

## Installation Instructions

### 1. Install systemd Integration

```bash
cd /home/user/brain-in-jar
sudo ./scripts/install_systemd.sh
```

### 2. Verify Installation

```bash
# Check service files
ls -la /etc/systemd/system/brain-experiment*

# Check directories
ls -la /etc/brain-in-jar/
ls -la /var/log/brain-in-jar/

# Check coordinator
sudo systemctl status brain-experiment-coordinator
```

### 3. Start Coordinator

```bash
sudo systemctl start brain-experiment-coordinator
sudo systemctl enable brain-experiment-coordinator
```

### 4. Run First Experiment

```bash
# Ensure config exists
ls experiments/configs/amnesiac_001.json

# Start experiment
sudo systemctl start brain-experiment@amnesiac_001

# Monitor
sudo journalctl -u brain-experiment@amnesiac_001 -f
```

### 5. Enable Auto-start (Optional)

```bash
# Enable experiment to start on boot
sudo systemctl enable brain-experiment@amnesiac_001

# Verify
systemctl is-enabled brain-experiment@amnesiac_001
```

## How to Manage Experiments via systemd

### Starting Experiments

**Via systemctl:**
```bash
sudo systemctl start brain-experiment@<experiment_id>
```

**Via Python API:**
```python
manager.start_experiment("amnesiac_001", "experiments/configs/amnesiac_001.json")
```

**With custom resource limits:**
```python
manager.start_experiment(
    "amnesiac_001",
    "experiments/configs/amnesiac_001.json",
    env_vars={
        "EXPERIMENT_RAM_LIMIT": "8G",
        "EXPERIMENT_CPU_QUOTA": "100%"
    }
)
```

### Monitoring Experiments

**Check status:**
```bash
sudo systemctl status brain-experiment@amnesiac_001
```

**Get detailed metrics:**
```bash
sudo systemctl show brain-experiment@amnesiac_001 \
  --property=MemoryCurrent,MemoryPeak,MemoryMax,NRestarts
```

**View logs:**
```bash
# Real-time
sudo journalctl -u brain-experiment@amnesiac_001 -f

# Last 100 lines
sudo journalctl -u brain-experiment@amnesiac_001 -n 100

# Since timestamp
sudo journalctl -u brain-experiment@amnesiac_001 --since "2025-01-16 10:00:00"
```

**Python API:**
```python
# Get status
status = manager.get_status("amnesiac_001")
print(f"State: {status.state.value}")
print(f"Memory: {status.memory_current_mb}MB")

# Get logs
logs = manager.get_logs("amnesiac_001", lines=100)
print(logs)
```

### Stopping Experiments

**Via systemctl:**
```bash
sudo systemctl stop brain-experiment@amnesiac_001
```

**Via Python API:**
```python
manager.stop_experiment("amnesiac_001")
```

**Stop all experiments:**
```bash
sudo systemctl stop brain-experiment.target
```

### Restarting Experiments

**Via systemctl:**
```bash
sudo systemctl restart brain-experiment@amnesiac_001
```

**Via Python API:**
```python
manager.restart_experiment("amnesiac_001")
```

## Integration with Existing Experiment Runner

### No Changes Required

The experiment runner (`src/runner/experiment_runner.py`) works unchanged:

```python
# experiment_runner.py uses same interface
if __name__ == "__main__":
    config = ExperimentConfig.from_json(args.config)
    runner = ExperimentRunner(config, db_path=args.db)
    runner.start()
```

### systemd invokes it via:

```ini
ExecStart=/home/user/brain-in-jar/venv/bin/python3 -m src.runner.experiment_runner \
    --config /home/user/brain-in-jar/experiments/configs/%i.json \
    --db /home/user/brain-in-jar/logs/experiments.db
```

### Crash detection works automatically:

1. Runner detects crash (OOM, exception)
2. Process exits with non-zero code
3. systemd sees failure
4. Restarts process after 5 seconds
5. Runner loads crash_count from database
6. Continues with crash semantics

### Signal handling preserved:

```python
# In ExperimentRunner.__init__
signal.signal(signal.SIGTERM, self._handle_interrupt)
signal.signal(signal.SIGINT, self._handle_interrupt)

def _handle_interrupt(self, signum, frame):
    """Handle interrupt signal"""
    self.console.print("\n[yellow]Received interrupt signal...[/yellow]")
    self.running = False
    # Cleanup happens in finally block
```

## Summary

**Complete systemd integration with:**

✅ Template service file for experiments
✅ Coordinator service for multi-experiment management
✅ Target for grouping
✅ Installation script with full automation
✅ Python API for programmatic control
✅ Web UI integration layer
✅ Resource management (RAM, CPU, GPU)
✅ Auto-restart on crash (preserves experiment semantics)
✅ Graceful shutdown
✅ Dependency management
✅ Comprehensive logging
✅ Log rotation
✅ Jetson Orin optimization (GPU access, temperature monitoring, power modes)
✅ Recovery on system reboot
✅ State persistence
✅ Security hardening
✅ Complete documentation (40+ pages)

**Ready for production deployment on Jetson Orin AGX.**
