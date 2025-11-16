#!/usr/bin/env python3
"""
Web Monitor Integration for Neural Link
Bridges the neural link system with the web server for real-time monitoring
"""

import threading
import time
from datetime import datetime

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
            'cpu_usage': state.get('cpu_usage', 0),
            'gpu_memory': state.get('gpu_memory', None),
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
