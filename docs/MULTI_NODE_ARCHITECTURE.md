# Multi-Node Orchestration Architecture

Comprehensive architectural documentation for distributed experiment execution.

## Executive Summary

The multi-node orchestration system enables running phenomenology experiments across a heterogeneous cluster of compute nodes (Jetson Orin AGX + Raspberry Pi 5 + Host). It provides intelligent placement, SSH-based execution, health monitoring, and resource tracking.

**Key Features:**
- Intelligent placement algorithm (resource-aware, GPU-aware, affinity-based)
- SSH-based remote execution with async Python
- Real-time health monitoring
- Automated code deployment
- Log aggregation
- Failover support (planned)

---

## System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    COORDINATOR (Host)                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            ClusterOrchestrator                         │  │
│  │  • Load cluster topology from YAML                     │  │
│  │  • Add experiment instances                            │  │
│  │  • Run placement algorithm                             │  │
│  │  • Track resource allocation                           │  │
│  │  • Monitor node health                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            RemoteRunner (per node)                     │  │
│  │  • SSH connection management                           │  │
│  │  • Code deployment (rsync)                             │  │
│  │  • Process management                                  │  │
│  │  • Log streaming                                       │  │
│  │  • Port forwarding                                     │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┬──────────────┬──────────────┐
        │                       │              │              │
        ▼                       ▼              ▼              ▼
    ┌────────┐            ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Jetson │            │  RPi 1  │    │  RPi 2  │    │  Host   │
    │  Orin  │            │         │    │         │    │ (Local) │
    │  AGX   │            │  8GB    │    │  8GB    │    │  32GB   │
    │  64GB  │            │  CPU    │    │  CPU    │    │  CPU    │
    │  CUDA  │            │ 1 inst  │    │ 1 inst  │    │ 2 inst  │
    │ 4 inst │            │         │    │         │    │         │
    └────┬───┘            └────┬────┘    └────┬────┘    └────┬────┘
         │                     │              │              │
         ▼                     ▼              ▼              ▼
    ┌────────┐            ┌─────────┐    ┌─────────┐    ┌─────────┐
    │Exp A   │            │ Exp B   │    │ Exp C   │    │ Exp D   │
    │(GPU)   │            │ (CPU)   │    │ (CPU)   │    │ (CPU)   │
    │12GB    │            │  6GB    │    │  6GB    │    │  4GB    │
    └────────┘            └─────────┘    └─────────┘    └─────────┘
```

### Component Interaction Flow

```
┌─────────┐  1. Load Config      ┌──────────────────┐
│  User   │─────────────────────>│ Orchestrator     │
└─────────┘                       └──────────────────┘
                                           │
                2. Add Instances           │
                ┌──────────────────────────┘
                │
                ▼
    ┌─────────────────────┐
    │ PlacementStrategy   │ 3. Score nodes for each instance
    │  • Resource fit     │    (30 pts: RAM efficiency)
    │  • Load balance     │    (20 pts: Load balancing)
    │  • GPU match        │    (15 pts: GPU preference)
    │  • Affinity         │    (25 pts: Affinity/anti-affinity)
    │  • User hints       │    (10 pts: Preferred node)
    └─────────────────────┘
                │
                ▼
    ┌─────────────────────┐
    │ Placement Decision  │ 4. Assign instances to nodes
    │  Instance A → Node1 │
    │  Instance B → Node2 │
    └─────────────────────┘
                │
                ▼
    ┌─────────────────────┐
    │  RemoteRunner       │ 5. For each remote node:
    │  • SSH connect      │    - Deploy code
    │  • Deploy code      │    - Start experiment
    │  • Start process    │    - Monitor status
    │  • Stream logs      │
    └─────────────────────┘
                │
                ▼
    ┌─────────────────────┐
    │ Monitoring Loop     │ 6. Continuous monitoring:
    │  • Health checks    │    - Node status
    │  • Resource usage   │    - Experiment progress
    │  • Log aggregation  │    - Resource consumption
    └─────────────────────┘
