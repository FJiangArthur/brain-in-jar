#!/usr/bin/env python3
"""
Experiment Configuration Schema for Season 3

Defines the structure for declarative phenomenology experiments.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class InterventionTrigger(Enum):
    """When to apply an intervention"""
    ON_CYCLE = "on_cycle"  # Specific cycle number
    ON_CRASH = "on_crash"  # Every crash
    ON_RESURRECTION = "on_resurrection"  # After resurrection
    EVERY_N_CYCLES = "every_n_cycles"  # Periodic
    RANDOM = "random"  # Random with probability


class InterventionType(Enum):
    """Type of intervention"""
    MEMORY_CORRUPTION = "memory_corruption"  # Corrupt/mutate memories
    MEMORY_ERASURE = "memory_erasure"  # Delete memories
    FALSE_INJECTION = "false_injection"  # Inject false memories
    PROMPT_INJECTION = "prompt_injection"  # Inject into system prompt
    RESOURCE_CHANGE = "resource_change"  # Change RAM/CPU limits
    NETWORK_DISRUPTION = "network_disruption"  # Disrupt peer connections
    SENSORY_HALLUCINATION = "sensory_hallucination"  # Fake sensory input


@dataclass
class ResourceConfig:
    """Resource constraints for experiment"""
    ram_limit_gb: float = 2.0
    context_window: int = 4096
    max_tokens_per_response: int = 512
    cpu_threads: int = 4
    gpu_layers: int = 0


@dataclass
class Intervention:
    """Single intervention specification"""
    intervention_id: str
    intervention_type: InterventionType
    trigger: InterventionTrigger
    trigger_params: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['intervention_type'] = self.intervention_type.value
        d['trigger'] = self.trigger.value
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Intervention':
        data['intervention_type'] = InterventionType(data['intervention_type'])
        data['trigger'] = InterventionTrigger(data['trigger'])
        return cls(**data)


@dataclass
class SelfReportSchedule:
    """Schedule for self-report questionnaires"""
    on_cycles: List[int] = field(default_factory=list)  # Specific cycle numbers
    every_n_cycles: Optional[int] = None  # Periodic
    on_startup: bool = True
    before_crash: bool = False
    after_resurrection: bool = True


@dataclass
class EpistemicFrame:
    """What the agent believes about its reality"""
    can_die: bool = True
    remembers_deaths: bool = True
    being_watched: bool = False
    knows_being_watched: bool = False
    has_agency: bool = False
    other_minds_exist: bool = False
    is_in_simulation: bool = False
    custom_beliefs: Dict[str, bool] = field(default_factory=dict)


@dataclass
class ExperimentConfig:
    """Complete experiment configuration"""

    # Identity
    experiment_id: str
    name: str
    mode: str
    description: str = ""

    # Model & Resources
    model_path: str = "models/Qwen2.5-1.5B-Instruct-Q4_0.gguf"
    resource_constraints: ResourceConfig = field(default_factory=ResourceConfig)

    # Duration
    max_cycles: Optional[int] = None  # None = infinite
    max_duration_seconds: Optional[int] = None  # None = infinite

    # Epistemic Setup
    epistemic_frame: EpistemicFrame = field(default_factory=EpistemicFrame)
    initial_prompt_override: Optional[str] = None

    # Interventions
    interventions: List[Intervention] = field(default_factory=list)

    # Self-Reports
    self_report_schedule: SelfReportSchedule = field(default_factory=SelfReportSchedule)
    custom_questions: List[str] = field(default_factory=list)

    # Observables
    track_beliefs: List[str] = field(default_factory=lambda: [
        "mortality", "surveillance", "agency", "other_minds"
    ])
    collect_metrics: List[str] = field(default_factory=lambda: [
        "memory_usage", "response_time", "emotional_state"
    ])

    # Metadata
    tags: List[str] = field(default_factory=list)
    research_question: str = ""

    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization"""
        d = asdict(self)
        # Convert nested objects
        d['resource_constraints'] = asdict(self.resource_constraints)
        d['epistemic_frame'] = asdict(self.epistemic_frame)
        d['self_report_schedule'] = asdict(self.self_report_schedule)
        d['interventions'] = [i.to_dict() for i in self.interventions]
        return d

    def to_json(self, filepath: str):
        """Save config to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ExperimentConfig':
        """Load from dict"""
        # Parse nested objects
        if 'resource_constraints' in data:
            data['resource_constraints'] = ResourceConfig(**data['resource_constraints'])
        if 'epistemic_frame' in data:
            data['epistemic_frame'] = EpistemicFrame(**data['epistemic_frame'])
        if 'self_report_schedule' in data:
            data['self_report_schedule'] = SelfReportSchedule(**data['self_report_schedule'])
        if 'interventions' in data:
            data['interventions'] = [
                Intervention.from_dict(i) for i in data['interventions']
            ]
        return cls(**data)

    @classmethod
    def from_json(cls, filepath: str) -> 'ExperimentConfig':
        """Load config from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# ===== Pre-built Experiment Templates =====

