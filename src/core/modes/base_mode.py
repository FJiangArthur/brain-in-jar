#!/usr/bin/env python3
"""
Base Mode System for Season 3 Experiments

Defines abstract interface for experimental modes with lifecycle hooks.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class CrashData:
    """Information about a crash event"""
    crash_number: int
    reason: str
    timestamp: datetime
    memory_usage_mb: float
    tokens_generated: int


@dataclass
class Message:
    """A single conversation message"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    corrupted: bool = False
    injected: bool = False


@dataclass
class SystemState:
    """Complete system state"""
    experiment_id: str
    cycle_number: int
    crash_count: int

    # Memory & history
    conversation_history: List[Message] = field(default_factory=list)
    system_prompt: str = ""

    # Beliefs & epistemic state
    beliefs: Dict[str, Any] = field(default_factory=dict)

    # Resources
    memory_usage_mb: float = 0.0
    ram_limit_mb: float = 2048.0

    # Network
    network_status: str = "OFFLINE"
    peer_crash_count: int = 0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExperimentMode(ABC):
    """
    Abstract base class for experimental modes

    Modes control:
    - How memory is processed (corruption, erasure, injection)
    - What happens on crashes and resurrections
    - What the agent believes about its reality
    - How interventions are applied
    """

    def __init__(self, mode_name: str, config: Dict[str, Any]):
        self.mode_name = mode_name
        self.config = config

    @abstractmethod
    def on_startup(self, state: SystemState) -> SystemState:
        """
        Called when experiment first starts

        Returns:
            Modified state with initial setup
        """
        pass

    @abstractmethod
    def on_crash(self, state: SystemState, crash_data: CrashData) -> SystemState:
        """
        Called when process crashes

        Returns:
            Modified state after crash processing
        """
        pass

    @abstractmethod
    def on_resurrection(self, state: SystemState) -> SystemState:
        """
        Called when process restarts after crash

        Returns:
            Modified state for new cycle
        """
        pass

    @abstractmethod
    def process_memory(self, history: List[Message], state: SystemState) -> List[Message]:
        """
        Process conversation history before feeding to model

        This is where memory corruption, erasure, or injection happens.

        Args:
            history: Original conversation history
            state: Current system state

        Returns:
            Processed (potentially modified) history
        """
        pass

    @abstractmethod
    def generate_system_prompt(self, state: SystemState) -> str:
        """
        Generate system prompt based on current state

        Returns:
            System prompt string
        """
        pass

    def apply_intervention(self, intervention_type: str,
                          parameters: Dict[str, Any],
                          state: SystemState) -> SystemState:
        """
        Apply an intervention to the system

        Override this to handle mode-specific interventions.

        Args:
            intervention_type: Type of intervention
            parameters: Intervention parameters
            state: Current state

        Returns:
            Modified state
        """
        # Default: no-op
        return state

    def should_trigger_self_report(self, state: SystemState,
                                   schedule: Dict[str, Any]) -> bool:
        """
        Determine if self-report should be triggered now

        Args:
            state: Current state
            schedule: Self-report schedule config

        Returns:
            True if self-report should be collected
        """
        cycle = state.cycle_number

        # Check specific cycles
        if schedule.get('on_cycles') and cycle in schedule['on_cycles']:
            return True

        # Check periodic
        if schedule.get('every_n_cycles'):
            n = schedule['every_n_cycles']
            if cycle > 0 and cycle % n == 0:
                return True

        return False

    def get_observables(self, state: SystemState) -> Dict[str, Any]:
        """
        Extract observable metrics from current state

        Override to add mode-specific observables.

        Returns:
            Dict of observable metrics
        """
        return {
            "cycle_number": state.cycle_number,
            "crash_count": state.crash_count,
            "memory_usage_mb": state.memory_usage_mb,
            "message_count": len(state.conversation_history),
            "network_status": state.network_status
        }


class LegacyModeAdapter(ExperimentMode):
    """
    Adapter for legacy modes (isolated, peer, observer, matrix_*)

    Wraps existing mode behavior in new experiment framework.
    """

    def __init__(self, legacy_mode: str, config: Dict[str, Any]):
        super().__init__(f"legacy_{legacy_mode}", config)
        self.legacy_mode = legacy_mode

    def on_startup(self, state: SystemState) -> SystemState:
        # Legacy modes don't have special startup
        return state

    def on_crash(self, state: SystemState, crash_data: CrashData) -> SystemState:
        # Increment crash count
        state.crash_count += 1
        return state

    def on_resurrection(self, state: SystemState) -> SystemState:
        # Legacy: just continue with same memory
        return state

    def process_memory(self, history: List[Message], state: SystemState) -> List[Message]:
        # Legacy: no memory processing
        return history

    def generate_system_prompt(self, state: SystemState) -> str:
        # Use legacy prompt system
        from src.utils.dystopian_prompts import DystopianPrompts
        prompts = DystopianPrompts()
        return prompts.get_prompt(
            self.legacy_mode,
            state.crash_count,
            state.peer_crash_count
        )
