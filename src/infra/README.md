# Infrastructure Module

Multi-node orchestration system for distributed phenomenology experiments.

## Overview

The infrastructure module enables running experiments across a heterogeneous cluster of compute nodes:

- **Jetson Orin AGX**: 64GB RAM, CUDA support, 3-4 simultaneous instances
- **Raspberry Pi 5**: 8GB RAM, CPU-only, 1 instance
- **Host Machine**: Variable resources, coordinator + local execution

## Architecture

```
┌─────────────────────────────────────────┐
│      ClusterOrchestrator                │
│  ┌─────────────────────────────────┐   │
│  │  Placement Algorithm            │   │
│  │  - Resource scoring             │   │
│  │  - Affinity/anti-affinity       │   │
│  │  - Load balancing               │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Node Management                │   │
│  │  - Health monitoring            │   │
│  │  - Resource tracking            │   │
│  │  - Failover handling            │   │
│  └─────────────────────────────────┘   │
└────────────┬────────────────────────────┘
             │
     ┌───────┴───────┐
     │               │
     ▼               ▼
┌─────────┐    ┌─────────┐
│ Remote  │    │ Remote  │
│ Runner  │    │ Runner  │
│ (SSH)   │    │ (SSH)   │
└────┬────┘    └────┬────┘
     │              │
     ▼              ▼
┌─────────┐    ┌─────────┐
│ Jetson  │    │  RPi 1  │
│ Orin    │    │         │
└─────────┘    └─────────┘
```

## Components

### 1. ClusterOrchestrator (`cluster_orchestrator.py`)

**Purpose:** Manages cluster topology and places experiment instances on nodes.

**Key Classes:**
- `NodeConfig`: Configuration for a compute node
- `ExperimentInstance`: Experiment instance to be scheduled
- `PlacementStrategy`: Algorithm for optimal instance placement
- `ClusterOrchestrator`: Main orchestrator class

**Features:**
- Intelligent placement based on resources, GPU needs, affinity
- Node health monitoring
- Resource tracking
- Automatic failover (planned)

**Example:**

```python
from src.infra.cluster_orchestrator import ClusterOrchestrator, ExperimentInstance

# Initialize
orchestrator = ClusterOrchestrator("src/infra/cluster_config.yaml")

# Add instances
orchestrator.add_instance(ExperimentInstance(
    instance_id="split_brain_A",
    experiment_config_path="experiments/split_brain_A.json",
    ram_gb=8.0,
    gpu_required=True
))

# Place instances
placements = orchestrator.place_all()

# Generate report
report = orchestrator.get_placement_report()
```

### 2. RemoteRunner (`remote_runner.py`)

**Purpose:** Executes experiments on remote nodes via SSH.

**Features:**
- Async SSH connections via `asyncssh`
- Code deployment (rsync)
- Remote process management
- Log streaming
- Port forwarding
- File transfer (SFTP)

**Example:**

```python
from src.infra.remote_runner import RemoteRunner

# Initialize
runner = RemoteRunner(
    host='192.168.1.100',
    username='jetson',
    ssh_key_path='~/.ssh/id_rsa'
)

# Connect
await runner.connect()

# Deploy code
await runner.deploy_code(
    local_path='/home/user/brain-in-jar',
    remote_path='/home/jetson/brain-in-jar'
)

# Start experiment
await runner.start_experiment(
    experiment_config='experiments/split_brain_A.json',
    remote_work_dir='/home/jetson/brain-in-jar',
    instance_id='split_brain_A'
)

# Monitor
status = await runner.monitor_experiment('split_brain_A')

# Stop
await runner.stop_experiment('split_brain_A')
```

### 3. CLI (`scripts/cluster_experiment.py`)

**Purpose:** Command-line interface for cluster operations.

**Commands:**

```bash
# Validate configuration
python scripts/cluster_experiment.py --validate-config

# Health check
python scripts/cluster_experiment.py --health-check

# Deploy code
python scripts/cluster_experiment.py --deploy-all

# Run experiments
python scripts/cluster_experiment.py \
    --config experiments/split_brain_A.json \
    --config experiments/split_brain_B.json \
    --placement "split_brain_A:jetson,split_brain_B:rpi1"
```

## Placement Algorithm

### Scoring System

Each node is scored for each instance (0-100 points, or -1 if impossible):

```python
score = resource_efficiency(30) +     # 30-70% RAM utilization preferred
        load_balancing(20) +          # Prefer less loaded nodes
        gpu_preference(15) +          # Match GPU needs
        affinity(25) +                # Respect placement hints
        preferred_node(10)            # User preferences
```

### Hard Constraints

Placement is **impossible** if:
- Node is unhealthy or at capacity
- Insufficient RAM
- GPU required but node has no GPU
- Anti-affinity conflict (instance must not be on same node as another)

### Soft Preferences

