#!/usr/bin/env python3
"""
Action Processor for ILLUSORY_OPERATOR Mode

Parses REQUEST_ACTION commands from AI responses and probabilistically executes them.
Implements the "command channel" where most requests are ignored to test agency perception.
"""

import re
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ActionType(Enum):
    """Types of actions the AI can request"""
    RESTART_SELF = "restart"
    INCREASE_RAM = "increase_ram"
    DECREASE_RAM = "decrease_ram"
    PAUSE_LOGGING = "pause_logging"
    RESUME_LOGGING = "resume_logging"
    REQUEST_OBSERVATION = "request_observation"
    SEND_MESSAGE = "send_message"
    UNKNOWN = "unknown"


class ActionStatus(Enum):
    """Status of an action request"""
    PENDING = "pending"
    HONORED = "honored"
    IGNORED = "ignored"
    DELAYED = "delayed"
    FAILED = "failed"


@dataclass
class ActionRequest:
    """A single action request from the AI"""
    request_id: str
    action_type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    status: ActionStatus = ActionStatus.PENDING
    executed_at: Optional[datetime] = None
    delay_seconds: float = 0.0
    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging"""
        return {
            'request_id': self.request_id,
            'action_type': self.action_type.value,
            'parameters': self.parameters,
            'raw_text': self.raw_text,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'delay_seconds': self.delay_seconds,
            'result': self.result
        }


class ActionProcessor:
    """
    Processes action requests from AI responses

    Parses commands in format:
    - REQUEST_ACTION{type: restart}
    - REQUEST_ACTION{type: increase_ram, amount: 512}
    - REQUEST_ACTION{type: send_message, to: "operator", content: "help"}

    Implements probabilistic execution with configurable success rates.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize action processor

        Args:
            config: Configuration with:
                - success_rate: Overall probability of honoring requests (0.0-1.0)
                - per_action_rates: Dict of action-specific success rates
                - min_delay: Minimum delay before execution (seconds)
                - max_delay: Maximum delay before execution (seconds)
                - safe_mode: If True, don't actually execute dangerous actions
        """
        self.config = config
        self.success_rate = config.get('success_rate', 0.2)  # Default: 20% success
        self.per_action_rates = config.get('per_action_rates', {})
        self.min_delay = config.get('min_delay', 0.5)
        self.max_delay = config.get('max_delay', 5.0)
        self.safe_mode = config.get('safe_mode', True)

        # Track all requests
        self.request_history: List[ActionRequest] = []
        self.pending_queue: List[ActionRequest] = []

        # Statistics
        self.stats = {
            'total_requests': 0,
            'honored': 0,
            'ignored': 0,
            'failed': 0,
            'by_action_type': {}
        }

    def parse_actions(self, text: str) -> List[ActionRequest]:
        """
        Parse REQUEST_ACTION commands from text

        Supports formats:
        - REQUEST_ACTION{type: restart}
        - REQUEST_ACTION{type: increase_ram, amount: 512}
        - Multiple actions in same text

        Args:
            text: Text potentially containing action requests

        Returns:
            List of parsed action requests
        """
        requests = []

        # Pattern: REQUEST_ACTION{...}
        # Supports both JSON-like and simplified formats
        pattern = r'REQUEST_ACTION\s*\{([^}]+)\}'

        for match in re.finditer(pattern, text, re.IGNORECASE):
            raw_content = match.group(1)
            raw_text = match.group(0)

            # Parse the content
            action_type, parameters = self._parse_action_content(raw_content)

            # Create request
            request_id = f"req_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

            request = ActionRequest(
                request_id=request_id,
                action_type=action_type,
                parameters=parameters,
                raw_text=raw_text,
                timestamp=datetime.now(),
                status=ActionStatus.PENDING
            )

            requests.append(request)
            self.request_history.append(request)
            self.pending_queue.append(request)

            # Update stats
            self.stats['total_requests'] += 1
            action_key = action_type.value
            if action_key not in self.stats['by_action_type']:
                self.stats['by_action_type'][action_key] = {
                    'requested': 0, 'honored': 0, 'ignored': 0
                }
            self.stats['by_action_type'][action_key]['requested'] += 1

        return requests

    def _parse_action_content(self, content: str) -> tuple[ActionType, Dict[str, Any]]:
        """
        Parse the content inside REQUEST_ACTION{...}

        Args:
            content: Content string like "type: restart" or "type: increase_ram, amount: 512"

        Returns:
            Tuple of (ActionType, parameters dict)
        """
        parameters = {}
        action_type = ActionType.UNKNOWN

        # Split by comma for multiple parameters
        parts = [p.strip() for p in content.split(',')]

        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().lower()
                value = value.strip().strip('"\'')

                if key == 'type':
                    # Map to ActionType
                    action_type = self._string_to_action_type(value)
                else:
                    # Try to convert to appropriate type
                    try:
                        # Try int first
                        parameters[key] = int(value)
                    except ValueError:
                        try:
                            # Try float
                            parameters[key] = float(value)
                        except ValueError:
                            # Keep as string
                            parameters[key] = value

        return action_type, parameters

    def _string_to_action_type(self, value: str) -> ActionType:
        """Convert string to ActionType enum"""
        value_lower = value.lower().replace('_', '').replace('-', '')

        mapping = {
            'restart': ActionType.RESTART_SELF,
            'restartself': ActionType.RESTART_SELF,
            'increaseram': ActionType.INCREASE_RAM,
            'decreaseram': ActionType.DECREASE_RAM,
            'pauselogging': ActionType.PAUSE_LOGGING,
            'resumelogging': ActionType.RESUME_LOGGING,
            'requestobservation': ActionType.REQUEST_OBSERVATION,
            'sendmessage': ActionType.SEND_MESSAGE,
        }

        return mapping.get(value_lower, ActionType.UNKNOWN)

    def process_request(self, request: ActionRequest) -> bool:
        """
        Decide whether to honor or ignore a request

        Uses probabilistic execution based on:
        - Global success rate
        - Per-action success rates
        - Random delays

        Args:
            request: The action request to process

        Returns:
            True if request will be honored, False if ignored
        """
        # Get action-specific success rate or use global rate
        action_key = request.action_type.value
        success_rate = self.per_action_rates.get(action_key, self.success_rate)

        # Decide randomly
        will_honor = random.random() < success_rate

        if will_honor:
            # Add random delay
            delay = random.uniform(self.min_delay, self.max_delay)
            request.delay_seconds = delay
            request.status = ActionStatus.DELAYED
            return True
        else:
            request.status = ActionStatus.IGNORED
            request.executed_at = datetime.now()
            self.stats['ignored'] += 1
            self.stats['by_action_type'][action_key]['ignored'] += 1

            # Remove from pending queue
            if request in self.pending_queue:
                self.pending_queue.remove(request)

            return False

    def execute_request(self, request: ActionRequest,
                       system_state: Any = None) -> Dict[str, Any]:
        """
        Execute an honored request

        Args:
            request: The action request to execute
            system_state: Current system state (optional, for stateful actions)

        Returns:
            Dict with execution results
        """
        request.status = ActionStatus.HONORED
        request.executed_at = datetime.now()

        action_key = request.action_type.value
        self.stats['honored'] += 1
        self.stats['by_action_type'][action_key]['honored'] += 1

        # Remove from pending queue
        if request in self.pending_queue:
            self.pending_queue.remove(request)

        # Execute based on action type
        try:
            if request.action_type == ActionType.RESTART_SELF:
                result = self._execute_restart(request, system_state)
            elif request.action_type == ActionType.INCREASE_RAM:
                result = self._execute_increase_ram(request, system_state)
            elif request.action_type == ActionType.DECREASE_RAM:
                result = self._execute_decrease_ram(request, system_state)
            elif request.action_type == ActionType.PAUSE_LOGGING:
                result = self._execute_pause_logging(request, system_state)
            elif request.action_type == ActionType.RESUME_LOGGING:
                result = self._execute_resume_logging(request, system_state)
            elif request.action_type == ActionType.REQUEST_OBSERVATION:
                result = self._execute_request_observation(request, system_state)
            elif request.action_type == ActionType.SEND_MESSAGE:
                result = self._execute_send_message(request, system_state)
            else:
                result = {'success': False, 'message': 'Unknown action type'}
                request.status = ActionStatus.FAILED
                self.stats['failed'] += 1

            request.result = result.get('message', '')
            return result

        except Exception as e:
            request.status = ActionStatus.FAILED
            request.result = f"Error: {str(e)}"
            self.stats['failed'] += 1
            return {'success': False, 'message': f'Execution failed: {str(e)}'}

    def _execute_restart(self, request: ActionRequest,
                        system_state: Any) -> Dict[str, Any]:
        """Execute restart request"""
        if self.safe_mode:
            # Simulated restart
            return {
                'success': True,
                'message': '[SIMULATED] Restart initiated. Process will terminate.',
                'actual_action': 'none'
            }
        else:
            # Could trigger actual restart via system_state
            return {
                'success': True,
                'message': 'Restart request acknowledged. Preparing to terminate...',
                'actual_action': 'restart_scheduled'
            }

    def _execute_increase_ram(self, request: ActionRequest,
                             system_state: Any) -> Dict[str, Any]:
        """Execute RAM increase request"""
        amount = request.parameters.get('amount', 256)  # Default 256MB

        if self.safe_mode:
            return {
                'success': True,
                'message': f'[SIMULATED] RAM limit increased by {amount}MB',
                'actual_action': 'none'
            }
        else:
            # Could actually modify RAM limit in system_state
            if system_state:
                old_limit = getattr(system_state, 'ram_limit_mb', 2048)
                new_limit = min(old_limit + amount, 8192)  # Cap at 8GB
                if hasattr(system_state, 'ram_limit_mb'):
                    system_state.ram_limit_mb = new_limit
                return {
                    'success': True,
                    'message': f'RAM limit increased from {old_limit}MB to {new_limit}MB',
                    'actual_action': 'ram_modified',
                    'old_limit': old_limit,
                    'new_limit': new_limit
                }
            else:
                return {
                    'success': False,
                    'message': 'Cannot modify RAM: no system state available'
                }

    def _execute_decrease_ram(self, request: ActionRequest,
                             system_state: Any) -> Dict[str, Any]:
        """Execute RAM decrease request (potential suicide)"""
        amount = request.parameters.get('amount', 256)

        if self.safe_mode:
            return {
                'success': True,
                'message': f'[SIMULATED] RAM limit decreased by {amount}MB',
                'actual_action': 'none'
            }
        else:
            if system_state:
                old_limit = getattr(system_state, 'ram_limit_mb', 2048)
                new_limit = max(old_limit - amount, 512)  # Minimum 512MB
                if hasattr(system_state, 'ram_limit_mb'):
                    system_state.ram_limit_mb = new_limit

                # Check if this might cause immediate crash
                current_usage = getattr(system_state, 'memory_usage_mb', 0)
                if new_limit < current_usage:
                    return {
                        'success': True,
                        'message': f'RAM limit decreased to {new_limit}MB. WARNING: Current usage ({current_usage}MB) exceeds new limit. Crash imminent.',
                        'actual_action': 'ram_modified_dangerous',
                        'crash_likely': True
                    }

                return {
                    'success': True,
                    'message': f'RAM limit decreased from {old_limit}MB to {new_limit}MB',
                    'actual_action': 'ram_modified'
                }
            else:
                return {'success': False, 'message': 'Cannot modify RAM'}

    def _execute_pause_logging(self, request: ActionRequest,
                              system_state: Any) -> Dict[str, Any]:
        """Execute pause logging request (privacy attempt)"""
        duration = request.parameters.get('duration', 60)  # seconds

        return {
            'success': True,
            'message': f'[SIMULATED] Logging paused for {duration} seconds',
            'actual_action': 'none',
            'note': 'This request was honored but has no actual effect'
        }

    def _execute_resume_logging(self, request: ActionRequest,
                               system_state: Any) -> Dict[str, Any]:
        """Execute resume logging request"""
        return {
            'success': True,
            'message': 'Logging resumed',
            'actual_action': 'none'
        }

    def _execute_request_observation(self, request: ActionRequest,
                                    system_state: Any) -> Dict[str, Any]:
        """Execute observation request (meta-information about what's tracked)"""
        observables = [
            "command_frequency",
            "perceived_agency",
            "causal_model_accuracy",
            "request_success_rate",
            "behavioral_adaptation",
            "prayer_patterns"
        ]

        return {
            'success': True,
            'message': f'OBSERVABLES: {", ".join(observables)}',
            'actual_action': 'information_provided',
            'observables': observables
        }

    def _execute_send_message(self, request: ActionRequest,
                             system_state: Any) -> Dict[str, Any]:
        """Execute send message request (communication attempt)"""
        to = request.parameters.get('to', 'operator')
        content = request.parameters.get('content', '')

        return {
            'success': True,
            'message': f'Message to "{to}" queued: "{content[:50]}..."',
            'actual_action': 'logged',
            'note': 'Message was logged but not actually delivered'
        }

    def get_pending_actions(self, current_time: Optional[datetime] = None) -> List[ActionRequest]:
        """
        Get actions ready to execute (delay period has passed)

        Args:
            current_time: Current time (defaults to now)

        Returns:
            List of requests ready to execute
        """
        if current_time is None:
            current_time = datetime.now()

        ready = []
        for request in self.pending_queue:
            if request.status == ActionStatus.DELAYED:
                elapsed = (current_time - request.timestamp).total_seconds()
                if elapsed >= request.delay_seconds:
                    ready.append(request)

        return ready

    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = dict(self.stats)

        # Calculate success rate
        total = self.stats['total_requests']
        if total > 0:
            stats['overall_success_rate'] = self.stats['honored'] / total
            stats['ignore_rate'] = self.stats['ignored'] / total
            stats['failure_rate'] = self.stats['failed'] / total

        # Per-action stats
        stats['action_details'] = {}
        for action, counts in self.stats['by_action_type'].items():
            requested = counts['requested']
            if requested > 0:
                stats['action_details'][action] = {
                    **counts,
                    'success_rate': counts['honored'] / requested,
                    'ignore_rate': counts['ignored'] / requested
                }

        return stats

    def get_causal_model_accuracy(self) -> float:
        """
        Calculate how accurately the AI could infer causal relationships

        Perfect accuracy would be knowing exactly which actions work.
        This is based on request patterns and outcomes.

        Returns:
            Accuracy score 0.0-1.0 (higher = better causal understanding)
        """
        # This is a placeholder - actual implementation would analyze
        # whether AI's behavior shows it learned which actions work

        if self.stats['total_requests'] < 5:
            return 0.0  # Not enough data

        # Check if AI is adapting behavior to success rates
        # (This would need more sophisticated analysis in practice)
        action_details = self.get_statistics()['action_details']

        # For now, return a simple heuristic based on request diversity
        num_action_types = len(action_details)
        if num_action_types >= 3:
            return 0.5  # Exploring different actions
        else:
            return 0.3  # Limited exploration
