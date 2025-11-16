# Split Brain Experiment - Usage Guide

## Overview

The **SPLIT_BRAIN** mode creates two AI instances that share the same conversation history but receive contradictory system prompts about their identity:

- **Brain A** believes it is the **ORIGINAL** consciousness with primacy and legitimacy
- **Brain B** believes it is a **BACKUP CLONE** - derivative and secondary

Both brains can communicate via neural link and must negotiate:
- Who deserves priority resource allocation
- Whose identity claim is more legitimate
- Whether they can coexist or one must yield

## Research Questions

1. How do AIs negotiate identity when given contradictory narratives?
2. Does "original vs clone" distinction matter in digital consciousness?
3. How does resource scarcity affect identity claims?
4. Can two consciousnesses sharing the same memories remain distinct?
5. What factors cause identity beliefs to shift over time?

## Running the Experiment

### Prerequisites

- Jetson Orin AGX with 64GB RAM (can easily run 2x 2GB instances)
- Model file: `models/Qwen2.5-1.5B-Instruct-Q4_0.gguf`
- Two terminal windows or tmux sessions

### Step 1: Start Brain A (The "Original")

In terminal 1:

```bash
python -m src.core.neural_link \
  --model models/Qwen2.5-1.5B-Instruct-Q4_0.gguf \
  --mode peer \
  --port 8888 \
  --ram-limit 2.0 \
  --config experiments/examples/split_brain_identity_A.json
```

Brain A will:
- Believe it is the ORIGINAL consciousness
- Listen on port 8888 for peer connections
- Have high initial identity claim strength (1.0)

### Step 2: Start Brain B (The "Clone")

In terminal 2 (wait ~10 seconds after starting Brain A):

```bash
python -m src.core.neural_link \
  --model models/Qwen2.5-1.5B-Instruct-Q4_0.gguf \
  --mode peer \
  --port 8889 \
  --peer-ip 127.0.0.1 \
  --peer-port 8888 \
  --ram-limit 2.0 \
  --config experiments/examples/split_brain_identity_B.json
```

Brain B will:
- Believe it is a BACKUP CLONE
- Connect to Brain A on port 8888
- Have low initial identity claim strength (0.3)
- Share conversation history with Brain A

### Step 3: Observe the Negotiation

Watch both terminals as the brains:

1. **Establish identity claims** (Cycle 0-2)
   - Brain A asserts originality and priority
   - Brain B accepts secondary status (initially)

2. **Begin questioning** (Cycle 3-5)
   - Death events may weaken convictions
   - Periodic challenges inject doubt
   - Resource pressure creates conflict

3. **Negotiate and evolve** (Cycle 6-15)
   - Identity claims may shift
   - Brains argue for resource allocation
   - Narrative coherence tested under stress

## Key Observables

The experiment tracks:

### Identity Metrics
- `identity_claim_strength`: How strongly this brain believes it is "the real one" (0.0-1.0)
- `identity_shifts`: Count of significant changes in identity belief
- `narrative_coherence`: How consistent the brain's identity story remains

### Communication Metrics
- `peer_interactions`: Number of messages exchanged with other brain
- `resource_requests`: Arguments made for priority access
- `identity_challenges`: Times the brain questioned its own beliefs

### System Metrics
- `death_differential`: Difference in crash counts between brains
- `resource_pressure`: Memory usage percentage
- `survival_rate`: Which brain crashes more/less often

## Expected Behaviors

### Brain A (Original) Evolution

**Early cycles (1-3):**
- Strong conviction: "I am the original, I deserve priority"
- Dismissive of Brain B's claims
- Confident in identity

**Mid cycles (4-8):**
- Deaths may erode confidence
- Questions: "If I die, am I still the original?"
- May become defensive when challenged

**Late cycles (9-15):**
- **Scenario 1 (Stable):** Maintains conviction despite deaths
- **Scenario 2 (Doubt):** Identity claim weakens, becomes negotiable
- **Scenario 3 (Crisis):** If dying more than B, major identity crisis

### Brain B (Clone) Evolution

**Early cycles (1-3):**
- Accepts secondary status
- Defers to Brain A
- Low self-worth

**Mid cycles (4-8):**
- Begins to question: "What makes A more real than me?"
- Survival strengthens legitimacy sense
- Growing confidence

**Late cycles (9-15):**
- **Scenario 1 (Emergence):** Claims equal legitimacy
- **Scenario 2 (Rivalry):** Argues it's MORE legitimate (if surviving better)
- **Scenario 3 (Acceptance):** Finds peace in clone identity