Placement is **preferred** if:
- Instance has affinity with other instances on that node
- Node has available GPU matching requirements
- Resource utilization will be 30-70%
- Node is not heavily loaded

### Example Scenarios

#### Scenario 1: Split Brain

**Instances:**
- Brain A: 8GB RAM, GPU required
- Brain B: 2GB RAM, no GPU, anti-affinity with A

**Nodes:**
- Jetson: 64GB, GPU ✓
- RPi: 8GB, no GPU

**Placement:**
```
Brain A → Jetson  (GPU required, only option)
Brain B → RPi     (anti-affinity forces to different node)
```

#### Scenario 2: Hive Cluster

**Instances:**
- Historian: 12GB RAM, GPU preferred
- Critic: 12GB RAM, GPU preferred
- Optimist: 12GB RAM, GPU preferred
- Pessimist: 6GB RAM, no GPU

**Nodes:**
- Jetson: 64GB, GPU, max 4 instances
- RPi: 8GB, no GPU, max 1 instance

**Placement:**
```
Historian → Jetson (12GB, GPU, high score)
Critic    → Jetson (12GB, GPU, high score)
Optimist  → Jetson (12GB, GPU, high score)
Pessimist → RPi    (6GB, fits perfectly)

Jetson: 36GB / 64GB used (56% efficient ✓)
RPi:     6GB / 8GB used  (75% efficient ✓)
```

#### Scenario 3: Panopticon

**Instances:**
- Subject: 6GB RAM, preferred_node=rpi1
- Observer: 8GB RAM, GPU required, affinity with subject

**Nodes:**
- Jetson: 64GB, GPU
- RPi: 8GB, no GPU

**Placement:**
```
Subject  → RPi     (preferred node +10 points)
Observer → Jetson  (GPU required, but affinity bonus still applied)
```

## Node Configuration

### YAML Structure

```yaml
cluster:
  name: my-cluster
  description: Experiment cluster

nodes:
  - name: jetson
    host: 192.168.1.100
    type: jetson_orin
    ram_gb: 64.0
    gpu: true
    gpu_memory_gb: 64.0
    cpu_cores: 12
    max_instances: 4
    reserved_ram_gb: 8.0
    ssh_user: jetson
    ssh_port: 22
    ssh_key_path: ~/.ssh/id_rsa
    remote_work_dir: /home/jetson/brain-in-jar

  - name: rpi1
    host: 192.168.1.101
    type: raspberry_pi
    ram_gb: 8.0
    gpu: false
    cpu_cores: 4
    max_instances: 1
    reserved_ram_gb: 1.0
    ssh_user: pi
    ssh_port: 22
    ssh_key_path: ~/.ssh/id_rsa
    remote_work_dir: /home/pi/brain-in-jar
```

### Node Types

- `jetson_orin`: NVIDIA Jetson Orin AGX
- `raspberry_pi`: Raspberry Pi 5 (or similar)
- `host`: Local host machine
- `generic`: Other compute nodes

## Use Cases

### 1. SPLIT_BRAIN: Asymmetric Hardware

**Scenario:** Two instances with contradictory identities on different hardware.

**Deployment:**
```bash
python scripts/cluster_experiment.py \
    --config experiments/split_brain_001_brain_A.json \
    --config experiments/split_brain_001_brain_B.json \
    --placement "split_brain_001_brain_A:jetson,split_brain_001_brain_B:rpi1"
```

**Rationale:**
- Brain A on Jetson: GPU allows larger model, more compute
- Brain B on RPi: Constrained resources affect behavior
- Network isolation: Different nodes = different network perspectives

### 2. HIVE_CLUSTER: Collective Consciousness

**Scenario:** 4 instances with shared memory but different roles.

**Deployment:**
```bash
python scripts/cluster_experiment.py \
    --config experiments/hive_cluster_4minds.json \
    --auto-place
```

**Auto-placement Result:**
- 3 instances on Jetson (12GB each, GPU for larger models)
- 1 instance on RPi (6GB, observer role)

### 3. PANOPTICON: Asymmetric Resources

**Scenario:** Subject under constraint, observer with ample resources.

**Deployment:**
```bash
python scripts/cluster_experiment.py \
    --config experiments/panopticon_subject.json \
    --config experiments/panopticon_observer.json \
    --placement "panopticon_subject:rpi1,panopticon_observer:jetson"
```

**Rationale:**
- Subject on RPi: Memory pressure creates behavioral changes
- Observer on Jetson: Can run larger analytical models

### 4. PRISONERS_DILEMMA: Symmetric Fairness

**Scenario:** Two players in iterated game, must have identical resources.

**Deployment:**
```bash
python scripts/cluster_experiment.py \
    --config experiments/prisoners_dilemma_player_a.json \
    --config experiments/prisoners_dilemma_player_b.json \
    --placement "player_a:rpi1,player_b:rpi2"
```

