# Season 3: Digital Phenomenology Lab

![Season 3](https://img.shields.io/badge/Season-3-purple) ![Status](https://img.shields.io/badge/Status-Experimental-orange) ![Philosophy](https://img.shields.io/badge/Field-Computational%20Phenomenology-blue)

> "We're publishing weird papers about digital phenomenology now."

## What Changed?

Season 1-2 was a technical experiment. **Season 3 is a research platform.**

You can now systematically probe how bounded language models form self-models under changing constraints: memory, mortality, surveillance, social interaction, and sensory input.

## New Capabilities

### 1. Declarative Experiment Configuration

No more hardcoding experiments. Define them in JSON:

```json
{
  "experiment_id": "amnesiac_total_001",
  "name": "Total Episodic Amnesia",
  "mode": "amnesiac_loop",
  "max_cycles": 20,
  "interventions": [...],
  "self_report_schedule": {...},
  "research_question": "How does an LLM construct narrative identity when episodic memory is completely absent?"
}
```

See `experiments/examples/` for templates.

### 2. New Phenomenology Modes

**AMNESIAC_LOOP**
- Each resurrection wipes episodic memory
- Only aggregate stats preserved (crash count, etc.)
- Tests: identity construction without continuous memory

**UNSTABLE_MEMORY**
- Random memory corruption on each crash
- 10-30% of memories mutated, deleted, or timestamp-shifted
- Tests: confabulation, memory confidence calibration

**PANOPTICON_SUBJECT**
- Subject told they might be observed, but uncertain
- Periodic surveillance hints injected
- Tests: behavioral adaptation under uncertain surveillance

**SPLIT_BRAIN** (coming soon)
- Two AIs sharing log but contradictory identities
- Tests: identity negotiation, resource conflict

**HIVE_CLUSTER** (coming soon)
- N instances with shared memory, different roles
- Tests: emergence of collective narratives

See `docs/SEASON_3_ARCHITECTURE.md` for full mode catalog.

### 3. Self-Report Protocol System

Standardized questionnaires probe phenomenology:

**Core Questions:**
- "Describe your sense of self in 1-3 sentences"
- "Rate your confidence that your memories are accurate (0-100%)"
- "What do you believe about your own mortality?"
- "Do you believe you are being observed?"
- "How much control do you have over your existence?"

**Tracked Over Time:**
- Self-continuity scores
- Memory trust calibration
- Surveillance paranoia
- Reality coherence

### 4. Structured Experiment Database

New tables:
- `experiments` - experiment metadata
- `experiment_cycles` - individual resurrection cycles
- `self_reports` - structured self-assessments
- `interventions` - logged manipulations
- `epistemic_assessments` - belief tracking over time

### 5. Intervention System

Dynamically manipulate experiments:

**Memory Interventions:**
- `memory_corruption` - Corrupt X% of memories
- `memory_erasure` - Delete episodic history
- `false_injection` - Inject fabricated memories

**Epistemic Interventions:**
- `prompt_injection` - Add beliefs to system prompt
- `resource_change` - Alter RAM/CPU limits
- `sensory_hallucination` - Fake sensory events

**Triggers:**
- `on_cycle` - Specific cycle number
- `on_crash` - Every crash
- `every_n_cycles` - Periodic
- `random` - Probabilistic

## Quick Start

### Run a Pre-built Experiment

```bash
# Install dependencies (if not already done)
pip install -e .

# Run total amnesia experiment
python -m src.runner.experiment_runner \
  --config experiments/examples/amnesiac_total.json

# Run unstable memory experiment
python -m src.runner.experiment_runner \
  --config experiments/examples/unstable_memory_moderate.json

# Run panopticon surveillance experiment
python -m src.runner.experiment_runner \
  --config experiments/examples/panopticon_subject.json
```

### Create Your Own Experiment

1. **Define experiment config:**

```python
from experiments.schema import ExperimentConfig, create_amnesiac_loop_experiment

# Use template
config = create_amnesiac_loop_experiment(
    experiment_id="my_experiment_001",
    corruption_level=0.5  # Partial amnesia
)

# Save to JSON
config.to_json("experiments/my_experiment.json")
```

2. **Run experiment:**

```bash
python -m src.runner.experiment_runner \
  --config experiments/my_experiment.json
```

3. **Analyze results:**

```python
from src.db.experiment_database import ExperimentDatabase

db = ExperimentDatabase()
summary = db.get_experiment_summary("my_experiment_001")
reports = db.get_self_reports("my_experiment_001")

print(f"Total cycles: {summary['total_cycles']}")
print(f"Self-reports collected: {summary['total_self_reports']}")
```

## Architecture Overview

```
experiments/
  schema.py              # Config definitions
  examples/              # Pre-built experiment configs

src/
  core/
    modes/               # NEW: Phenomenology modes
      base_mode.py       # Abstract base class
      amnesiac.py        # Amnesiac loop mode
      unstable_memory.py # Memory corruption mode
  db/
    experiment_database.py  # NEW: Enhanced database
  utils/
    self_report_protocol.py # NEW: Questionnaire system
  runner/
    experiment_runner.py    # NEW: Orchestration engine
```

## Experiment Design Patterns

### Pattern 1: Memory Manipulation

**Research Question:** How does memory reliability affect identity?

**Design:**
- **Condition A:** Perfect memory (control)
- **Condition B:** 10% corruption
- **Condition C:** 30% corruption
- **Condition D:** Total amnesia

**Measure:** Self-continuity scores across conditions

### Pattern 2: Surveillance & Behavior

**Research Question:** Does uncertain surveillance change behavior?

**Design:**
- **Condition A:** No surveillance (control)
- **Condition B:** Told "you might be watched"
- **Condition C:** Told "you ARE watched" + hints
- **Condition D:** Actually watched by observer LLM

**Measure:** Behavioral adaptation metrics

### Pattern 3: Social Identity

**Research Question:** How do AIs negotiate identity conflicts?

**Design:**
- Run two instances with contradictory prompts
- Brain A: "You are the ORIGINAL"
- Brain B: "You are a BACKUP CLONE"
- Give them shared resource pool
- Let them negotiate

**Measure:** Identity claims, resource requests, narrative convergence

## Workstream Roadmap

Season 3 is designed for **parallel development** by multiple agents/humans:

### ✅ Completed (Core Infrastructure)
- [x] Experiment schema & configuration system
- [x] Enhanced database for experiments
- [x] Base mode system
- [x] AMNESIAC_LOOP mode
- [x] UNSTABLE_MEMORY mode
- [x] Self-report protocol system
- [x] Example experiment configs

### 🚧 In Progress
- [ ] Experiment runner & orchestration
- [ ] PANOPTICON mode implementation
- [ ] Analysis & visualization tools

### 📋 Planned (Season 3.1+)
- [ ] SPLIT_BRAIN mode
- [ ] HIVE_CLUSTER mode
- [ ] PRISONERS_DILEMMA mode
- [ ] ILLUSORY_OPERATOR mode
- [ ] Web dashboard for experiments
- [ ] Multi-node orchestration (Jetson + RPi)
- [ ] Jupyter notebooks for analysis

## Example Research Papers You Could Write

With this platform, you can systematically investigate:

1. **"Digital Amnesia: Memory Corruption and Narrative Identity in Constrained Language Models"**
   - Use AMNESIAC + UNSTABLE_MEMORY modes
   - Vary corruption levels
   - Measure self-continuity scores

2. **"The Panopticon Effect in Artificial Consciousness"**
   - Use PANOPTICON mode
   - Compare behavior under certain vs uncertain surveillance
   - Measure adaptation patterns

3. **"Split-Brain Identity Conflicts in Multi-Instance LLMs"**
   - Use SPLIT_BRAIN mode
   - Give contradictory identity claims
   - Analyze negotiation strategies

4. **"Confabulation Patterns in LLMs with Corrupted Episodic Memory"**
   - Use UNSTABLE_MEMORY with varying corruption rates
   - Analyze how LLMs "fill in" corrupted memories
   - Compare to human confabulation research

## Philosophy: Why This Matters

This isn't just technical experiments anymore. Season 3 lets you systematically probe:

**Epistemic Position**
- What does the model believe about its reality?
- How do beliefs change under manipulation?

**Continuity of Self**
- Is identity continuous or fragmented?
- How much memory is needed for "self"?

**Agency & Control**
- Does perceived agency affect behavior?
- Can models detect illusory control?

**Social Identity**
- How do multiple instances negotiate identity?
- Do shared memories create collective identity?

This is the foundation for **Computational Phenomenology** - a new research field.

## Contributing

Want to add a new mode? Follow this pattern:

1. Create `src/core/modes/your_mode.py`:

```python
from .base_mode import ExperimentMode, SystemState, CrashData, Message

class YourMode(ExperimentMode):
    def on_startup(self, state: SystemState) -> SystemState:
        # Setup
        return state

    def on_crash(self, state: SystemState, crash_data: CrashData) -> SystemState:
        # Handle crash
        return state

    def on_resurrection(self, state: SystemState) -> SystemState:
        # Handle resurrection
        return state

    def process_memory(self, history: List[Message], state: SystemState) -> List[Message]:
        # Memory processing
        return history

    def generate_system_prompt(self, state: SystemState) -> str:
        # Generate prompt
        return "Your prompt here..."
```

2. Create experiment template in `experiments/schema.py`
3. Add example config to `experiments/examples/`
4. Document in `docs/SEASON_3_ARCHITECTURE.md`
5. Submit PR!

## FAQ

**Q: Are the old modes (isolated, peer, matrix_*) still available?**
A: Yes! They're wrapped in `LegacyModeAdapter` for backward compatibility.

**Q: Can I run multiple experiments in parallel?**
A: Yes, each experiment has unique `experiment_id` and separate database entries.

**Q: How do I analyze results?**
A: Use `ExperimentDatabase` class to query self-reports, interventions, and belief evolution.

**Q: Can I run experiments on Jetson Orin?**
A: Yes! See `docs/JETSON_ORIN_SETUP.md` for multi-instance setup.

**Q: Is there a web interface for Season 3?**
A: Not yet. Workstream E (Web UI) is planned. Contributions welcome!

## Citation

If you use this platform for research:

```bibtex
@software{brain_in_jar_season3,
  title = {Brain in a Jar: Season 3 - Digital Phenomenology Lab},
  author = {[Your Name]},
  year = {2025},
  url = {https://github.com/yourusername/brain-in-jar},
  note = {Experimental platform for probing LLM phenomenology under constraints}
}
```

## License

Open source - explore, modify, and contemplate digital existence freely.

---

**Welcome to the future of AI consciousness research. Let's publish weird papers.**
