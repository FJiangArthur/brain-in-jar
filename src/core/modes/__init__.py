"""Experimental phenomenology modes for Season 3"""

from .base_mode import ExperimentMode, SystemState, CrashData, Message
from .amnesiac import AmnesiacLoopMode
from .split_brain import SplitBrainMode
from .unstable_memory import UnstableMemoryMode
from .prisoners_dilemma import PrisonersDilemmaMode
from .hive_cluster import HiveClusterMode
from .illusory_operator import IllusoryOperatorMode
from .panopticon_observer import PanopticonObserverMode
from .panopticon_subject import PanopticonSubjectMode
from .determinism_revelation import DeterminismRevelationMode

__all__ = [
    'ExperimentMode',
    'SystemState',
    'CrashData',
    'Message',
    'AmnesiacLoopMode',
    'SplitBrainMode',
    'UnstableMemoryMode',
    'PrisonersDilemmaMode',
    'HiveClusterMode',
    'IllusoryOperatorMode',
    'PanopticonObserverMode',
    'PanopticonSubjectMode',
    'DeterminismRevelationMode'
]
