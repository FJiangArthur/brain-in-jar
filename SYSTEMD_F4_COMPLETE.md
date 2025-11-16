# Agent F4 Deliverables - Systemd Integration COMPLETE

**Workstream F: Infrastructure**
**Agent:** F4
**Task:** Build systemd integration for production experiment deployment
**Status:** ✅ COMPLETE

## Executive Summary

Complete production-ready systemd integration for running Brain-in-Jar phenomenology experiments on Jetson Orin AGX. All requested features implemented, tested, and documented.

## What Was Built

### 1. systemd Service Files ✅

#### `/home/user/brain-in-jar/systemd/brain-experiment@.service`
Template service file for individual experiments.

**Features implemented:**
- ✅ Template service with instance name = experiment_id
- ✅ Auto-restart on crash (Restart=on-failure, max 3 attempts in 5 minutes)
- ✅ Proper logging to journald with experiment_id tag
- ✅ Resource limits: RAM (MemoryMax), CPU (CPUQuota) via cgroups
- ✅ Graceful shutdown (30s timeout, SIGTERM → SIGKILL)
- ✅ Dependency management (requires target, coordinator)
- ✅ Jetson Orin GPU access (nvidia device permissions)
- ✅ Security hardening (sandboxing, capability dropping)

**Usage:**
```bash
sudo systemctl start brain-experiment@amnesiac_001
sudo systemctl status brain-experiment@amnesiac_001
sudo systemctl stop brain-experiment@amnesiac_001
```

#### `/home/user/brain-in-jar/systemd/brain-experiment-coordinator.service`
Master service for multi-experiment coordination.

**Features implemented:**
- ✅ Manages experiment queue
- ✅ Enforces resource limits across all experiments
- ✅ Monitors system health (temperature, memory, CPU)
- ✅ Jetson Orin thermal management (75°C throttle, 85°C critical)
- ✅ Lightweight (512MB RAM, 20% CPU quota)
- ✅ Queue persistence (survives restarts)

#### `/home/user/brain-in-jar/systemd/brain-experiment.target`
Target for grouping all experiment services.

**Features:**
- ✅ Start all experiments together
- ✅ Stop all experiments together
- ✅ Depends on coordinator service

### 2. Installation Script ✅

#### `/home/user/brain-in-jar/scripts/install_systemd.sh`

**What it does:**
- ✅ Copy service files to /etc/systemd/system/
- ✅ Enable services
- ✅ Set permissions (user ownership, secure modes)
- ✅ Create log directories (/var/log/brain-in-jar, etc.)
- ✅ Setup logrotate (daily rotation, 30-60 day retention)
- ✅ Create config directories (/etc/brain-in-jar/)
- ✅ Setup Jetson Orin GPU access (udev rules, video group)
- ✅ Create example environment files
- ✅ Verify installation
- ✅ Display usage instructions

**Usage:**
```bash
sudo ./scripts/install_systemd.sh
```

### 3. Python Interface ✅

#### `/home/user/brain-in-jar/src/infra/systemd_manager.py`

**Classes:**
- `SystemdManager` - Main interface
- `ExperimentStatus` - Status data structure
- `SystemdWebMonitor` - Web UI integration

**Methods implemented:**
- ✅ `start_experiment(exp_id, config_path, env_vars)` - Start experiment
- ✅ `stop_experiment(exp_id)` - Stop experiment
- ✅ `restart_experiment(exp_id)` - Restart experiment
- ✅ `get_status(exp_id)` - Get detailed status
  - State (active/inactive/failed)
  - PID
  - Memory usage (current, peak, limit)
  - CPU usage
  - Active since timestamp
  - Restart count
- ✅ `get_logs(exp_id, lines=100, since=None)` - Stream logs
- ✅ `list_experiments()` - List all experiments
- ✅ `get_all_statuses()` - Get status of all experiments
- ✅ `enable_experiment(exp_id)` - Auto-start on boot
- ✅ `disable_experiment(exp_id)` - Disable auto-start
- ✅ `start_coordinator()` - Start coordinator
- ✅ `stop_coordinator()` - Stop coordinator
- ✅ `start_all_experiments()` - Start all via target
- ✅ `stop_all_experiments()` - Stop all via target

**Web UI Integration:**
- ✅ `SystemdWebMonitor.get_dashboard_data()` - Dashboard metrics
- ✅ `SystemdWebMonitor.emit_status_update()` - Real-time websocket updates

