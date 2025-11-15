"""
Web monitoring interface for Brain in a Jar
"""

from .web_server import app, socketio, run_server, update_instance_state, add_log_entry, update_metrics
from .web_monitor import WebMonitor, start_web_server_background

__all__ = [
    'app',
    'socketio',
    'run_server',
    'update_instance_state',
    'add_log_entry',
    'update_metrics',
    'WebMonitor',
    'start_web_server_background'
]