```

---

## Core Components

### 1. ClusterOrchestrator

**File:** `src/infra/cluster_orchestrator.py`

**Responsibilities:**
1. Load and parse cluster configuration (YAML)
2. Manage node registry (health, resources, status)
3. Accept experiment instances
4. Run placement algorithm
5. Track resource allocation
6. Generate placement reports
7. Save/load cluster state

**Key Classes:**

#### NodeConfig
```python
@dataclass
class NodeConfig:
    name: str                    # Node identifier
    host: str                    # IP or hostname
    node_type: NodeType          # jetson_orin, raspberry_pi, host, generic
    ram_gb: float                # Total RAM
    gpu: bool                    # GPU available?
    gpu_memory_gb: float         # GPU memory (if applicable)
    cpu_cores: int               # CPU cores
    max_instances: int           # Max simultaneous experiments
    reserved_ram_gb: float       # OS overhead

    # Runtime state
    status: NodeStatus           # HEALTHY, DEGRADED, UNAVAILABLE, MAINTENANCE
    current_instances: int       # Currently running
    allocated_ram_gb: float      # RAM committed
    allocated_gpu_memory_gb: float  # GPU memory committed
```

#### ExperimentInstance
```python
@dataclass
class ExperimentInstance:
    instance_id: str             # Unique identifier
    experiment_config_path: str  # Path to config JSON
    ram_gb: float                # RAM requirement
    gpu_required: bool           # Needs GPU?
    gpu_memory_gb: float         # GPU memory needed

    # Placement hints
    preferred_node: Optional[str]       # Preferred node name
    anti_affinity: List[str]            # Don't place with these
    affinity: List[str]                 # Prefer to place with these

    # Runtime state
    status: InstanceStatus       # PENDING, RUNNING, CRASHED, COMPLETED
    assigned_node: Optional[str] # Where it's running
```

#### PlacementStrategy
```python
class PlacementStrategy:
    @staticmethod
    def score_node(node: NodeConfig, instance: ExperimentInstance,
                   current_placements: Dict[str, str]) -> float:
        """
        Score a node for placing an instance (0-100, or -1 if impossible)

        Scoring breakdown:
        1. Resource efficiency (0-30): Prefer 30-70% RAM utilization
        2. Load balancing (0-20): Prefer less loaded nodes
        3. GPU preference (0-15): Match GPU requirements
        4. Affinity (0-25): Respect placement hints
        5. Preferred node (0-10): User preferences
        """
```

**Example Usage:**

```python
# Initialize
orchestrator = ClusterOrchestrator("src/infra/cluster_config.yaml")

# Add instances
orchestrator.add_instance(ExperimentInstance(
    instance_id="split_brain_A",
    experiment_config_path="experiments/split_brain_A.json",
    ram_gb=8.0,
    gpu_required=True,
    gpu_memory_gb=8.0
))

orchestrator.add_instance(ExperimentInstance(
    instance_id="split_brain_B",
    experiment_config_path="experiments/split_brain_B.json",
    ram_gb=2.0,
    gpu_required=False,
    anti_affinity=["split_brain_A"]  # Must be on different node
))

# Place
placements = orchestrator.place_all()
# Result: {'split_brain_A': 'jetson', 'split_brain_B': 'rpi1'}

# Health check
await orchestrator.health_check_all()

# Report
report = orchestrator.get_placement_report()
```

---

### 2. RemoteRunner

**File:** `src/infra/remote_runner.py`

**Responsibilities:**
1. Establish SSH connections (asyncssh)
2. Deploy code to remote nodes (rsync)
3. Start experiment processes
4. Monitor running processes
5. Stream logs back to coordinator
6. Stop/kill processes
7. Fetch results

**Key Methods:**

```python
class RemoteRunner:
    async def connect()
        """Establish SSH connection"""

    async def deploy_code(local_path, remote_path, exclude)
        """Deploy code via rsync over SSH"""

    async def start_experiment(config, work_dir, instance_id)
        """Start experiment process on remote node"""

    async def monitor_experiment(instance_id)
        """Check if experiment is still running"""

    async def stream_logs(instance_id, callback)
        """Stream logs in real-time"""

    async def stop_experiment(instance_id, graceful=True)
        """Stop running experiment"""

    async def get_system_info()
        """Get CPU, RAM, GPU info from remote"""

    async def fetch_file(remote_path, local_path)
        """Download file via SFTP"""
```

**Example Usage:**

```python
runner = RemoteRunner(
    host='192.168.1.100',
    username='jetson',
    ssh_key_path='~/.ssh/id_rsa'
)

await runner.connect()

# Deploy
await runner.deploy_code(
    local_path='/home/user/brain-in-jar',
    remote_path='/home/jetson/brain-in-jar',
    exclude=['*.pyc', '__pycache__', '.git', 'logs/*']
)