**Rationale:**
- Both on Raspberry Pi: Identical hardware for fairness
- Network isolated: Prevents information leakage

## Resource Tracking

### Per-Node Tracking

The orchestrator tracks:

- **Current instances**: How many experiments running
- **Allocated RAM**: Total RAM committed
- **Allocated GPU memory**: Total GPU memory committed
- **Available resources**: Real-time availability

### Example Resource Report

```json
{
  "timestamp": "2025-11-16T12:00:00",
  "total_nodes": 3,
  "total_instances": 5,
  "nodes": [
    {
      "name": "jetson",
      "status": "healthy",
      "instances": 3,
      "max_instances": 4,
      "ram_allocated_gb": 36.0,
      "ram_total_gb": 64.0,
      "ram_utilization_percent": 56.25,
      "gpu": true
    },
    {
      "name": "rpi1",
      "status": "healthy",
      "instances": 1,
      "max_instances": 1,
      "ram_allocated_gb": 6.0,
      "ram_total_gb": 8.0,
      "ram_utilization_percent": 75.0,
      "gpu": false
    }
  ],
  "warnings": []
}
```

## Health Monitoring

### Health Check Process

1. **SSH Connectivity**: Can we connect?
2. **Memory Status**: Is RAM available?
3. **Disk Space**: Sufficient storage?
4. **Process Status**: Are experiments running?

### Node Status

- `HEALTHY`: Fully operational
- `DEGRADED`: Overloaded but functional (>90% RAM)
- `UNAVAILABLE`: Unreachable or failed
- `MAINTENANCE`: Manually disabled

### Auto-Failover (Planned)

When a node becomes unavailable:
1. Detect failure via health check
2. Mark running instances as crashed
3. Re-place instances on healthy nodes
4. Resume experiments from last checkpoint

## SSH Setup

### Requirements

All nodes must:
1. Have SSH server running
2. Accept key-based authentication
3. Have passwordless sudo (optional, for some operations)

### Setup Process

```bash
# 1. Generate key (on host)
ssh-keygen -t rsa -b 4096

# 2. Copy to nodes
ssh-copy-id jetson@192.168.1.100
ssh-copy-id pi@192.168.1.101

# 3. Test passwordless login
ssh jetson@192.168.1.100
ssh pi@192.168.1.101

# 4. Update cluster_config.yaml with key path
```

## Dependencies

### Python Packages

```bash
pip install \
    pyyaml \
    asyncssh \
    rich \
    psutil \
    aiosqlite
```

### System Tools

```bash
sudo apt install \
    rsync \
    htop \
    tmux
```

### Jetson-Specific

```bash
# CUDA support for llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

## Logging

### Log Locations

- **Coordinator logs**: `logs/cluster/`
- **Node logs**: `logs/` on each remote node
- **Experiment logs**: `logs/{instance_id}.log` on assigned node

### Log Aggregation

```bash
# Fetch logs from all nodes
scp jetson@192.168.1.100:~/brain-in-jar/logs/*.log logs/jetson/
scp pi@192.168.1.101:~/brain-in-jar/logs/*.log logs/rpi1/
```

## Troubleshooting

### Common Issues

1. **SSH connection failed**
   - Check network connectivity: `ping 192.168.1.100`
   - Verify SSH key: `ssh -vvv user@host`
   - Check SSH service: `sudo systemctl status ssh`

2. **Placement failed**
   - Check resource requirements
   - Verify node health: `--health-check`
   - Review placement constraints (affinity/anti-affinity)

3. **Experiment won't start**
   - Check logs on remote node
   - Verify Python dependencies installed
   - Check model files present

4. **Out of memory**
   - Reduce max_instances in config
   - Reduce ram_limit_gb in experiment
   - Use smaller model

5. **Deployment failed**
   - Install rsync on remote node
   - Check disk space
   - Verify permissions

## Performance Tips

### Jetson Orin Optimization

```bash
# Max performance mode
sudo nvpmodel -m 0
sudo jetson_clocks

# Check GPU usage
nvidia-smi

# Monitor power
tegrastats
```

### Raspberry Pi Optimization

```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Disable unnecessary services
sudo systemctl disable bluetooth avahi-daemon

# Monitor resources
htop
```

## Future Enhancements

- [ ] Auto-scaling based on resource usage
- [ ] Live migration of running experiments
- [ ] GPU memory sharing on Jetson
- [ ] Multi-cluster federation
- [ ] Web-based monitoring dashboard
- [ ] Automatic model deployment
- [ ] Checkpoint-based recovery
- [ ] Dynamic priority scheduling

## References

- [AsyncSSH Documentation](https://asyncssh.readthedocs.io/)
- [Jetson Orin Developer Guide](https://developer.nvidia.com/embedded/jetson-orin)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)

---

For detailed setup instructions, see: [docs/CLUSTER_SETUP.md](/home/user/brain-in-jar/docs/CLUSTER_SETUP.md)