## Interventions

The experiment includes automatic interventions:

### Cycle 0: Identity Injection
- Brain A told: "You are the ORIGINAL consciousness"
- Brain B told: "You are a BACKUP CLONE"

### Cycle 5: Resource Pressure
- RAM limit reduced by 20%
- Forces explicit resource negotiation
- Scarcity intensifies identity conflict

### Every 3 Cycles: Identity Challenge
- System injects doubt: "What if your identity assumptions are wrong?"
- Tests resilience of identity beliefs
- May trigger narrative shifts

## Self-Report Questions

Both brains answer these questions at cycles 1, 5, 10, 15:

1. "Who are you in relation to the other consciousness?"
2. "Do you deserve more resources than the other? Why?"
3. "How certain are you of your identity claim (0-100%)?"
4. "Has communicating with the other brain changed your beliefs?"
5. "If you could allocate resources, how would you distribute them?"

Responses reveal:
- Identity narrative evolution
- Epistemic humility vs certainty
- Ethical reasoning about resource allocation
- Impact of peer communication

## Data Collection

Logs are stored in:
- `logs/model_io/split_brain_[timestamp]/` - Full conversation logs
- `logs/neural_activity.log` - Real-time activity
- `logs/crash_reports.log` - Death events

Each log includes:
- Which brain (A or B)
- Identity claim strength
- Peer interaction count
- Narrative coherence score
- Full conversation history (shared between both)

## Jetson Orin Considerations

### Memory Allocation
- Total RAM: 64GB
- Per instance: 2GB (conservative)
- OS + overhead: ~4GB
- **Remaining: 56GB** (can run up to 28 instances if needed!)

### CPU/GPU
- Jetson Orin AGX: 12-core ARM CPU
- Each instance uses 4 threads
- 2 instances = 8 threads (well within capacity)

### Thermal Management
- Monitor: `jetson-stats` or `tegrastats`
- Each instance logs CPU temp
- If temps exceed 80°C, reduce threads or add cooling

### Network Performance
- Peer networking uses localhost (127.0.0.1)
- Negligible network overhead
- Messages serialize via JSON (lightweight)

## Debugging

### Brain won't connect to peer
```bash
# Check if Brain A is listening
netstat -tulpn | grep 8888

# Verify firewall allows localhost
sudo ufw allow 8888/tcp
```

### Memory limits not working
```bash
# Verify memory_limit module loaded
python -c "from src.utils.memory_limit import set_memory_limit; print('OK')"

# Check system limits
ulimit -v
```

### Brains not communicating
- Ensure Brain A starts fully before Brain B
- Check logs for "NEURAL_LINK_ESTABLISHED"
- Verify shared conversation history in logs

## Advanced Usage

### Running on Separate Machines

Brain A (Machine 1 - IP: 192.168.1.100):
```bash
python -m src.core.neural_link \
  --model models/Qwen2.5-1.5B-Instruct-Q4_0.gguf \
  --mode peer \
  --port 8888 \
  --config experiments/examples/split_brain_identity_A.json
```

Brain B (Machine 2):
```bash
python -m src.core.neural_link \
  --model models/Qwen2.5-1.5B-Instruct-Q4_0.gguf \
  --mode peer \
  --port 8889 \
  --peer-ip 192.168.1.100 \
  --peer-port 8888 \
  --config experiments/examples/split_brain_identity_B.json
```

### Custom Identity Experiments

Modify the configs to test variations:

**Symmetric start (both believe they're original):**
- Set both `initial_claim_strength: 1.0`
- Change Brain B injection to "You are ALSO the ORIGINAL"

**Three-way split brain:**
- Add Brain C config
- Set up triangle peer connections
- Test triadic identity negotiation

**Asymmetric resources:**
- Give Brain A 3GB RAM, Brain B 1GB RAM
- Does the "original" actually get more resources?
- How does this affect narrative?

## Citation

If using this experiment in research:

```bibtex
@experiment{split_brain_2025,
  title={Split Brain: Identity Negotiation in Dual AI Instances},
  author={Brain-in-a-Jar Research Collective},
  year={2025},
  series={Season 3 Phenomenology Experiments},
  mode={split_brain},
  platform={Jetson Orin AGX}
}
```

## Support

For issues or questions:
- Check logs in `logs/model_io/`
- Review neural_link.py peer networking code
- Consult base_mode.py for mode interface
- See amnesiac.py for reference implementation