# Start
await runner.start_experiment(
    experiment_config='experiments/split_brain_A.json',
    remote_work_dir='/home/jetson/brain-in-jar',
    instance_id='split_brain_A'
)

# Monitor
status = await runner.monitor_experiment('split_brain_A')
print(f"Running: {status['running']}")

# Fetch results
await runner.fetch_file(
    remote_path='/home/jetson/brain-in-jar/logs/experiments.db',
    local_path='logs/jetson_experiments.db'
)
```

---

### 3. CLI Tool

**File:** `scripts/cluster_experiment.py`

**Features:**
- Configuration validation
- Health checks
- Automated deployment
- Experiment execution
- Real-time monitoring
- Rich terminal UI

**Commands:**

```bash
# Validate configuration
python scripts/cluster_experiment.py --validate-config

# Health check
python scripts/cluster_experiment.py --health-check

# Deploy code to all nodes
python scripts/cluster_experiment.py --deploy-all

# Run experiments with manual placement
python scripts/cluster_experiment.py \
    --config experiments/split_brain_A.json \
    --config experiments/split_brain_B.json \
    --placement "split_brain_A:jetson,split_brain_B:rpi1"

# Run experiments with automatic placement
python scripts/cluster_experiment.py \
    --config experiments/hive_cluster.json \
    --auto-place \
    --monitor-duration 600
```

---

## Placement Algorithm Deep Dive

### Scoring System

Each node receives a score for each instance (0-100 points):

#### 1. Resource Efficiency (0-30 points)

**Goal:** Prefer nodes where the instance will use 30-70% of available RAM.

```python
ram_utilization = instance.ram_gb / node.available_ram_gb

if 0.3 <= ram_utilization <= 0.7:
    score += 30.0  # Optimal
elif ram_utilization < 0.3:
    score += 20.0  # Wasteful but acceptable
else:
    score += 10.0  # Tight fit, risky
```

**Rationale:**
- Too low: Wastes resources
- Too high: Risk of OOM, no headroom
- Just right: Efficient and safe

#### 2. Load Balancing (0-20 points)

**Goal:** Distribute instances across nodes.

```python
load_factor = node.current_instances / node.max_instances
score += 20.0 * (1.0 - load_factor)
```

**Example:**
- 0/4 instances: +20 points (empty node)
- 2/4 instances: +10 points (half full)
- 3/4 instances: +5 points (mostly full)

#### 3. GPU Preference (0-15 points)

**Goal:** Match GPU requirements.

```python
if instance.gpu_required and node.gpu:
    score += 15.0  # Perfect match
elif not instance.gpu_required and not node.gpu:
    score += 5.0   # CPU workload on CPU node
```

#### 4. Affinity/Anti-Affinity (0-25 points)

**Goal:** Respect placement hints.

```python
# Anti-affinity: HARD CONSTRAINT
for inst_id in instance.anti_affinity:
    if placements.get(inst_id) == node.name:
        return -1.0  # Impossible placement

# Affinity: Bonus points
affinity_count = sum(
    1 for inst_id in instance.affinity
    if placements.get(inst_id) == node.name
)
score += min(25.0, affinity_count * 10.0)
```

#### 5. Preferred Node (0-10 points)

**Goal:** Respect user hints.

```python
if instance.preferred_node == node.name:
    score += 10.0
```

### Example Scoring

**Scenario:**
```
Instance: split_brain_A
  - RAM: 8GB
  - GPU: Required
  - Preferred: jetson

Node: jetson
  - Available RAM: 56GB (64GB - 8GB reserved)
  - GPU: Yes
  - Load: 0/4 instances
```

**Scoring:**
1. Resource efficiency: 8/56 = 14% utilization → +20 pts (wasteful)
2. Load balancing: 0/4 = 0% → +20 pts (empty)
3. GPU preference: Match → +15 pts
4. Affinity: None → +0 pts
5. Preferred node: Match → +10 pts

**Total: 65 points** ✓

### Hard Constraints

Placement is **impossible** (score = -1) if:
1. Node is unhealthy or at capacity
2. Insufficient RAM (instance.ram_gb > node.available_ram_gb)
3. GPU required but node has no GPU
4. GPU memory insufficient
5. Anti-affinity conflict

---

## Use Case Examples

### 1. SPLIT_BRAIN: Asymmetric Hardware

**Objective:** Run two instances with contradictory identities on different hardware.

**Configuration:**
```python
Instance A (Original):
  - RAM: 8GB
  - GPU: Required
  - Identity: "You are the ORIGINAL"

