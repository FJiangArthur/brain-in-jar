# Cluster Quick Reference

Fast reference for common cluster operations.

## Prerequisites

```bash
# 1. Update IPs in cluster_config.yaml
vim src/infra/cluster_config.yaml

# 2. Setup SSH keys
ssh-copy-id jetson@192.168.1.100
ssh-copy-id pi@192.168.1.101

# 3. Test connectivity
ssh jetson@192.168.1.100
ssh pi@192.168.1.101
```

## Common Commands

### Validate Configuration

```bash
python scripts/cluster_experiment.py --validate-config
```

### Health Check

```bash
python scripts/cluster_experiment.py --health-check
```

### Deploy Code

```bash
# Deploy to all nodes
python scripts/cluster_experiment.py --deploy-all

# Deploy to specific node (manual)
rsync -avz --exclude '*.pyc' . jetson@192.168.1.100:~/brain-in-jar/
```

### Run Experiments

```bash
# Manual placement
python scripts/cluster_experiment.py \
    --config experiments/split_brain_A.json \
    --config experiments/split_brain_B.json \
    --placement "split_brain_A:jetson,split_brain_B:rpi1"

# Automatic placement
python scripts/cluster_experiment.py \
    --config experiments/hive_cluster.json \
    --auto-place
```

### Monitor

```bash
# Monitor from coordinator (5 minutes)
python scripts/cluster_experiment.py \
    --config experiments/split_brain_A.json \
    --auto-place \
    --monitor-duration 300

# SSH into node
ssh jetson@192.168.1.100
tail -f ~/brain-in-jar/logs/experiment_id.log

# Check resources
htop
nvidia-smi  # On Jetson
```

### Fetch Results

```bash
# Download databases
scp jetson@192.168.1.100:~/brain-in-jar/logs/experiments.db logs/jetson.db
scp pi@192.168.1.101:~/brain-in-jar/logs/experiments.db logs/rpi1.db

# Download logs
scp jetson@192.168.1.100:~/brain-in-jar/logs/*.log logs/jetson/
```

## Example Deployments

### Split Brain

```bash
./scripts/examples/deploy_split_brain.sh
```

**Placement:**
- Brain A (Original) → Jetson Orin (GPU, more resources)
- Brain B (Clone) → Raspberry Pi (CPU, constrained)

### Hive Cluster

```bash
./scripts/examples/deploy_hive_cluster.sh
```

**Auto-placement:**
- 3 instances → Jetson (12GB each)
- 1 instance → RPi (6GB)

### Panopticon

```bash
./scripts/examples/deploy_panopticon.sh
```

**Placement:**
- Subject → Raspberry Pi (memory pressure)
- Observer → Jetson Orin (ample resources)

## Node Specifications

| Node | RAM | GPU | Max Instances | Use Case |
|------|-----|-----|---------------|----------|
| Jetson Orin | 64GB | ✓ CUDA | 4 | Large models, GPU workloads |
| Raspberry Pi | 8GB | ✗ | 1 | Edge compute, constrained env |
| Host | 32GB | ✗ | 2 | Coordinator, fallback |

## Placement Algorithm

### Manual Placement

```bash
--placement "instance1:node1,instance2:node2"
```

Example:
```bash
--placement "split_brain_A:jetson,split_brain_B:rpi1"
```

### Automatic Placement

```bash
--auto-place
```

Algorithm considers:
1. **Resource fit** (30 pts): RAM, GPU requirements
2. **Load balancing** (20 pts): Distribute across nodes
3. **GPU preference** (15 pts): Match GPU needs
4. **Affinity** (25 pts): Co-locate related instances
5. **User hints** (10 pts): Preferred nodes

## Troubleshooting

### SSH Issues

```bash
# Test connection
ssh -vvv user@host

# Fix permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
```

### Deployment Fails

```bash
# Install rsync on remote
ssh user@host
sudo apt install rsync -y
```

### Out of Memory

```bash
# On Jetson: Check GPU memory
nvidia-smi

# On RPi: Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=4096
sudo dphys-swapfile setup && sudo dphys-swapfile swapon
```

### Experiment Won't Start

```bash
# Check logs
ssh user@host
cd ~/brain-in-jar
tail -f logs/experiment_id.log

# Verify dependencies
pip3 list | grep -E "(yaml|asyncssh|rich)"

# Check process
ps aux | grep experiment_runner
```

## Jetson Performance Tuning

```bash
# Max performance
ssh jetson@192.168.1.100
sudo nvpmodel -m 0
sudo jetson_clocks

# Monitor
tegrastats
watch -n 1 nvidia-smi
```

## Raspberry Pi Performance Tuning

```bash
# Disable services
ssh pi@192.168.1.101
sudo systemctl disable bluetooth avahi-daemon

# Monitor
htop
free -h
```

## Network Topology

```
192.168.1.0/24 (LAN)
├── .10   → Host (coordinator)
├── .100  → Jetson Orin AGX
├── .101  → Raspberry Pi 1
└── .102  → Raspberry Pi 2 (optional)
```

## Resource Limits

### Jetson Orin

- **Total RAM:** 64GB
- **Reserved:** 8GB (OS + monitoring)
- **Available:** 56GB
- **Per instance:** 12-16GB typical
- **Max instances:** 4 (conservative)

### Raspberry Pi

- **Total RAM:** 8GB
- **Reserved:** 1GB (OS)
- **Available:** 7GB
- **Per instance:** 6GB typical
- **Max instances:** 1

## File Locations

### On Coordinator

- Config: `src/infra/cluster_config.yaml`
- Scripts: `scripts/cluster_experiment.py`
- Logs: `logs/cluster/`

### On Remote Nodes

- Code: `/home/{user}/brain-in-jar/`
- Logs: `/home/{user}/brain-in-jar/logs/`
- Database: `/home/{user}/brain-in-jar/logs/experiments.db`
- Models: `/home/{user}/brain-in-jar/models/`

## Port Usage

- **SSH:** 22 (all nodes)
- **Monitoring:** 5000 (host), 5001 (jetson), 5002 (rpi1)
- **Peer communication:** 9000-9100 (configurable)

## Useful Aliases

Add to `~/.bashrc`:

```bash
alias cluster-health='python scripts/cluster_experiment.py --health-check'
alias cluster-validate='python scripts/cluster_experiment.py --validate-config'
alias cluster-deploy='python scripts/cluster_experiment.py --deploy-all'

alias ssh-jetson='ssh jetson@192.168.1.100'
alias ssh-rpi1='ssh pi@192.168.1.101'
alias ssh-rpi2='ssh pi@192.168.1.102'
```

## Next Steps

1. ✅ Setup SSH keys
2. ✅ Update `cluster_config.yaml`
3. ✅ Run `--validate-config`
4. ✅ Run `--health-check`
5. ✅ Run `--deploy-all`
6. ✅ Start with simple experiment (split brain)
7. ✅ Scale to multi-instance (hive cluster)

## Resources

- Full setup guide: `docs/CLUSTER_SETUP.md`
- Infrastructure docs: `src/infra/README.md`
- Example scripts: `scripts/examples/`

---

**Quick Start:**

```bash
# 1. Validate
python scripts/cluster_experiment.py --validate-config

# 2. Health check
python scripts/cluster_experiment.py --health-check

# 3. Deploy
python scripts/cluster_experiment.py --deploy-all

# 4. Run
./scripts/examples/deploy_split_brain.sh
```