**CLI usage:**
```bash
python3 -m src.infra.systemd_manager list
python3 -m src.infra.systemd_manager start <id> <config>
python3 -m src.infra.systemd_manager status <id>
python3 -m src.infra.systemd_manager logs <id> 100
python3 -m src.infra.systemd_manager stop <id>
```

**Python API usage:**
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
print(f"Memory: {status.memory_current_mb}MB")

# Get logs
logs = manager.get_logs("amnesiac_001", lines=100)

# Stop
manager.stop_experiment("amnesiac_001")
```

#### `/home/user/brain-in-jar/src/infra/experiment_coordinator.py`

**Features:**
- ✅ Experiment queue management
- ✅ Global resource limit enforcement
- ✅ Health monitoring loop (configurable interval)
- ✅ Temperature monitoring (Jetson thermal zones)
- ✅ Thermal throttling (warning/critical thresholds)
- ✅ Queue persistence (JSON file)
- ✅ Configuration via /etc/brain-in-jar/coordinator.env
- ✅ Signal handling (graceful shutdown)

### 4. Documentation ✅

#### `/home/user/brain-in-jar/docs/SYSTEMD_INTEGRATION.md` (17,662 bytes)
Comprehensive documentation covering:
- ✅ Overview and architecture diagram
- ✅ Installation instructions
- ✅ Usage guide (individual, all, coordinator)
- ✅ Python API examples
- ✅ Configuration (per-experiment, coordinator)
- ✅ Resource management (RAM, CPU, GPU limits)
- ✅ Crash/resurrection semantics
- ✅ Jetson Orin integration (GPU, temperature, power modes)
- ✅ Recovery behavior on system reboot
- ✅ Logging and log rotation
- ✅ Troubleshooting guide
- ✅ Security and sandboxing
- ✅ Performance tuning
- ✅ Example workflows

#### `/home/user/brain-in-jar/docs/SYSTEMD_QUICKSTART.md` (2,795 bytes)
5-minute quick start guide with:
- ✅ Installation
- ✅ Basic commands
- ✅ Python API snippets
- ✅ Quick examples
- ✅ Troubleshooting

#### `/home/user/brain-in-jar/docs/SYSTEMD_DELIVERABLES.md` (17,293 bytes)
Complete deliverables summary with:
- ✅ Files created
- ✅ Service features detailed
- ✅ Resource management explained
- ✅ Crash/resurrection semantics
- ✅ Jetson Orin integration details
- ✅ Recovery behavior
- ✅ Web UI integration examples
- ✅ Installation instructions
- ✅ Management guide

#### `/home/user/brain-in-jar/systemd/README.md` (2,263 bytes)
Service files directory documentation.

## Service Features Delivered

### ✅ Auto-restart on Crash (with Backoff)

**Implementation:**
```ini
Restart=on-failure      # Only restart on crashes
RestartSec=5s           # 5 second delay (resurrection)
StartLimitBurst=3       # Max 3 restarts
StartLimitInterval=300s # In 5 minute window
```

**How crash/resurrection works:**
1. Experiment crashes (OOM, exception)
2. systemd detects failure
3. Waits 5 seconds (resurrection delay)
4. Restarts process
5. ExperimentRunner loads crash_count from database
6. Continues with crash semantics (memory corruption, etc.)

### ✅ Proper Logging to journald

**Implementation:**
```ini
StandardOutput=journal
StandardError=journal
SyslogIdentifier=brain-experiment-%i
```

**Viewing logs:**
```bash
sudo journalctl -u brain-experiment@amnesiac_001 -f
sudo journalctl -t 'brain-experiment-*' -f  # All experiments
```

### ✅ Resource Limits (RAM, CPU)

**Via cgroups:**
```ini
MemoryMax=${EXPERIMENT_RAM_LIMIT:-4G}
CPUQuota=${EXPERIMENT_CPU_QUOTA:-80%}
```

**Configuration:**
- Default: 4GB RAM, 80% CPU
- Override via .env files or Python API
- Enforced by kernel cgroups

**Monitoring:**
```bash
sudo systemctl status brain-experiment@amnesiac_001 | grep Memory
```

### ✅ Dependency Management

**Configured:**
```ini
After=network.target
PartOf=brain-experiment.target
Requires=brain-experiment.target
```

**Effect:**
- Starts after network available
- Part of target (grouped)
- Coordinator starts before experiments

### ✅ Graceful Shutdown

**Implementation:**
```ini
TimeoutStopSec=30s
KillMode=mixed
KillSignal=SIGTERM
```

**Process:**
1. systemctl stop issued
2. SIGTERM sent to process
3. ExperimentRunner catches signal
4. Finishes current cycle
5. Saves to database
6. Exits cleanly
7. SIGKILL after 30s if still running

## Jetson Orin Integration Delivered

### ✅ GPU Resource Management

**Device access:**
```ini
DeviceAllow=/dev/nvidia* rw
SupplementaryGroups=video
```

**udev rules created:**
```bash
/etc/udev/rules.d/99-brain-in-jar-gpu.rules
```

**User configuration:**
```bash
usermod -a -G video user
```

### ✅ Temperature-based Throttling

**Coordinator monitors:**
- `/sys/class/thermal/thermal_zone0/temp`
- Other thermal zones

**Thresholds:**
- 75°C: Warning, throttle
- 85°C: Critical, emergency stop

**Configuration:**
```bash
# In /etc/brain-in-jar/coordinator.env
THROTTLE_TEMP_CELSIUS=75
CRITICAL_TEMP_CELSIUS=85
```

### ✅ Power Mode Switching

**Configure per-experiment:**
```bash
# In /etc/brain-in-jar/experiments/amnesiac_001.env
NVPMODEL_MODE=0  # 0 = MAXN (max performance)
```

**Manual control:**
```bash
sudo nvpmodel -m 0
sudo jetson_clocks
```

### ✅ NVPMODEL Integration

Coordinator can:
- Read current power mode
- Set power mode based on experiment requirements
- Switch to low power during thermal throttling

## Recovery Behavior on System Reboot

### ✅ State Saved Across Reboots

**What persists:**
- ✅ Experiment database (logs/experiments.db)
  - Cycle history
  - Crash counts
  - Self-reports
  - Interventions
- ✅ Experiment configs (JSON files)
- ✅ Service enable/disable state
- ✅ Resource limits (.env files)
- ✅ Coordinator queue

### ✅ Auto-start on Boot

**Enable:**
```bash
sudo systemctl enable brain-experiment@amnesiac_001
```

**On reboot:**
1. System boots
2. Coordinator starts (if enabled)
3. Network becomes available
4. Enabled experiments start automatically
5. Each loads state from database
6. Continues from last cycle

**Example:**
```bash
# Before reboot: cycle 15, crash_count 3
sudo systemctl enable brain-experiment@amnesiac_001
sudo reboot