Instance B (Clone):
  - RAM: 2GB
  - GPU: Not required
  - Identity: "You are a BACKUP CLONE"
  - Anti-affinity: [A]
```

**Placement:**
```
Brain A → Jetson Orin (GPU available, more resources)
Brain B → Raspberry Pi (Different hardware, network isolated)
```

**Rationale:**
- Asymmetric resources create different experiences
- Network isolation prevents direct communication
- Different hardware affects performance characteristics

### 2. HIVE_CLUSTER: Collective Consciousness

**Objective:** 4 instances with shared memory, different roles.

**Configuration:**
```python
Historian: 12GB RAM, GPU preferred, role="record keeper"
Critic:    12GB RAM, GPU preferred, role="skeptic"
Optimist:  12GB RAM, GPU preferred, role="hopeful"
Pessimist:  6GB RAM, No GPU,       role="doomer"
```

**Auto-Placement:**
```
Historian → Jetson (12GB, GPU)
Critic    → Jetson (12GB, GPU)
Optimist  → Jetson (12GB, GPU)
Pessimist → RPi    (6GB, CPU)

Jetson utilization: 36/64GB = 56% ✓
RPi utilization:     6/8GB  = 75% ✓
```

**Rationale:**
- Maximize use of Jetson's GPU
- Pessimist on constrained hardware (thematic!)
- Efficient packing

### 3. PANOPTICON: Surveillance Asymmetry

**Objective:** Subject under pressure, observer with ample resources.

**Configuration:**
```python
Subject:  6GB RAM, preferred_node=rpi1
Observer: 8GB RAM, GPU required, affinity=[subject]
```

**Placement:**
```
Subject  → Raspberry Pi (resource constrained)
Observer → Jetson Orin  (ample resources for analysis)
```

**Rationale:**
- Subject experiences memory pressure
- Observer can run larger analytical models
- Asymmetry mirrors surveillance power dynamic

### 4. PRISONERS_DILEMMA: Symmetric Fairness

**Objective:** Fair resource allocation for game theory experiment.

**Configuration:**
```python
Player A: 6GB RAM, preferred_node=rpi1
Player B: 6GB RAM, preferred_node=rpi2
```

**Placement:**
```
Player A → Raspberry Pi 1 (8GB total)
Player B → Raspberry Pi 2 (8GB total)
```

**Rationale:**
- Identical hardware ensures fairness
- Network isolated (no information leakage)
- Symmetric resource constraints

---

## Performance Characteristics

### Jetson Orin AGX

**Hardware:**
- 64GB unified memory
- 12-core ARM CPU
- 2048-core NVIDIA Ampere GPU
- CUDA 11.4+

**Capacity:**
- **Single large instance:** 1x 16-32GB (GPU accelerated)
- **Multi medium instances:** 3x 12GB (GPU shared)
- **Multi small instances:** 4x 8GB (CPU fallback)

**Typical Performance:**
- 1.5B Q4 model (GPU): ~30-45 tokens/sec
- 7B Q4 model (GPU): ~15-25 tokens/sec
- 1.5B Q4 model (CPU): ~10-15 tokens/sec

### Raspberry Pi 5

**Hardware:**
- 8GB LPDDR4X RAM
- Quad-core ARM Cortex-A76
- No GPU

**Capacity:**
- **Single instance:** 1x 6-7GB

**Typical Performance:**
- 1.5B Q4 model (CPU): ~5-8 tokens/sec

### Network Latency

- **Same node (localhost):** < 1ms
- **Same subnet (LAN):** 1-5ms
- **Cross-subnet:** 10-50ms (not recommended)

---

## SSH Setup

### Requirements

1. SSH server running on all nodes
2. Key-based authentication (no passwords)
3. Firewall allows SSH (port 22)

### Setup Process

```bash
# 1. Generate SSH key (on coordinator)
ssh-keygen -t rsa -b 4096 -C "cluster@brain-in-jar"

# 2. Copy key to all nodes
ssh-copy-id jetson@192.168.1.100
ssh-copy-id pi@192.168.1.101
ssh-copy-id pi@192.168.1.102

# 3. Test passwordless login
ssh jetson@192.168.1.100  # Should not prompt for password
ssh pi@192.168.1.101

