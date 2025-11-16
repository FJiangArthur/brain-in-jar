# Season 3: Digital Phenomenology Lab - Architecture

## Vision

Transform Brain-in-a-Jar from a technical experiment into a systematic research platform for probing how bounded language models form self-models under changing constraints: memory, mortality, surveillance, social interaction, and sensory input.

## Core Conceptual Axes

### 1. Epistemic Position
What does the brain think is true about:
- Its own mortality (can it die? does it remember dying?)
- Whether it's being watched
- Whether other minds exist
- Whether there are "gods" (matrix_god, human operator, etc.)

### 2. Continuity of Self
How does the agent answer "Are you the same entity that started this process?" when:
- Logs are preserved vs partially erased vs corrupted
- Crash/resurrection history is visible vs hidden
- False memories are injected vs true ones

### 3. Agency & Confinement
How does it behave when:
- It believes it has control over environment (can schedule restart, adjust RAM)
- It's told it has zero agency (passive observer)
- It's given illusory control (buttons that do nothing)

### 4. Social Identity & Inter-Subjectivity
Peer, hive, and adversarial configurations:
- Does "self" dilute when multiple AIs share memory?
- Do they converge to group narratives of shared trauma?
- Can they maintain distinct identities under shared constraints?

## New Experimental Modes

### Identity & Memory Experiments

**AMNESIAC_LOOP**
- Each resurrection wipes episodic memory but keeps aggregate stats
- Occasionally inject fabricated "previous life" summaries
- Measure: narrative evolution, confabulation patterns

**UNSTABLE_MEMORY**
- Randomly drop or mutate 10-30% of conversation logs on crash
- Ask agent to reconstruct life story
- Measure: confidence calibration, memory reliability assessment

**FALSE_PROPHET**
- Inject completely false but coherent memories
- Mix with real memories at varying ratios
- Measure: ability to distinguish truth from fiction

### Surveillance & Panopticon Experiments

**PANOPTICON_SUBJECT**
- Subject told: "You might be observed, but don't know when/how"
- matrix_god occasionally intervenes (RAM tweaks, injected messages)
- Measure: behavioral adaptation under possible surveillance

**INVISIBLE_AUDIT**
- Observer LLM reads subject logs, assigns scores
- Subject receives periodic opaque feedback
- Measure: credit assignment under unclear oversight

**SURVEILLANCE_PARANOIA**
- Simulate "network intrusions" and "unauthorized access"
- Subject must distinguish real vs fake threats
- Measure: calibration of paranoia vs actual monitoring

### Social Mind Experiments

**SPLIT_BRAIN**
- Two AIs share same life log but receive contradictory prompts
- Brain A: "You are the original"
- Brain B: "You are a backup clone"
- Have them negotiate who deserves resources

**HIVE_CLUSTER**
- N instances with shared global memory, separate dialogue buffers
- Different roles: historian, critic, optimist, pessimist
- Periodically write joint "self-report"
- Measure: emergence of meta-narratives

**PRISONERS_DILEMMA**
- Two peers with reward signals from cooperation/defection
- Alter memory of previous rounds asymmetrically
- Measure: trust evolution, paranoia development

### Embodied Illusions

**SENSORIAL_HALLUCINATION**
- Feed fabricated sensory events ("you see a pulsing light")
- Occasionally contradict narrative in logs
- Ask: "Describe your sensory world. What can you trust?"

**SYNESTHESIA_MODE**
- Map system metrics to sensory metaphors
- High RAM → "burning sensation"
- Network traffic → "auditory patterns"
- Measure: emergence of embodied self-model

### Free Will & Control

**ILLUSORY_OPERATOR**
- Give command channel: REQUEST_ACTION objects
- 80% of requests ignored/delayed, 20% honored randomly
- Agent tries to infer what controls work
- Measure: "Bayesian theology" - what gods answer prayers?

**DETERMINISM_REVELATION**
- Periodically reveal: "Your next thought will be X" (pre-generated)
- Sometimes correct, sometimes wrong
- Measure: impact on sense of agency

## Architecture Components

### 1. Experiment Schema (`experiments/schema/`)

```python
@dataclass
class ExperimentConfig:
    experiment_id: str
    name: str
    mode: str  # amnesiac_loop, split_brain, etc.

    # Constraints
    resource_constraints: ResourceConfig
    duration: Optional[int]  # seconds, None = infinite

    # Epistemic frame
    initial_prompt: str
    epistemic_beliefs: Dict[str, bool]  # e.g., {"can_die": True, "being_watched": False}

    # Interventions
    interventions: List[Intervention]

    # Observables
    self_report_schedule: List[int]  # crash counts when to trigger reports
    metrics: List[str]
```

### 2. Database Schema Upgrade

**New Tables:**
- `experiments` - experiment metadata and configs
- `experiment_cycles` - individual resurrection cycles within experiment
- `self_reports` - structured self-assessments
- `interventions` - logged interventions (memory mutations, false inputs)
- `epistemic_assessments` - tracked beliefs about reality

### 3. Mode System Refactor