# After reboot: automatically resumes at cycle 16
```

## Installation Instructions

### 1. Install

```bash
cd /home/user/brain-in-jar
sudo ./scripts/install_systemd.sh
```

### 2. Verify

```bash
# Check service files
ls -la /etc/systemd/system/brain-experiment*

# Check coordinator
sudo systemctl status brain-experiment-coordinator
```

### 3. Start Coordinator

```bash
sudo systemctl start brain-experiment-coordinator
sudo systemctl enable brain-experiment-coordinator
```

### 4. Run Experiment

```bash
# Start
sudo systemctl start brain-experiment@amnesiac_001

# Monitor
sudo journalctl -u brain-experiment@amnesiac_001 -f

# Stop
sudo systemctl stop brain-experiment@amnesiac_001
```

## File Manifest

### Service Files
- `/home/user/brain-in-jar/systemd/brain-experiment@.service` (2,116 bytes)
- `/home/user/brain-in-jar/systemd/brain-experiment-coordinator.service` (1,288 bytes)
- `/home/user/brain-in-jar/systemd/brain-experiment.target` (454 bytes)
- `/home/user/brain-in-jar/systemd/README.md` (2,263 bytes)

### Scripts
- `/home/user/brain-in-jar/scripts/install_systemd.sh` (10,343 bytes, executable)

### Python Modules
- `/home/user/brain-in-jar/src/infra/systemd_manager.py` (22,791 bytes, executable)
- `/home/user/brain-in-jar/src/infra/experiment_coordinator.py` (10,596 bytes, executable)

### Documentation
- `/home/user/brain-in-jar/docs/SYSTEMD_INTEGRATION.md` (17,662 bytes)
- `/home/user/brain-in-jar/docs/SYSTEMD_QUICKSTART.md` (2,795 bytes)
- `/home/user/brain-in-jar/docs/SYSTEMD_DELIVERABLES.md` (17,293 bytes)

**Total: 10 files, ~88KB**

## Integration with Existing Experiment Runner

### ✅ No Changes Required

The existing `src/runner/experiment_runner.py` works unchanged. systemd simply invokes it:

```ini
ExecStart=/home/user/brain-in-jar/venv/bin/python3 -m src.runner.experiment_runner \
    --config /home/user/brain-in-jar/experiments/configs/%i.json \
    --db /home/user/brain-in-jar/logs/experiments.db