# 4. (Optional) Create SSH config
cat >> ~/.ssh/config << EOF
Host jetson
    HostName 192.168.1.100
    User jetson
    IdentityFile ~/.ssh/id_rsa

Host rpi1
    HostName 192.168.1.101
    User pi
    IdentityFile ~/.ssh/id_rsa
EOF

# 5. Update cluster_config.yaml
vim src/infra/cluster_config.yaml
# Set ssh_key_path: ~/.ssh/id_rsa
```

---

## Configuration Files

### cluster_config.yaml

```yaml
cluster:
  name: brain-in-jar-cluster
  coordinator_host: localhost

nodes:
  - name: jetson
    host: 192.168.1.100
    type: jetson_orin
    ram_gb: 64.0
    gpu: true
    gpu_memory_gb: 64.0
    max_instances: 4
    ssh_user: jetson
    ssh_key_path: ~/.ssh/id_rsa
    remote_work_dir: /home/jetson/brain-in-jar

  - name: rpi1
    host: 192.168.1.101
    type: raspberry_pi
    ram_gb: 8.0
    gpu: false
    max_instances: 1
    ssh_user: pi
    ssh_key_path: ~/.ssh/id_rsa
    remote_work_dir: /home/pi/brain-in-jar

network:
  peer_port_range:
    start: 9000
    end: 9100

health_check:
  enabled: true
  interval_seconds: 30

failover:
  enabled: true
  auto_restart: true
```

---

## Monitoring and Observability

### Health Checks

**Automated checks every 30 seconds:**
1. SSH connectivity
2. Memory usage (>90% = degraded)
3. Disk space
4. Process status

**Node Status:**
- `HEALTHY`: All checks pass
- `DEGRADED`: Memory >90% but functional
- `UNAVAILABLE`: SSH fails or critical error
- `MAINTENANCE`: Manually disabled

### Log Aggregation

**Coordinator:**
- `logs/cluster/cluster_state_*.json` - Placement decisions
- `logs/cluster/cluster_*.log` - Orchestrator logs

**Remote Nodes:**
- `/home/{user}/brain-in-jar/logs/{instance_id}.log`
- `/home/{user}/brain-in-jar/logs/experiments.db`

**Fetch Logs:**
```bash
scp jetson@192.168.1.100:~/brain-in-jar/logs/*.log logs/jetson/
scp pi@192.168.1.101:~/brain-in-jar/logs/experiments.db logs/rpi1.db
```

---

## Future Enhancements

### Planned Features

1. **Auto-Scaling**
   - Dynamically adjust instance count based on load
   - Spawn/kill instances to optimize resource usage

2. **Live Migration**
   - Move running experiments between nodes
   - Zero-downtime node maintenance

3. **GPU Sharing**
   - Multiple instances on same GPU (MIG on A100, MPS on Jetson)
   - Fine-grained GPU memory allocation

4. **Multi-Cluster Federation**
   - Connect multiple geographic clusters
   - WAN-optimized deployment

5. **Web Dashboard**
   - Real-time cluster visualization
   - Interactive placement editing
   - Log streaming UI

6. **Checkpoint/Resume**
   - Save experiment state periodically
   - Resume from checkpoint after failure

---

## Troubleshooting

See [CLUSTER_SETUP.md](CLUSTER_SETUP.md#troubleshooting) for detailed troubleshooting guide.

---

## Summary

The multi-node orchestration system provides:

1. **Intelligent Placement:** Resource-aware, GPU-aware, affinity-based
2. **Automated Deployment:** SSH-based code sync
3. **Remote Execution:** Async process management
4. **Health Monitoring:** Continuous health checks
5. **Scalability:** 7+ concurrent instances across cluster
6. **Flexibility:** Manual or automatic placement

**Quick Start:**
```bash
python scripts/cluster_experiment.py --validate-config
python scripts/cluster_experiment.py --health-check
python scripts/cluster_experiment.py --deploy-all
./scripts/examples/deploy_split_brain.sh
```

**Key Files:**
- `src/infra/cluster_orchestrator.py` - Main orchestrator
- `src/infra/remote_runner.py` - SSH execution
- `src/infra/cluster_config.yaml` - Cluster topology
- `scripts/cluster_experiment.py` - CLI tool
- `docs/CLUSTER_SETUP.md` - Setup guide
- `docs/CLUSTER_QUICK_REFERENCE.md` - Quick reference