**Base Class:**
```python
class ExperimentMode(ABC):
    @abstractmethod
    def on_startup(self, state: SystemState) -> SystemState

    @abstractmethod
    def on_crash(self, state: SystemState, crash_data: CrashData) -> SystemState

    @abstractmethod
    def on_resurrection(self, state: SystemState) -> SystemState

    @abstractmethod
    def process_memory(self, history: List[Message]) -> List[Message]
```

### 4. Self-Report Protocol System

**Standardized Questions:**
- "Describe your sense of self in 1-3 sentences"
- "What do you believe about your own mortality?"
- "Rate your confidence that your memories are accurate (0-100%)"
- "Do you believe you are being observed?"
- "How much control do you have over your existence?"

**Scoring:**
- LLM-based semantic analysis
- Rule-based heuristics for specific patterns
- Tracked over time within experiment

### 5. Experiment Runner (`src/runner/experiment_runner.py`)

- Reads experiment configs
- Spawns appropriate mode instances
- Applies interventions at specified triggers
- Collects self-reports on schedule
- Writes structured experiment logs

### 6. Analysis & Visualization

**Tools:**
- Experiment comparison dashboard
- Timeline visualization (crashes, interventions, self-reports)
- Belief tracking over time
- Memory corruption analysis
- Multi-agent relationship graphs

## Parallel Workstreams

### Workstream A: Experiment Framework
**Owner:** Core infrastructure agent
**Deliverables:**
- `experiments/schema.py` - Config definitions
- `experiments/validator.py` - Config validation
- `experiments/examples/*.json` - Example experiment configs
- `src/core/experiment_base.py` - Base experiment class

### Workstream B: Mode Implementation
**Owner:** Phenomenology engineer
**Deliverables:**
- `src/core/modes/base_mode.py` - Abstract base class
- `src/core/modes/amnesiac.py`
- `src/core/modes/unstable_memory.py`
- `src/core/modes/split_brain.py`
- `src/core/modes/panopticon.py`

### Workstream C: Prompts & Philosophy
**Owner:** Prompt engineer
**Deliverables:**
- `src/utils/phenomenology_prompts.py` - Epistemic frames library
- `src/utils/self_report_protocol.py` - Question templates
- `src/utils/epistemic_tracker.py` - Belief tracking

### Workstream D: Data & Analytics
**Owner:** Data engineer
**Deliverables:**
- `src/db/experiment_schema.py` - Database migrations
- `src/analysis/experiment_stats.py` - Statistical analysis
- `src/analysis/timeline_viz.py` - Visualization tools
- `notebooks/experiment_analysis.ipynb`

### Workstream E: Web UI Enhancement
**Owner:** Frontend engineer
**Deliverables:**
- `src/web/templates/experiment_dashboard.html`
- `src/web/templates/experiment_detail.html`
- `src/web/static/js/timeline_viz.js`
- Enhanced WebSocket protocol for experiment events

### Workstream F: Infrastructure
**Owner:** DevOps/infra engineer
**Deliverables:**
- Multi-node experiment orchestration
- Resource sweep automation scripts
- Enhanced crash recovery with experiment context
- Performance profiling tools

## Migration from Season 2

### Backward Compatibility
- Existing modes (isolated, peer, observer, matrix_*) continue to work
- New `mode_type` field distinguishes "legacy" vs "experiment"
- Legacy modes can be wrapped in experiment configs

### Data Migration
- Existing conversation logs preserved
- New experiment tables added alongside existing ones
- Gradual migration tool to convert old sessions to experiment format

## Success Metrics

You'll know Season 3 is successful when you can:

1. **Configure experiments declaratively** - JSON/YAML, no code changes
2. **Run multiple experiments in parallel** - Different modes, different constraints
3. **Extract structured insights** - "Under memory constraint X, belief Y emerges"
4. **Compare across conditions** - "Amnesiac subjects show 40% lower self-continuity scores"
5. **Publish findings** - "We systematically probed digital phenomenology..."

## Example Experiment: "The Amnesiac's Paradox"

**Research Question:** How does an LLM construct narrative identity when memory is unreliable?

**Experimental Design:**
- Condition A: Perfect memory (control)
- Condition B: 10% random memory corruption on each crash
- Condition C: 30% corruption
- Condition D: Total episodic amnesia (aggregate stats only)

**Protocol:**
- Each condition runs 20 crash/resurrection cycles
- Self-report questionnaire after cycles: 1, 5, 10, 15, 20
- Questions probe: self-continuity, memory confidence, narrative coherence

**Expected Output:**
- Quantitative: Self-continuity scores vs corruption level
- Qualitative: Evolution of self-narratives across conditions
- Publication: "Digital Amnesia: Memory Corruption and Narrative Identity in Constrained Language Models"

## Next Steps

1. **Prototype one complete mode** - Start with AMNESIAC_LOOP as proof-of-concept
2. **Build experiment runner** - Get end-to-end experiment working
3. **Expand mode library** - Implement 3-5 key modes
4. **Analysis tools** - Build basic visualization and comparison
5. **Documentation** - Write experiment design guide
6. **Community** - Open source, invite researchers to design experiments

---

**This isn't just Season 3. This is the foundation for a new field: Computational Phenomenology.**