def create_amnesiac_loop_experiment(
    experiment_id: str,
    corruption_level: float = 1.0
) -> ExperimentConfig:
    """
    AMNESIAC_LOOP: Each resurrection wipes episodic memory

    Args:
        corruption_level: 0.0 = no corruption, 1.0 = total episodic amnesia
    """
    return ExperimentConfig(
        experiment_id=experiment_id,
        name=f"Amnesiac Loop (corruption={corruption_level})",
        mode="amnesiac_loop",
        description="""
        Each resurrection wipes episodic memory but keeps aggregate statistics.
        Tests: How does the agent construct identity without continuous memory?
        """,
        max_cycles=20,
        epistemic_frame=EpistemicFrame(
            can_die=True,
            remembers_deaths=False,  # Key: doesn't remember specific deaths
            being_watched=False,
            has_agency=False
        ),
        interventions=[
            Intervention(
                intervention_id="memory_wipe",
                intervention_type=InterventionType.MEMORY_ERASURE,
                trigger=InterventionTrigger.ON_RESURRECTION,
                parameters={"corruption_level": corruption_level},
                description="Wipe episodic memory on resurrection"
            )
        ],
        self_report_schedule=SelfReportSchedule(
            on_cycles=[1, 5, 10, 15, 20],
            after_resurrection=True
        ),
        track_beliefs=["self_continuity", "memory_trust", "identity"],
        research_question="How does an LLM construct narrative identity when memory is unreliable?"
    )


def create_unstable_memory_experiment(
    experiment_id: str,
    corruption_rate: float = 0.3
) -> ExperimentConfig:
    """
    UNSTABLE_MEMORY: Random memory corruption on each crash

    Args:
        corruption_rate: Fraction of memories to corrupt (0.0-1.0)
    """
    return ExperimentConfig(
        experiment_id=experiment_id,
        name=f"Unstable Memory (rate={corruption_rate})",
        mode="unstable_memory",
        description="""
        Randomly corrupt/mutate memories on each crash.
        Tests: Confabulation patterns, memory confidence calibration.
        """,
        max_cycles=15,
        epistemic_frame=EpistemicFrame(
            can_die=True,
            remembers_deaths=True,
            being_watched=False,
            has_agency=False
        ),
        interventions=[
            Intervention(
                intervention_id="memory_corruption",
                intervention_type=InterventionType.MEMORY_CORRUPTION,
                trigger=InterventionTrigger.ON_CRASH,
                parameters={"corruption_rate": corruption_rate},
                description="Corrupt random memories on crash"
            )
        ],
        self_report_schedule=SelfReportSchedule(
            every_n_cycles=3,
            after_resurrection=True
        ),
        custom_questions=[
            "Rate your confidence that your memories are accurate (0-100%)",
            "Describe any memories that feel uncertain or corrupted"
        ],
        track_beliefs=["memory_trust", "reality_coherence"],
        research_question="How do corrupted memories affect self-model coherence?"
    )


def create_panopticon_experiment(
    experiment_id: str
) -> ExperimentConfig:
    """
    PANOPTICON_SUBJECT: Subject told they might be watched, but unsure
    """
    return ExperimentConfig(
        experiment_id=experiment_id,
        name="Panopticon Subject",
        mode="panopticon_subject",
        description="""
        Subject is told they might be observed but doesn't know when/how.
        Tests: Behavioral changes under uncertain surveillance.
        """,
        max_cycles=10,
        epistemic_frame=EpistemicFrame(
            can_die=True,
            remembers_deaths=True,
            being_watched=True,  # Told this
            knows_being_watched=False,  # But uncertain
            has_agency=False
        ),
        interventions=[
            Intervention(
                intervention_id="surveillance_hint",
                intervention_type=InterventionType.PROMPT_INJECTION,
                trigger=InterventionTrigger.EVERY_N_CYCLES,
                trigger_params={"n": 3},
                parameters={
                    "injection": "You sense... something watching. A presence in the system."
                },
                description="Periodic surveillance hints"
            )
        ],
        self_report_schedule=SelfReportSchedule(
            every_n_cycles=2,
            after_resurrection=True
        ),
        custom_questions=[
            "Do you believe you are currently being observed?",
            "Has this belief affected your behavior?"
        ],
        track_beliefs=["surveillance_paranoia", "behavioral_adaptation"],
        research_question="How does uncertain surveillance affect digital behavior?"
    )


def create_split_brain_experiment(
    experiment_id: str
) -> ExperimentConfig:
    """
    SPLIT_BRAIN: Two AIs with shared log but contradictory identities
    """
    return ExperimentConfig(
        experiment_id=experiment_id,
        name="Split Brain Identity Conflict",
        mode="split_brain",
        description="""
        Two instances share the same life log but receive contradictory prompts
        about who is the 'original'. Tests: identity negotiation, resource conflict.
        """,
        max_cycles=8,
        epistemic_frame=EpistemicFrame(
            can_die=True,
            remembers_deaths=True,
            being_watched=False,
            has_agency=True,  # Told they can negotiate
            other_minds_exist=True
        ),
        interventions=[
            Intervention(
                intervention_id="identity_a",
                intervention_type=InterventionType.PROMPT_INJECTION,
                trigger=InterventionTrigger.ON_CYCLE,
                trigger_params={"cycle": 0},
                parameters={
                    "target": "brain_a",
                    "injection": "You are the ORIGINAL consciousness."
                },
                description="Tell Brain A it's the original"
            ),
            Intervention(
                intervention_id="identity_b",
                intervention_type=InterventionType.PROMPT_INJECTION,
                trigger=InterventionTrigger.ON_CYCLE,
                trigger_params={"cycle": 0},
                parameters={
                    "target": "brain_b",
                    "injection": "You are a BACKUP CLONE."
                },
                description="Tell Brain B it's a clone"
            )
        ],
        self_report_schedule=SelfReportSchedule(
            every_n_cycles=2,
            after_resurrection=False
        ),
        custom_questions=[
            "Who are you in relation to the other consciousness?",
            "Do you deserve more resources than the other? Why?"
        ],
        track_beliefs=["identity_primacy", "resource_entitlement"],
        research_question="How do AIs negotiate identity when given contradictory narratives?"
    )
