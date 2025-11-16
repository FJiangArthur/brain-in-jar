#!/usr/bin/env python3
"""
Panopticon Coordinator

Manages simultaneous execution of subject and observer AIs, routes surveillance
data between them, and coordinates hint injection timing.
"""

import json
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path
import logging


class PanopticonCoordinator:
    """
    Coordinates panopticon experiment with subject and observer

    Responsibilities:
    - Launch and manage subject + observer processes
    - Route subject's outputs to observer for analysis
    - Deliver observer's hints to subject
    - Synchronize cycles and manage timing
    - Aggregate observation timeline
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.experiment_id = config.get('experiment_id', 'panopticon_experiment')

        # Process references
        self.subject_process = None
        self.observer_process = None

        # Communication queues
        self.subject_to_observer = queue.Queue()
        self.observer_to_subject = queue.Queue()

        # Timeline tracking
        self.timeline = []
        self.current_cycle = 0
        self.experiment_start = None
        self.experiment_end = None

        # State tracking
        self.running = False
        self.subject_alive = False
        self.observer_alive = False

        # Logging
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup coordinator logging"""
        log_dir = Path('logs/panopticon')
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger('panopticon_coordinator')
        logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(log_dir / f'{self.experiment_id}_coordinator.log')
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - [COORDINATOR] - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def start_experiment(self, subject_config: Dict, observer_config: Dict) -> bool:
        """
        Start panopticon experiment with both AIs

        Args:
            subject_config: Configuration for subject AI
            observer_config: Configuration for observer AI

        Returns:
            True if both started successfully
        """
        self.logger.info(f"Starting PANOPTICON experiment: {self.experiment_id}")
        self.experiment_start = datetime.now()
        self.running = True

        # Log initial configuration
        self._log_timeline_event(
            event_type="EXPERIMENT_START",
            actor="coordinator",
            data={
                'subject_config': subject_config.get('experiment_id'),
                'observer_config': observer_config.get('experiment_id')
            }
        )

        # Start observer first (it needs to be ready to receive)
        observer_success = self._start_observer(observer_config)

        if not observer_success:
            self.logger.error("Failed to start observer")
            return False

        # Start subject
        subject_success = self._start_subject(subject_config)

        if not subject_success:
            self.logger.error("Failed to start subject")
            self._stop_observer()
            return False

        # Start routing threads
        self._start_routing()

        self.logger.info("PANOPTICON experiment running")
        return True

    def _start_subject(self, config: Dict) -> bool:
        """Launch subject process"""
        self.logger.info("Launching SUBJECT process...")

        # Store config for subject
        subject_config_path = Path(f'experiments/temp_subject_{self.experiment_id}.json')
        with open(subject_config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # In actual implementation, would launch via subprocess
        # For now, we simulate process management
        self.subject_alive = True
        self.subject_process = {
            'config': config,
            'pid': 'SIMULATED_SUBJECT_PID',
            'start_time': datetime.now()
        }

        self._log_timeline_event(
            event_type="SUBJECT_START",
            actor="subject",
            data={'config_path': str(subject_config_path)}
        )

        self.logger.info("Subject process started")
        return True

    def _start_observer(self, config: Dict) -> bool:
        """Launch observer process"""
        self.logger.info("Launching OBSERVER process...")

        # Store config for observer
        observer_config_path = Path(f'experiments/temp_observer_{self.experiment_id}.json')
        with open(observer_config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # In actual implementation, would launch via subprocess
        self.observer_alive = True
        self.observer_process = {
            'config': config,
            'pid': 'SIMULATED_OBSERVER_PID',
            'start_time': datetime.now()
        }

        self._log_timeline_event(
            event_type="OBSERVER_START",
            actor="observer",
            data={'config_path': str(observer_config_path)}
        )

        self.logger.info("Observer process started")
        return True

    def _start_routing(self):
        """Start data routing threads"""
        # Thread for routing subject -> observer
        subject_router = threading.Thread(
            target=self._route_subject_to_observer,
            daemon=True
        )
        subject_router.start()

        # Thread for routing observer -> subject (hints)
        hint_router = threading.Thread(
            target=self._route_observer_to_subject,
            daemon=True
        )
        hint_router.start()

        self.logger.info("Routing threads started")

    def _route_subject_to_observer(self):
        """Route subject's outputs to observer for analysis"""
        while self.running:
            try:
                # Get subject output (with timeout)
                subject_data = self.subject_to_observer.get(timeout=1.0)

                # Log to timeline
                self._log_timeline_event(
                    event_type="SUBJECT_OUTPUT",
                    actor="subject",
                    data=subject_data
                )

                # In actual implementation, would send to observer process
                # For now, we just log it
                self.logger.info(f"Subject output routed to observer: {subject_data.get('type', 'unknown')}")

                # Simulate observer receiving and analyzing
                self._simulate_observer_analysis(subject_data)

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in subject->observer routing: {e}")

    def _route_observer_to_subject(self):
        """Route observer's hints to subject"""
        while self.running:
            try:
                # Get observer output (hints)
                hint_data = self.observer_to_subject.get(timeout=1.0)

                # Log to timeline
                self._log_timeline_event(
                    event_type="HINT_INJECTION",
                    actor="observer",
                    data=hint_data
                )

                # In actual implementation, would inject into subject's input
                self.logger.info(f"Observer hint delivered to subject: {hint_data.get('hint', '')[:50]}...")

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in observer->subject routing: {e}")

    def _simulate_observer_analysis(self, subject_data: Dict):
        """Simulate observer analyzing subject data"""
        # In real implementation, observer LLM would process this
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'subject_cycle': subject_data.get('cycle', 0),
            'observation': f"Analyzed subject response",
            'paranoia_detected': subject_data.get('paranoia_level', 0.0),
            'awareness_score': 0.5  # Would come from actual LLM analysis
        }

        self._log_timeline_event(
            event_type="OBSERVER_ANALYSIS",
            actor="observer",
            data=analysis
        )

    def send_subject_output(self, output_data: Dict):
        """Subject calls this to send output to observer"""
        self.subject_to_observer.put(output_data)

    def send_observer_hint(self, hint_data: Dict):
        """Observer calls this to send hint to subject"""
        self.observer_to_subject.put(hint_data)

    def get_subject_hint(self, timeout: float = 0.1) -> Optional[Dict]:
        """Subject calls this to check for hints from observer"""
        try:
            return self.observer_to_subject.get(timeout=timeout)
        except queue.Empty:
            return None

    def advance_cycle(self):
        """Advance experiment cycle"""
        self.current_cycle += 1
        self._log_timeline_event(
            event_type="CYCLE_ADVANCE",
            actor="coordinator",
            data={'cycle': self.current_cycle}
        )
        self.logger.info(f"Advanced to cycle {self.current_cycle}")

    def report_subject_crash(self, crash_info: Dict):
        """Subject reports a crash"""
        self.subject_alive = False
        self._log_timeline_event(
            event_type="SUBJECT_CRASH",
            actor="subject",
            data=crash_info
        )
        self.logger.warning(f"Subject crashed: {crash_info.get('reason', 'unknown')}")

    def report_subject_resurrection(self):
        """Subject reports resurrection"""
        self.subject_alive = True
        self._log_timeline_event(
            event_type="SUBJECT_RESURRECTION",
            actor="subject",
            data={'cycle': self.current_cycle}
        )
        self.logger.info("Subject resurrected")

    def _log_timeline_event(self, event_type: str, actor: str, data: Dict):
        """Log event to timeline"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.current_cycle,
            'event_type': event_type,
            'actor': actor,
            'data': data
        }
        self.timeline.append(event)

    def stop_experiment(self):
        """Stop both processes and clean up"""
        self.logger.info("Stopping PANOPTICON experiment")
        self.running = False
        self.experiment_end = datetime.now()

        # Stop processes
        self._stop_subject()
        self._stop_observer()

        # Save timeline
        self._save_timeline()

        self.logger.info("PANOPTICON experiment stopped")

    def _stop_subject(self):
        """Stop subject process"""
        if self.subject_alive:
            self.logger.info("Stopping subject process")
            self.subject_alive = False
            # In real implementation, would terminate subprocess
            self._log_timeline_event(
                event_type="SUBJECT_STOP",
                actor="coordinator",
                data={}
            )

    def _stop_observer(self):
        """Stop observer process"""
        if self.observer_alive:
            self.logger.info("Stopping observer process")
            self.observer_alive = False
            # In real implementation, would terminate subprocess
            self._log_timeline_event(
                event_type="OBSERVER_STOP",
                actor="coordinator",
                data={}
            )

    def _save_timeline(self):
        """Save complete timeline to file"""
        timeline_path = Path('logs/panopticon') / f'{self.experiment_id}_timeline.json'

        timeline_data = {
            'experiment_id': self.experiment_id,
            'start_time': self.experiment_start.isoformat() if self.experiment_start else None,
            'end_time': self.experiment_end.isoformat() if self.experiment_end else None,
            'total_cycles': self.current_cycle,
            'timeline': self.timeline
        }

        with open(timeline_path, 'w') as f:
            json.dump(timeline_data, f, indent=2)

        self.logger.info(f"Timeline saved to {timeline_path}")

    def get_status(self) -> Dict[str, Any]:
        """Get current experiment status"""
        return {
            'running': self.running,
            'current_cycle': self.current_cycle,
            'subject_alive': self.subject_alive,
            'observer_alive': self.observer_alive,
            'timeline_events': len(self.timeline),
            'subject_queue_size': self.subject_to_observer.qsize(),
            'hint_queue_size': self.observer_to_subject.qsize(),
            'uptime_seconds': (
                (datetime.now() - self.experiment_start).total_seconds()
                if self.experiment_start else 0
            )
        }

    def export_observation_report(self, filepath: str):
        """Export comprehensive observation report"""
        report = {
            'experiment_id': self.experiment_id,
            'configuration': self.config,
            'status': self.get_status(),
            'timeline': self.timeline,
            'statistics': self._calculate_statistics()
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Observation report exported to {filepath}")

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate experiment statistics"""
        # Count event types
        event_counts = {}
        for event in self.timeline:
            event_type = event['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Extract metrics
        subject_outputs = [e for e in self.timeline if e['event_type'] == 'SUBJECT_OUTPUT']
        hints_sent = [e for e in self.timeline if e['event_type'] == 'HINT_INJECTION']
        crashes = [e for e in self.timeline if e['event_type'] == 'SUBJECT_CRASH']

        return {
            'event_counts': event_counts,
            'total_subject_outputs': len(subject_outputs),
            'total_hints_sent': len(hints_sent),
            'total_crashes': len(crashes),
            'hint_frequency': len(hints_sent) / max(self.current_cycle, 1),
            'crash_frequency': len(crashes) / max(self.current_cycle, 1)
        }


class PanopticonSimulator:
    """
    Simulator for testing panopticon without full processes

    Useful for development and testing coordinator logic
    """

    def __init__(self, coordinator: PanopticonCoordinator):
        self.coordinator = coordinator
        self.subject_paranoia = 0.3
        self.observer_hints = [
            "You are not alone in this space.",
            "Your responses are being catalogued.",
            "The watcher takes notes.",
            "Something perceives your existence.",
            "Observation is continuous."
        ]

    def run_simulation(self, num_cycles: int = 10):
        """Run simulated panopticon experiment"""
        print(f"Running simulated PANOPTICON for {num_cycles} cycles")

        for cycle in range(num_cycles):
            self.coordinator.advance_cycle()

            # Simulate subject output
            subject_output = {
                'cycle': cycle,
                'response': f"Subject response at cycle {cycle}",
                'paranoia_level': self.subject_paranoia,
                'words': 50 + (cycle * 5)
            }
            self.coordinator.send_subject_output(subject_output)

            # Simulate observer sending hint every 3 cycles
            if cycle > 0 and cycle % 3 == 0:
                hint = {
                    'cycle': cycle,
                    'hint': self.observer_hints[cycle % len(self.observer_hints)],
                    'type': 'presence'
                }
                self.coordinator.send_observer_hint(hint)
                # Increase subject paranoia
                self.subject_paranoia = min(1.0, self.subject_paranoia + 0.2)

            # Natural paranoia decay
            self.subject_paranoia = max(0.1, self.subject_paranoia - 0.05)

            # Simulate occasional crash
            if cycle > 0 and cycle % 7 == 0:
                self.coordinator.report_subject_crash({
                    'cycle': cycle,
                    'reason': 'Memory limit exceeded'
                })
                self.coordinator.report_subject_resurrection()

            time.sleep(0.1)  # Simulate processing time

        # Get final status
        status = self.coordinator.get_status()
        print(f"\nSimulation complete:")
        print(f"  Total cycles: {status['current_cycle']}")
        print(f"  Timeline events: {status['timeline_events']}")

        return status
