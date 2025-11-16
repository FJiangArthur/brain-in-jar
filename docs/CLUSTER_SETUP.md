# Multi-Node Cluster Setup Guide

Complete guide for setting up and running multi-node experiments across Jetson Orin AGX and Raspberry Pi 5.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Network Setup](#network-setup)
4. [SSH Configuration](#ssh-configuration)
5. [Software Installation](#software-installation)
6. [Cluster Configuration](#cluster-configuration)
7. [Deployment](#deployment)
8. [Running Experiments](#running-experiments)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Coordinator (Host)                        │
│  • ClusterOrchestrator                                      │
│  • Placement Algorithm                                      │
│  • Health Monitoring                                        │
│  • Log Aggregation                                          │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────────┬──────────────┐
    │                 │                  │              │
    ▼                 ▼                  ▼              ▼
┌─────────┐    ┌──────────┐      ┌──────────┐   ┌──────────┐
│ Jetson  │    │   RPi 1  │      │   RPi 2  │   │   Host   │
│  Orin   │    │          │      │          │   │  (Local) │
│ 64GB    │    │   8GB    │      │   8GB    │   │  32GB    │
│ CUDA    │    │  CPU     │      │  CPU     │   │  CPU     │
│ 3-4 inst│    │  1 inst  │      │  1 inst  │   │  2 inst  │
└─────────┘    └──────────┘      └──────────┘   └──────────┘
```

### Components

1. **ClusterOrchestrator** (`src/infra/cluster_orchestrator.py`)
   - Manages cluster topology
   - Intelligent placement algorithm
   - Node health monitoring
   - Resource tracking

2. **RemoteRunner** (`src/infra/remote_runner.py`)
   - SSH-based execution
   - Code deployment
   - Process management
   - Log streaming

3. **CLI** (`scripts/cluster_experiment.py`)
   - User interface
   - Configuration validation
   - Deployment automation
   - Monitoring dashboard

---

## Hardware Requirements

### Jetson Orin AGX 64GB

- **RAM:** 64GB unified memory
- **GPU:** NVIDIA Ampere (CUDA 11.4+)
- **Storage:** 64GB+ eMMC/NVMe
- **Network:** Gigabit Ethernet
- **OS:** Ubuntu 20.04+ (JetPack 5.0+)
- **Capacity:** 3-4 simultaneous experiments

### Raspberry Pi 5 8GB

- **RAM:** 8GB LPDDR4X
- **CPU:** Quad-core Cortex-A76
- **Storage:** 64GB+ microSD (or NVMe via HAT)
- **Network:** Gigabit Ethernet
- **OS:** Raspberry Pi OS (64-bit) or Ubuntu 22.04
- **Capacity:** 1 experiment

### Host Machine (Coordinator)

- **RAM:** 16GB+ recommended
- **Network:** Gigabit Ethernet (same subnet as nodes)
- **OS:** Linux (Ubuntu 20.04+ recommended)
- **Storage:** Sufficient for logs and databases

---

## Network Setup

### Network Topology

All nodes should be on the same local network for minimal latency:

```
192.168.1.0/24
├── 192.168.1.100  → Jetson Orin AGX
├── 192.168.1.101  → Raspberry Pi 1
├── 192.168.1.102  → Raspberry Pi 2 (optional)
└── 192.168.1.10   → Host (coordinator)
```

### Static IP Configuration

#### On Jetson Orin (via netplan)

```bash
# Edit /etc/netplan/01-netcfg.yaml
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

```bash
sudo netplan apply
```

#### On Raspberry Pi (via dhcpcd)

```bash
sudo nano /etc/dhcpcd.conf
```

Add:

```
interface eth0
static ip_address=192.168.1.101/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
```

```bash
sudo systemctl restart dhcpcd
```

### Verify Connectivity

```bash
# From host
ping 192.168.1.100  # Jetson
ping 192.168.1.101  # RPi 1
ping 192.168.1.102  # RPi 2
```

---

## SSH Configuration

### Generate SSH Keys (on Host)

```bash
# Generate key (if you don't have one)
ssh-keygen -t rsa -b 4096 -C "cluster@brain-in-jar"

# Use default location: ~/.ssh/id_rsa
```

### Copy Keys to Nodes

```bash
# Jetson
ssh-copy-id jetson@192.168.1.100

# Raspberry Pi
ssh-copy-id pi@192.168.1.101
ssh-copy-id pi@192.168.1.102
```

### Test Passwordless SSH

```bash
# Should connect without password prompt
ssh jetson@192.168.1.100
ssh pi@192.168.1.101
```

### SSH Config (Optional but Recommended)

Create `~/.ssh/config`:

```
Host jetson
    HostName 192.168.1.100
    User jetson
    IdentityFile ~/.ssh/id_rsa

Host rpi1
    HostName 192.168.1.101
    User pi
    IdentityFile ~/.ssh/id_rsa

Host rpi2
    HostName 192.168.1.102
    User pi
    IdentityFile ~/.ssh/id_rsa
```

Now you can just: `ssh jetson`

---

## Software Installation

### On All Nodes (Jetson + RPi)

#### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Install Python 3.9+

```bash
# Check version
python3 --version  # Should be 3.9+

# If needed, install
sudo apt install python3 python3-pip python3-venv -y
```

#### 3. Install Dependencies

```bash
sudo apt install -y \
    build-essential \
    git \
    rsync \
    htop \
    tmux
```

#### 4. Install Python Packages

```bash
pip3 install --upgrade pip

pip3 install \
    pyyaml \
    asyncssh \
    rich \
    psutil \
    aiosqlite
```

### On Jetson Orin: CUDA Setup

```bash
# Check CUDA installation
nvcc --version
nvidia-smi

# If not installed, follow JetPack installation:
# https://developer.nvidia.com/embedded/jetpack

# Install llama-cpp-python with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip3 install llama-cpp-python
```

### On Raspberry Pi: Optimize for Performance

```bash
# Increase swap (helpful for 8GB model)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

---

## Cluster Configuration

### Update Cluster Config

Edit `src/infra/cluster_config.yaml`:

```yaml
nodes:
  - name: jetson
    host: 192.168.1.100  # ← UPDATE THIS
    ssh_user: jetson      # ← UPDATE THIS
    ssh_key_path: ~/.ssh/id_rsa  # ← UPDATE THIS

  - name: rpi1
    host: 192.168.1.101  # ← UPDATE THIS
    ssh_user: pi          # ← UPDATE THIS
    ssh_key_path: ~/.ssh/id_rsa  # ← UPDATE THIS
```

### Validate Configuration

```bash
cd /home/user/brain-in-jar

python scripts/cluster_experiment.py --validate-config
```

Expected output:

```
╭─────────────────────────────────────╮
│ Validating Cluster Configuration   │
╰─────────────────────────────────────╯

Nodes: 3
  • jetson: 192.168.1.100 (64GB RAM, GPU, max 4 instances)
  • rpi1: 192.168.1.101 (8GB RAM, CPU, max 1 instances)
  • host: localhost (32GB RAM, CPU, max 2 instances)

✓ Configuration loaded successfully
```

---

## Deployment

### Deploy Code to All Nodes

```bash
python scripts/cluster_experiment.py --deploy-all
```

This will:
1. Connect to each remote node via SSH
2. Sync code using rsync
3. Create necessary directories
4. Install dependencies (if needed)

### Manual Deployment (Alternative)

```bash
# Jetson
rsync -avz --exclude '*.pyc' --exclude '__pycache__' \
    . jetson@192.168.1.100:~/brain-in-jar/

# Raspberry Pi
rsync -avz --exclude '*.pyc' --exclude '__pycache__' \
    . pi@192.168.1.101:~/brain-in-jar/
```

### Deploy Models (Large Files)

Models should be deployed separately (too large for rsync):

```bash
# On each node, download models directly
ssh jetson@192.168.1.100
cd ~/brain-in-jar/models
wget https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_0.gguf
```

---

## Running Experiments

### Health Check

Before running experiments, check cluster health:

```bash
python scripts/cluster_experiment.py --health-check
```

Expected output:

```
╭─────────────────────╮
│ Cluster Health Check│
╰─────────────────────╯

┏━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━┳━━━━━━━━━━━━━━┓
┃ Node   ┃ Host           ┃ Status  ┃ RAM (GB)┃ GPU ┃ Max Instances┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━╇━━━━━━━━━━━━━━┩
│ jetson │ 192.168.1.100  │ healthy │ 64      │ ✓   │ 4            │
│ rpi1   │ 192.168.1.101  │ healthy │ 8       │ ✗   │ 1            │
│ host   │ localhost      │ healthy │ 32      │ ✗   │ 2            │
└────────┴────────────────┴─────────┴─────────┴─────┴──────────────┘

✓ All 3 nodes are healthy
```

### Example 1: SPLIT_BRAIN

Run two instances with manual placement:

```bash
python scripts/cluster_experiment.py \
    --config experiments/examples/split_brain_001_brain_A.json \
    --config experiments/examples/split_brain_001_brain_B.json \
    --placement "split_brain_001_brain_A:jetson,split_brain_001_brain_B:rpi1"
```

**Rationale:**
- Brain A on Jetson: Can use GPU for larger model
- Brain B on RPi: Different hardware creates asymmetry

### Example 2: HIVE_CLUSTER

Run 4-instance hive with automatic placement:

```bash
python scripts/cluster_experiment.py \
    --config experiments/examples/hive_cluster_4minds.json \
    --auto-place
```

**Automatic Placement:**
- Orchestrator will place 3 instances on Jetson (12GB each)
- 1 instance on RPi (6GB)
- Optimizes for resource efficiency

### Example 3: PANOPTICON

Subject on constrained hardware, observer on powerful hardware:

```bash
python scripts/cluster_experiment.py \
    --config experiments/examples/panopticon_subject.json \
    --config experiments/examples/panopticon_observer.json \
    --placement "panopticon_subject:rpi1,panopticon_observer:jetson"
```

**Rationale:**
- Subject on RPi: Resource constraints create pressure
- Observer on Jetson: More resources for analysis tasks

### Example 4: PRISONERS_DILEMMA

Symmetric placement for fairness:

```bash
python scripts/cluster_experiment.py \
    --config experiments/examples/prisoners_dilemma_player_a.json \
    --config experiments/examples/prisoners_dilemma_player_b.json \
    --placement "player_a:rpi1,player_b:rpi2"
```

**Rationale:**
- Both players on identical hardware
- Fair resource allocation
- Network isolated

---

## Monitoring

### Real-Time Monitoring

The cluster script monitors experiments in real-time:

```bash
python scripts/cluster_experiment.py \
    --config experiments/split_brain_001_brain_A.json \
    --auto-place \
    --monitor-duration 600  # Monitor for 10 minutes
```

### SSH into Running Experiments

```bash
# SSH into Jetson
ssh jetson@192.168.1.100

# Monitor logs
cd ~/brain-in-jar
tail -f logs/split_brain_001_brain_A.log

# Check resources
htop
nvidia-smi  # GPU usage
```

### Web Monitoring (Jetson)

If you set up the web interface:

```bash
# On Jetson
cd ~/brain-in-jar
python scripts/web_monitor.py --port 5001

# From host, forward port
ssh -L 8080:localhost:5001 jetson@192.168.1.100

# Open browser: http://localhost:8080
```

### Aggregate Logs

Fetch logs from all nodes:

```bash
# Fetch from Jetson
scp jetson@192.168.1.100:~/brain-in-jar/logs/experiments.db \
    logs/jetson_experiments.db

# Fetch from RPi
scp pi@192.168.1.101:~/brain-in-jar/logs/experiments.db \
    logs/rpi1_experiments.db
```

---

## Placement Algorithm

### How It Works

The `PlacementStrategy` class scores each node for each instance:

```python
score = resource_efficiency(30) +
        load_balancing(20) +
        gpu_preference(15) +
        affinity(25) +
        preferred_node(10)
```

### Scoring Factors

1. **Resource Efficiency (0-30 points)**
   - Prefers nodes where instance uses 30-70% of available RAM
   - Avoids wasting resources or overloading nodes

2. **Load Balancing (0-20 points)**
   - Distributes instances across nodes
   - Prefers less loaded nodes

3. **GPU Preference (0-15 points)**
   - GPU workloads → GPU nodes
   - CPU workloads → CPU nodes

4. **Affinity/Anti-Affinity (0-25 points)**
   - Respects instance placement hints
   - Anti-affinity: Hard constraint (score = -1)
   - Affinity: Bonus for co-location

5. **Preferred Node (0-10 points)**
   - Bonus if instance specifies preferred node

### Example Placement

**Scenario:**
- Instance A: 8GB RAM, GPU required
- Instance B: 2GB RAM, no GPU, anti-affinity with A
- Instance C: 4GB RAM, no GPU, affinity with A

**Nodes:**
- Jetson: 64GB, GPU
- RPi1: 8GB, no GPU
- Host: 32GB, no GPU

**Result:**
```
Instance A → Jetson  (GPU required, high score)
Instance B → RPi1    (anti-affinity with A)
Instance C → Jetson  (affinity with A, room available)
```

---

## Troubleshooting

### SSH Connection Fails

**Problem:** `Permission denied (publickey)`

**Solution:**
```bash
# Check SSH key permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Re-copy key
ssh-copy-id user@host
```

### Deployment Fails

**Problem:** `rsync: command not found`

**Solution:**
```bash
# Install rsync on remote node
ssh user@host
sudo apt install rsync -y
```

### Experiment Won't Start

**Problem:** `ModuleNotFoundError`

**Solution:**
```bash
# SSH into node
ssh user@host
cd ~/brain-in-jar

# Install dependencies
pip3 install -r requirements.txt
```

### Out of Memory on Jetson

**Problem:** CUDA OOM errors

**Solution:**
```bash
# Reduce max_instances in config
# Or reduce ram_limit_gb per experiment
# Or use smaller model

# Check current usage
nvidia-smi

# Kill processes
pkill python3
```

### Out of Memory on Raspberry Pi

**Problem:** Killed by OOM

**Solution:**
```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Or reduce RAM limit in experiment config
```

### Node Shows as Unavailable

**Problem:** Health check fails

**Solution:**
```bash
# Check node is online
ping 192.168.1.100

# Check SSH
ssh user@host

# Check free memory
free -h

# Restart if needed
sudo reboot
```

### Logs Not Streaming

**Problem:** Can't see experiment output

**Solution:**
```bash
# SSH into node
ssh user@host
cd ~/brain-in-jar

# Check logs directory
ls -la logs/

# Manually tail
tail -f logs/experiment_id.log

# Check process is running
ps aux | grep experiment_runner
```

---

## Advanced Topics

### Custom Placement Strategies

Modify `PlacementStrategy.score_node()` to implement custom logic:

```python
# Example: Prefer specific nodes for specific experiment types
if 'panopticon_subject' in instance.instance_id:
    if node.name == 'rpi1':
        score += 50  # Strong preference
```

### Multi-Cluster Federation

Connect multiple clusters:

```yaml
# cluster_config.yaml
federation:
  enabled: true
  peers:
    - name: lab2_cluster
      coordinator: 192.168.2.100
      port: 8888
```

### GPU Sharing on Jetson

Experimental support for running multiple instances on same GPU:

```yaml
# In cluster_config.yaml
experimental:
  gpu_sharing: true
```

### Live Migration

Move running experiments between nodes (experimental):

```python
# In cluster_experiment.py
await orchestrator.migrate_instance(
    instance_id='split_brain_A',
    from_node='jetson',
    to_node='host'
)
```

---

## Performance Benchmarks

### Jetson Orin AGX 64GB

| Configuration | Instances | Model Size | RAM per Instance | Tokens/sec |
|--------------|-----------|------------|------------------|------------|
| Single (GPU) | 1         | 7B Q4      | 16GB            | ~45        |
| Multi (GPU)  | 3         | 1.5B Q4    | 12GB each       | ~30 each   |
| Max (CPU)    | 4         | 1.5B Q4    | 12GB each       | ~15 each   |

### Raspberry Pi 5 8GB

| Configuration | Instances | Model Size | RAM per Instance | Tokens/sec |
|--------------|-----------|------------|------------------|------------|
| Single       | 1         | 1.5B Q4    | 6GB             | ~8         |

### Network Latency

- Same node (localhost): < 1ms
- Same subnet (LAN): 1-5ms
- Cross-subnet: 10-50ms (not recommended)

---

## Next Steps

1. **Run Health Check**: `python scripts/cluster_experiment.py --health-check`
2. **Deploy Code**: `python scripts/cluster_experiment.py --deploy-all`
3. **Start Simple**: Run split brain experiment
4. **Scale Up**: Try hive cluster with 4 instances
5. **Monitor**: Watch resource usage and logs
6. **Analyze**: Aggregate results from all nodes

## Resources

- [Jetson Orin Documentation](https://developer.nvidia.com/embedded/jetson-orin)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [AsyncSSH Documentation](https://asyncssh.readthedocs.io/)
- [YAML Configuration Guide](https://yaml.org/spec/1.2/spec.html)

---

**Questions?** Open an issue on GitHub or consult the main README.md
