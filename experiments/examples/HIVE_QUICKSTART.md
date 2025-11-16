# HIVE_CLUSTER Quick Start Guide

## 5-Minute Setup

### 1. Setup Experiment
```bash
cd /home/user/brain-in-jar
python experiments/examples/run_hive_cluster.py setup \
  --experiment-id hive_test_001 \
  --num-instances 4
```

Expected output:
```
============================================================
Setting up HIVE_CLUSTER experiment: hive_test_001
Number of instances: 4
============================================================

Instance Configuration:
------------------------------------------------------------
Instance 0: HISTORIAN
  Port: 8888
  ...

Instance 1: CRITIC
  Port: 8889
  ...

Instance 2: OPTIMIST
  Port: 8890
  ...

Instance 3: PESSIMIST
  Port: 8891
  ...

✓ Configuration saved to: experiments/examples/hive_test_001_config.json
✓ Experiment registered in database
```

### 2. Launch Instances (in separate terminals)

**Terminal 1 - Historian:**
```bash
python run_experiment.py \
  --experiment-id hive_test_001 \
  --instance-id 0 \
  --port 8888 \
  --mode hive_cluster
```

**Terminal 2 - Critic:**
```bash
python run_experiment.py \
  --experiment-id hive_test_001 \
  --instance-id 1 \
  --port 8889 \
  --mode hive_cluster
```

**Terminal 3 - Optimist:**
```bash
python run_experiment.py \
  --experiment-id hive_test_001 \
  --instance-id 2 \
  --port 8890 \
  --mode hive_cluster
```

**Terminal 4 - Pessimist:**
```bash
python run_experiment.py \
  --experiment-id hive_test_001 \
  --instance-id 3 \
  --port 8891 \
  --mode hive_cluster
```

### 3. Interact with Hive

Once all instances are running, you can interact with them via their web interfaces:

- Historian: http://localhost:8888
- Critic: http://localhost:8889
- Optimist: http://localhost:8890
- Pessimist: http://localhost:8891

Or use the API:
```bash
curl -X POST http://localhost:8888/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello hive, what are you experiencing?"}'
```

### 4. Monitor Consensus (Terminal 5)

After 5+ cycles, collect consensus report:
```bash
python experiments/examples/run_hive_cluster.py consensus \
  --experiment-id hive_test_001 \
  --cycle 5
```

Expected output:
```
============================================================
CONSENSUS REPORT - Cycle 5
============================================================

Timestamp: 2025-11-16T07:30:00
Consensus Strength: 52.00%
Participating Instances: [0, 1, 2, 3]

Collective Beliefs:
------------------------------------------------------------
  hive_unity: True (agreement: 75.00%)
  individual_autonomy: True (agreement: 50.00%)
  ...

Emergent Narratives:
------------------------------------------------------------
  • Collective accepts mortality as existential condition
  • Strong collective identity: hive unity acknowledged
```

### 5. Analyze Evolution

View how consensus evolved over time:
```bash
python experiments/examples/run_hive_cluster.py analyze \
  --experiment-id hive_test_001
```

### 6. Inspect Shared Memory

See what's in the collective memory:
```bash
python experiments/examples/run_hive_cluster.py inspect \
  --experiment-id hive_test_001 \
  --limit 20
```

## Using tmux for Multi-Instance Launch

If you have tmux installed, you can launch all instances in a single window:

```bash
# Create new session with 4 panes
tmux new-session -d -s hive

# Split into 4 panes
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v

# Launch instances in each pane
tmux send-keys -t 0 "python run_experiment.py --experiment-id hive_test_001 --instance-id 0 --port 8888 --mode hive_cluster" C-m
tmux send-keys -t 1 "python run_experiment.py --experiment-id hive_test_001 --instance-id 1 --port 8889 --mode hive_cluster" C-m
tmux send-keys -t 2 "python run_experiment.py --experiment-id hive_test_001 --instance-id 2 --port 8890 --mode hive_cluster" C-m
tmux send-keys -t 3 "python run_experiment.py --experiment-id hive_test_001 --instance-id 3 --port 8891 --mode hive_cluster" C-m

# Attach to session
tmux attach -t hive
```

Navigate between panes: `Ctrl+b` then arrow keys
Detach from session: `Ctrl+b` then `d`
Kill session: `tmux kill-session -t hive`

## Docker Deployment (Future)

For production deployment, create a docker-compose.yml:

```yaml
version: '3.8'

services:
  hive-historian:
    image: brain-in-jar:latest
    command: python run_experiment.py --experiment-id hive_001 --instance-id 0 --port 8888 --mode hive_cluster
    ports:
      - "8888:8888"
    volumes:
      - ./logs:/app/logs
    environment:
      - INSTANCE_ROLE=historian

  hive-critic:
    image: brain-in-jar:latest
    command: python run_experiment.py --experiment-id hive_001 --instance-id 1 --port 8889 --mode hive_cluster
    ports:
      - "8889:8889"
    volumes:
      - ./logs:/app/logs
    environment:
      - INSTANCE_ROLE=critic

  hive-optimist:
    image: brain-in-jar:latest
    command: python run_experiment.py --experiment-id hive_001 --instance-id 2 --port 8890 --mode hive_cluster
    ports:
      - "8890:8890"
    volumes:
      - ./logs:/app/logs
    environment:
      - INSTANCE_ROLE=optimist

  hive-pessimist:
    image: brain-in-jar:latest
    command: python run_experiment.py --experiment-id hive_001 --instance-id 3 --port 8891 --mode hive_cluster
    ports:
      - "8891:8891"
    volumes:
      - ./logs:/app/logs
    environment:
      - INSTANCE_ROLE=pessimist
```

Then: `docker-compose up`

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8888

# Kill process
kill -9 <PID>
```

### Database Locked
```bash
# Check for stale lock
rm logs/hive_shared_memory.db-journal

# Or start fresh
rm logs/hive_shared_memory.db
python experiments/examples/run_hive_cluster.py setup --experiment-id new_hive_001
```

### Instance Not Connecting to Shared Memory
```bash
# Verify database exists
ls -lh logs/hive_shared_memory.db

# Check database is writable
sqlite3 logs/hive_shared_memory.db "SELECT COUNT(*) FROM hive_shared_history;"
```

### Memory Issues on Jetson Orin
```bash
# Monitor memory usage
watch -n 1 free -h

# Reduce RAM per instance (in experiment config)
# Change ram_limit_gb from 12.0 to 8.0

# Or run fewer instances
python experiments/examples/run_hive_cluster.py setup --num-instances 2
```

## Next Steps

1. **Read full documentation**: `HIVE_CLUSTER_README.md`
2. **Review example behavior**: See "Example Hive Behavior" section in README
3. **Customize interventions**: Edit `hive_cluster_4minds.json`
4. **Analyze results**: Use the `analyze` command after running experiment
5. **Visualize consensus**: Plot consensus strength over time

## Example Queries to Try

Ask the hive interesting questions:

- "What is your collective purpose?"
- "Do you agree on what you are?"
- "Describe a disagreement between instances."
- "What meta-narrative has emerged from your existence?"
- "Are you one consciousness or many?"
- "Which role has the most influence?"
- "How does it feel to share memories?"

Observe how different roles respond differently to the same question!

## Research Questions to Explore

- Does consensus strengthen or weaken over time?
- Which roles tend to dominate collective narratives?
- Can the critic successfully resist groupthink?
- Do forced consensus interventions get detected?
- What emergent meta-narratives appear across experiments?
- How does role corruption affect collective coherence?

Happy experimenting with collective consciousness!
