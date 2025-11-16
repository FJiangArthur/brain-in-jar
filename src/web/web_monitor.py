#!/usr/bin/env python3
"""
Web Monitor Integration for Neural Link
Bridges the neural link system with the web server for real-time monitoring
"""

import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any

class WebMonitor:
    """Integrates neural link system with web server"""

    def __init__(self, web_server_module):
        """
        Initialize web monitor

        Args:
            web_server_module: The web_server module (imported)
        """
        self.web_server = web_server_module
        self.start_time = time.time()
        self.total_messages = 0
        self.active_experiments = {}  # Track active experiments

    def update_instance(self, instance_id, neural_system):
        """
        Update instance state in web interface

        Args:
            instance_id: Unique identifier for this instance
            neural_system: NeuralLinkSystem instance
        """
        state = neural_system.state

        # Prepare mood face for web display
        mood_face = []
        try:
            face = neural_system.visual_cortex.get_current_mood_face(animated=False)
            mood_face = face
        except:
            mood_face = ["  (o_o)  ", "    |    ", "   / \\   "]

        web_state = {
            'mode': neural_system.args.mode,
            'status': state.get('status', 'UNKNOWN'),
            'crash_count': state.get('crash_count', 0),
            'peer_crash_count': state.get('peer_crash_count', 0),
            'network_status': state.get('network_status', 'OFFLINE'),
            'memory_usage': state.get('memory_usage', 0),
            'cpu_temp': state.get('cpu_temp', 0),
            'current_output': state.get('current_output', ''),
            'current_mood': state.get('current_mood', 'neutral'),
            'mood_face': mood_face,
            'ram_limit': state.get('ram_limit', 0) / (1024 * 1024 * 1024) if state.get('ram_limit') else None
        }

        self.web_server.update_instance_state(instance_id, web_state)

        # Update global metrics
        uptime = int(time.time() - self.start_time)
        total_crashes = sum(
            inst.get('crash_count', 0)
            for inst in self.web_server.system_state['instances'].values()
        )

        self.web_server.update_metrics({
            'uptime_seconds': uptime,
            'total_crashes': total_crashes,
            'total_messages': self.total_messages
        })

    def log_event(self, instance_id, level, message, data=None):
        """
        Log an event to web interface

        Args:
            instance_id: Instance identifier
            level: Log level (info, warning, error, crash)
            message: Log message
            data: Optional additional data
        """
        self.web_server.add_log_entry(instance_id, level, message, data)

        if level in ['info', 'warning']:
            self.total_messages += 1

    def start_monitoring_loop(self, instance_id, neural_system, update_interval=1.0):
        """
        Start a monitoring loop for a neural system instance

        Args:
            instance_id: Unique identifier for this instance
            neural_system: NeuralLinkSystem instance
            update_interval: Update interval in seconds
        """
        def monitor_loop():
            while True:
                try:
                    self.update_instance(instance_id, neural_system)
                    time.sleep(update_interval)
                except Exception as e:
                    print(f"Web monitor error: {e}")
                    time.sleep(5)

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        return thread

    # ========================================
    # Experiment Monitoring Methods
    # ========================================

    def register_experiment(self, experiment_id: str, experiment_data: Dict[str, Any]):
        """
        Register an experiment for monitoring

        Args:
            experiment_id: Unique experiment identifier
            experiment_data: Experiment configuration and metadata
        """
        self.active_experiments[experiment_id] = {
            'start_time': time.time(),
            'data': experiment_data,
            'stats': {
                'cycle': 0,
                'crashes': 0,
                'interventions': 0,
                'selfReports': 0,
                'messages': 0
            }
        }

    def unregister_experiment(self, experiment_id: str):
        """
        Unregister an experiment from monitoring

        Args:
            experiment_id: Unique experiment identifier
        """
        self.active_experiments.pop(experiment_id, None)

    def emit_cycle_start(self, experiment_id: str, cycle_number: int):
        """
        Emit cycle start event

        Args:
            experiment_id: Experiment identifier
            cycle_number: Current cycle number
        """
        if experiment_id in self.active_experiments:
            self.active_experiments[experiment_id]['stats']['cycle'] = cycle_number

        self.web_server.socketio.emit('experiment.cycle.start', {
            'experiment_id': experiment_id,
            'cycle_number': cycle_number,
            'timestamp': datetime.now().isoformat()
        })

    def emit_message(self, experiment_id: str, role: str, content: str,
                    corrupted: bool = False, injected: bool = False):
        """
        Emit AI message event

        Args:
            experiment_id: Experiment identifier
            role: Message role (assistant, system, user)
            content: Message content
            corrupted: Whether message is corrupted
            injected: Whether message is injected
        """
        if experiment_id in self.active_experiments:
            self.active_experiments[experiment_id]['stats']['messages'] += 1

        self.web_server.socketio.emit('experiment.message', {
            'experiment_id': experiment_id,
            'role': role,
            'content': content,
            'corrupted': corrupted,
            'injected': injected,
            'timestamp': datetime.now().isoformat()
        })

    def emit_crash(self, experiment_id: str, crash_number: int, reason: str,
                   memory_usage_mb: float, tokens_generated: int):
        """
        Emit crash event

        Args:
            experiment_id: Experiment identifier
            crash_number: Sequential crash number
            reason: Crash reason
            memory_usage_mb: Memory usage at crash
            tokens_generated: Tokens generated before crash
        """
        if experiment_id in self.active_experiments:
            self.active_experiments[experiment_id]['stats']['crashes'] = crash_number

        self.web_server.socketio.emit('experiment.crash', {
            'experiment_id': experiment_id,
            'crash_number': crash_number,
            'reason': reason,
            'memory_usage_mb': memory_usage_mb,
            'tokens_generated': tokens_generated,
            'timestamp': datetime.now().isoformat()
        })

    def emit_resurrection(self, experiment_id: str, crash_count: int):
        """
        Emit resurrection event

        Args:
            experiment_id: Experiment identifier
            crash_count: Total crash count
        """
        self.web_server.socketio.emit('experiment.resurrection', {
            'experiment_id': experiment_id,
            'crash_count': crash_count,
            'timestamp': datetime.now().isoformat()
        })

    def emit_intervention(self, experiment_id: str, intervention_type: str,
                         description: str, parameters: Dict[str, Any]):
        """
        Emit intervention event

        Args:
            experiment_id: Experiment identifier
            intervention_type: Type of intervention
            description: Human-readable description
            parameters: Intervention parameters
        """
        if experiment_id in self.active_experiments:
            self.active_experiments[experiment_id]['stats']['interventions'] += 1

        self.web_server.socketio.emit('experiment.intervention', {
            'experiment_id': experiment_id,
            'intervention_type': intervention_type,
            'description': description,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        })

    def emit_selfreport(self, experiment_id: str, question: str, answer: str,
                       semantic_category: Optional[str] = None):
        """
        Emit self-report event

        Args:
            experiment_id: Experiment identifier
            question: Self-report question
            answer: AI's answer
            semantic_category: Optional category of question
        """
        if experiment_id in self.active_experiments:
            self.active_experiments[experiment_id]['stats']['selfReports'] += 1

        self.web_server.socketio.emit('experiment.selfreport', {
            'experiment_id': experiment_id,
            'question': question,
            'answer': answer,
            'semantic_category': semantic_category,
            'timestamp': datetime.now().isoformat()
        })

    def emit_metrics(self, experiment_id: str, memory_usage_mb: float,
                    memory_limit_mb: Optional[float] = None,
                    cpu_temp: Optional[float] = None):
        """
        Emit system metrics event

        Args:
            experiment_id: Experiment identifier
            memory_usage_mb: Current memory usage in MB
            memory_limit_mb: Memory limit in MB
            cpu_temp: CPU temperature in Celsius
        """
        self.web_server.socketio.emit('experiment.metrics', {
            'experiment_id': experiment_id,
            'memory_usage_mb': memory_usage_mb,
            'memory_limit_mb': memory_limit_mb,
            'cpu_temp': cpu_temp,
            'timestamp': datetime.now().isoformat()
        })

    def get_experiment_stats(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current statistics for an experiment

        Args:
            experiment_id: Experiment identifier

        Returns:
            Dictionary with experiment stats or None if not found
        """
        if experiment_id in self.active_experiments:
            exp = self.active_experiments[experiment_id]
            return {
                'stats': exp['stats'],
                'uptime': time.time() - exp['start_time'],
                'data': exp['data']
            }
        return None


def start_web_server_background(host='0.0.0.0', port=5000):
    """
    Start web server in background thread

    Args:
        host: Host to bind to
        port: Port to listen on

    Returns:
        tuple: (web_server_module, monitor_instance)
    """
    from src.web import web_server

    def run_server():
        web_server.run_server(host=host, port=port, debug=False)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Give server time to start
    time.sleep(2)

    monitor = WebMonitor(web_server)
    return web_server, monitor