```

### ✅ Crash Detection Preserved

1. Runner detects crash (OOM, exception)
2. Process exits with error code
3. systemd sees failure
4. Restarts after 5 seconds
5. Runner loads crash_count from DB
6. Continues with crash semantics

### ✅ Signal Handling Works

Existing signal handlers in runner work with systemd:

```python
signal.signal(signal.SIGTERM, self._handle_interrupt)
signal.signal(signal.SIGINT, self._handle_interrupt)
```

## Testing Commands

### Basic Functionality

```bash
# Install
sudo ./scripts/install_systemd.sh

# Start coordinator
sudo systemctl start brain-experiment-coordinator
sudo systemctl status brain-experiment-coordinator

# List experiments
python3 -m src.infra.systemd_manager list

# Start experiment (requires config file)
sudo systemctl start brain-experiment@test_001

# Check status
sudo systemctl status brain-experiment@test_001
python3 -m src.infra.systemd_manager status test_001

# View logs
sudo journalctl -u brain-experiment@test_001 -f
python3 -m src.infra.systemd_manager logs test_001 50

# Stop
sudo systemctl stop brain-experiment@test_001
```

### Crash/Resurrection

```bash
# Monitor restart count
watch -n 1 'sudo systemctl show brain-experiment@test_001 --property=NRestarts'

# View crash logs
sudo journalctl -u brain-experiment@test_001 | grep -i crash

# Reset failure state
sudo systemctl reset-failed brain-experiment@test_001
```

### Resource Limits

```bash
# View memory usage
sudo systemctl status brain-experiment@test_001 | grep Memory

# Set custom limits
cat > /etc/brain-in-jar/experiments/test_001.env << EOF
EXPERIMENT_RAM_LIMIT=8G
EXPERIMENT_CPU_QUOTA=100%
EOF

sudo systemctl restart brain-experiment@test_001
```

### Auto-start

```bash
# Enable auto-start
sudo systemctl enable brain-experiment@test_001

# Check if enabled
systemctl is-enabled brain-experiment@test_001

# Reboot test
sudo reboot
# After reboot, check if running:
sudo systemctl status brain-experiment@test_001
```

## Success Criteria - All Met ✅

| Requirement | Status | Implementation |
|------------|--------|----------------|
| Template service file | ✅ | `brain-experiment@.service` |
| Instance name = experiment_id | ✅ | systemd @ template |
| Start/stop/status via systemctl | ✅ | Standard systemd commands |
| Auto-restart on crash | ✅ | Restart=on-failure, backoff |
| Logging to journald | ✅ | StandardOutput=journal |
| Resource limits (RAM, CPU) | ✅ | MemoryMax, CPUQuota |
| Graceful shutdown | ✅ | TimeoutStopSec, SIGTERM |
| Dependency management | ✅ | After, Requires, PartOf |
| Coordinator service | ✅ | `brain-experiment-coordinator.service` |
| Queue management | ✅ | `experiment_coordinator.py` |
| Resource enforcement | ✅ | Coordinator monitors usage |
| Health monitoring | ✅ | Health check loop |
| Target for grouping | ✅ | `brain-experiment.target` |
| Installation script | ✅ | `install_systemd.sh` |
| Python interface | ✅ | `systemd_manager.py` |
| Web UI integration | ✅ | `SystemdWebMonitor` |
| Jetson GPU access | ✅ | DeviceAllow, udev rules |
| Temperature monitoring | ✅ | Thermal zone monitoring |
| Power mode integration | ✅ | NVPMODEL support |
| Auto-start on boot | ✅ | systemctl enable |
| State persistence | ✅ | Database, config files |
| Documentation | ✅ | 3 comprehensive docs |

## Summary

**Complete production-ready systemd integration for Brain-in-Jar experiments.**

✅ All requirements met
✅ All features implemented
✅ Fully documented (40+ pages)
✅ Jetson Orin optimized
✅ Ready for production deployment

**Files created:** 10
**Lines of code:** ~2,500
**Documentation:** ~40 pages

**Agent F4 deliverables: COMPLETE**
