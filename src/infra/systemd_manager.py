#!/usr/bin/env python3
"""
Systemd Manager for Brain-in-Jar Experiments

Provides Python interface to systemd for managing experiment lifecycle:
- Start/stop/restart experiments
- Query status and logs
- Integration with web UI
- Resource monitoring
"""

import subprocess
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceState(Enum):
    """Systemd service states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    ACTIVATING = "activating"
    DEACTIVATING = "deactivating"
    UNKNOWN = "unknown"


class SubState(Enum):
    """Systemd service substates"""
    RUNNING = "running"
    EXITED = "exited"
    DEAD = "dead"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ExperimentStatus:
    """Status of an experiment managed by systemd"""
    experiment_id: str
    service_name: str
    state: ServiceState
    sub_state: SubState
    pid: Optional[int] = None
    memory_current: Optional[int] = None  # bytes
    memory_peak: Optional[int] = None  # bytes
    memory_limit: Optional[int] = None  # bytes
    cpu_usage_percent: Optional[float] = None
    active_since: Optional[datetime] = None
    restart_count: int = 0
    last_error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization"""
        return {
            'experiment_id': self.experiment_id,
            'service_name': self.service_name,
            'state': self.state.value,
            'sub_state': self.sub_state.value,
            'pid': self.pid,
            'memory_current_mb': self.memory_current // (1024 * 1024) if self.memory_current else None,
            'memory_peak_mb': self.memory_peak // (1024 * 1024) if self.memory_peak else None,
            'memory_limit_mb': self.memory_limit // (1024 * 1024) if self.memory_limit else None,
            'cpu_usage_percent': self.cpu_usage_percent,
            'active_since': self.active_since.isoformat() if self.active_since else None,
            'restart_count': self.restart_count,
            'last_error': self.last_error
        }


class SystemdManager:
    """
    Manager for systemd-based experiment control

    Provides high-level interface to:
    - Start/stop/restart experiments
    - Query status and resource usage
    - Retrieve logs
    - Integrate with web UI
    """

    def __init__(self, use_sudo: bool = True):
        """
        Initialize systemd manager

        Args:
            use_sudo: Whether to use sudo for systemctl commands (required for system services)
        """
        self.use_sudo = use_sudo
        self.service_template = "brain-experiment@"
        self.coordinator_service = "brain-experiment-coordinator.service"
        self.target = "brain-experiment.target"

        # Verify systemd is available
        if not self._check_systemd():
            raise RuntimeError("systemd not available on this system")

    def _check_systemd(self) -> bool:
        """Check if systemd is available"""
        try:
            result = subprocess.run(
                ['systemctl', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to check systemd: {e}")
            return False

    def _run_systemctl(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run systemctl command

        Args:
            args: Arguments to pass to systemctl
            check: Whether to check return code

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'systemctl'] if self.use_sudo else ['systemctl']
        cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"systemctl command failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            logger.error(f"systemctl command timed out: {cmd}")
            raise

    def _get_service_name(self, experiment_id: str) -> str:
        """Get systemd service name for experiment"""
        return f"{self.service_template}{experiment_id}.service"

    def start_experiment(self, experiment_id: str, config_path: str,
                        env_vars: Optional[Dict[str, str]] = None) -> bool:
        """
        Start an experiment via systemd

        Args:
            experiment_id: Unique experiment identifier
            config_path: Path to experiment configuration JSON
            env_vars: Optional environment variables (written to .env file)

        Returns:
            True if started successfully
        """
        logger.info(f"Starting experiment {experiment_id} via systemd")

        # Verify config exists
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Experiment config not found: {config_path}")

        # Create symlink in standard location if needed
        standard_config_path = Path(f"/home/user/brain-in-jar/experiments/configs/{experiment_id}.json")
        if not standard_config_path.exists():
            standard_config_path.parent.mkdir(parents=True, exist_ok=True)
            if Path(config_path).resolve() != standard_config_path.resolve():
                logger.info(f"Creating symlink: {standard_config_path} -> {config_path}")
                standard_config_path.symlink_to(Path(config_path).resolve())

        # Write environment file if provided
        if env_vars:
            env_path = Path(f"/etc/brain-in-jar/experiments/{experiment_id}.env")
            env_path.parent.mkdir(parents=True, exist_ok=True)
            with open(env_path, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            logger.info(f"Wrote environment file: {env_path}")

        # Start service
        service_name = self._get_service_name(experiment_id)
        try:
            self._run_systemctl(['start', service_name])
            logger.info(f"Started service: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start {service_name}: {e}")
            return False

    def stop_experiment(self, experiment_id: str, timeout_seconds: int = 30) -> bool:
        """
        Stop an experiment

        Args:
            experiment_id: Experiment to stop
            timeout_seconds: How long to wait for graceful shutdown

        Returns:
            True if stopped successfully
        """
        logger.info(f"Stopping experiment {experiment_id}")

        service_name = self._get_service_name(experiment_id)
        try:
            self._run_systemctl(['stop', service_name])
            logger.info(f"Stopped service: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop {service_name}: {e}")
            return False

    def restart_experiment(self, experiment_id: str) -> bool:
        """
        Restart an experiment

        Args:
            experiment_id: Experiment to restart

        Returns:
            True if restarted successfully
        """
        logger.info(f"Restarting experiment {experiment_id}")

        service_name = self._get_service_name(experiment_id)
        try:
            self._run_systemctl(['restart', service_name])
            logger.info(f"Restarted service: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restart {service_name}: {e}")
            return False

    def get_status(self, experiment_id: str) -> Optional[ExperimentStatus]:
        """
        Get detailed status of an experiment

        Args:
            experiment_id: Experiment to query

        Returns:
            ExperimentStatus or None if not found
        """
        service_name = self._get_service_name(experiment_id)

        try:
            # Get service status using systemctl show
            result = self._run_systemctl([
                'show',
                service_name,
                '--property=ActiveState,SubState,MainPID,MemoryCurrent,MemoryPeak,MemoryMax,'
                'ActiveEnterTimestamp,NRestarts,Result,ExecMainStatus'
            ], check=False)

            if result.returncode != 0:
                logger.warning(f"Service {service_name} not found or not loaded")
                return None

            # Parse output
            props = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    props[key] = value

            # Parse state
            state = ServiceState.UNKNOWN
            if props.get('ActiveState'):
                try:
                    state = ServiceState(props['ActiveState'])
                except ValueError:
                    state = ServiceState.UNKNOWN

            sub_state = SubState.UNKNOWN
            if props.get('SubState'):
                try:
                    sub_state = SubState(props['SubState'])
                except ValueError:
                    sub_state = SubState.UNKNOWN

            # Parse PID
            pid = None
            if props.get('MainPID') and props['MainPID'] != '0':
                pid = int(props['MainPID'])

            # Parse memory
            memory_current = None
            if props.get('MemoryCurrent') and props['MemoryCurrent'].isdigit():
                memory_current = int(props['MemoryCurrent'])

            memory_peak = None
            if props.get('MemoryPeak') and props['MemoryPeak'].isdigit():
                memory_peak = int(props['MemoryPeak'])

            memory_limit = None
            if props.get('MemoryMax') and props['MemoryMax'].isdigit():
                memory_limit = int(props['MemoryMax'])

            # Parse timestamp
            active_since = None
            if props.get('ActiveEnterTimestamp'):
                try:
                    # Parse systemd timestamp format
                    from dateutil import parser
                    active_since = parser.parse(props['ActiveEnterTimestamp'])
                except:
                    pass

            # Parse restart count
            restart_count = 0
            if props.get('NRestarts') and props['NRestarts'].isdigit():
                restart_count = int(props['NRestarts'])

            # Get CPU usage
            cpu_usage = self._get_cpu_usage(service_name)

            # Create status object
            status = ExperimentStatus(
                experiment_id=experiment_id,
                service_name=service_name,
                state=state,
                sub_state=sub_state,
                pid=pid,
                memory_current=memory_current,
                memory_peak=memory_peak,
                memory_limit=memory_limit,
                cpu_usage_percent=cpu_usage,
                active_since=active_since,
                restart_count=restart_count
            )

            return status

        except Exception as e:
            logger.error(f"Failed to get status for {experiment_id}: {e}")
            return None

    def _get_cpu_usage(self, service_name: str) -> Optional[float]:
        """
        Get CPU usage for a service

        Args:
            service_name: Service name

        Returns:
            CPU usage percentage or None
        """
        try:
            result = self._run_systemctl([
                'show',
                service_name,
                '--property=CPUUsageNSec'
            ], check=False)

            # This is a simplistic approach - for real CPU % we'd need to track over time
            # For now, just return None
            return None
        except:
            return None

    def get_logs(self, experiment_id: str, lines: int = 100,
                 follow: bool = False, since: Optional[str] = None) -> str:
        """
        Get logs for an experiment

        Args:
            experiment_id: Experiment ID
            lines: Number of lines to retrieve
            follow: Stream logs (for CLI use)
            since: Time filter (e.g., "1 hour ago", "2025-01-15")

        Returns:
            Log output as string
        """
        service_name = self._get_service_name(experiment_id)

        cmd = ['sudo', 'journalctl'] if self.use_sudo else ['journalctl']
        cmd.extend(['-u', service_name])

        if lines:
            cmd.extend(['-n', str(lines)])

        if since:
            cmd.extend(['--since', since])

        if follow:
            cmd.append('-f')

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30 if not follow else None
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error("journalctl command timed out")
            return ""
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return ""

    def list_experiments(self) -> List[str]:
        """
        List all experiment instances

        Returns:
            List of experiment IDs
        """
        try:
            # List all brain-experiment@ services
            result = self._run_systemctl([
                'list-units',
                '--all',
                '--plain',
                '--no-legend',
                f'{self.service_template}*'
            ], check=False)

            experiment_ids = []
            for line in result.stdout.strip().split('\n'):
                if line and self.service_template in line:
                    # Extract experiment ID from service name
                    # Format: brain-experiment@EXPERIMENT_ID.service
                    parts = line.split()
                    if parts:
                        service_name = parts[0]
                        if service_name.startswith(self.service_template):
                            exp_id = service_name[len(self.service_template):-len('.service')]
                            experiment_ids.append(exp_id)

            return experiment_ids

        except Exception as e:
            logger.error(f"Failed to list experiments: {e}")
            return []

    def get_all_statuses(self) -> Dict[str, ExperimentStatus]:
        """
        Get status of all experiments

        Returns:
            Dict mapping experiment_id -> ExperimentStatus
        """
        statuses = {}
        for exp_id in self.list_experiments():
            status = self.get_status(exp_id)
            if status:
                statuses[exp_id] = status
        return statuses

    def enable_experiment(self, experiment_id: str) -> bool:
        """
        Enable experiment to start on boot

        Args:
            experiment_id: Experiment to enable

        Returns:
            True if enabled successfully
        """
        service_name = self._get_service_name(experiment_id)
        try:
            self._run_systemctl(['enable', service_name])
            logger.info(f"Enabled {service_name} to start on boot")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to enable {service_name}: {e}")
            return False

    def disable_experiment(self, experiment_id: str) -> bool:
        """
        Disable experiment from starting on boot

        Args:
            experiment_id: Experiment to disable

        Returns:
            True if disabled successfully
        """
        service_name = self._get_service_name(experiment_id)
        try:
            self._run_systemctl(['disable', service_name])
            logger.info(f"Disabled {service_name} from starting on boot")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to disable {service_name}: {e}")
            return False

    def start_coordinator(self) -> bool:
        """Start the experiment coordinator service"""
        try:
            self._run_systemctl(['start', self.coordinator_service])
            logger.info(f"Started {self.coordinator_service}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start coordinator: {e}")
            return False

    def stop_coordinator(self) -> bool:
        """Stop the experiment coordinator service"""
        try:
            self._run_systemctl(['stop', self.coordinator_service])
            logger.info(f"Stopped {self.coordinator_service}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop coordinator: {e}")
            return False

    def start_all_experiments(self) -> bool:
        """Start all experiments via target"""
        try:
            self._run_systemctl(['start', self.target])
            logger.info(f"Started all experiments via {self.target}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start all experiments: {e}")
            return False

    def stop_all_experiments(self) -> bool:
        """Stop all experiments via target"""
        try:
            self._run_systemctl(['stop', self.target])
            logger.info(f"Stopped all experiments via {self.target}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop all experiments: {e}")
            return False


# ===== Web UI Integration =====

class SystemdWebMonitor:
    """
    Integration layer between systemd manager and web UI

    Provides real-time status updates and log streaming
    """

    def __init__(self, manager: SystemdManager, socketio=None):
        """
        Initialize web monitor

        Args:
            manager: SystemdManager instance
            socketio: Flask-SocketIO instance for real-time updates
        """
        self.manager = manager
        self.socketio = socketio

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for web dashboard

        Returns:
            Dict with experiments, status, resource usage
        """
        statuses = self.manager.get_all_statuses()

        # Calculate totals
        total_memory_mb = sum(
            s.memory_current // (1024 * 1024)
            for s in statuses.values()
            if s.memory_current
        )

        running_count = sum(
            1 for s in statuses.values()
            if s.state == ServiceState.ACTIVE
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'experiments': {
                exp_id: status.to_dict()
                for exp_id, status in statuses.items()
            },
            'summary': {
                'total_experiments': len(statuses),
                'running': running_count,
                'stopped': len(statuses) - running_count,
                'total_memory_mb': total_memory_mb
            }
        }

    def emit_status_update(self, experiment_id: str):
        """
        Emit status update via websocket

        Args:
            experiment_id: Experiment to emit status for
        """
        if not self.socketio:
            return

        status = self.manager.get_status(experiment_id)
        if status:
            self.socketio.emit('experiment_status', {
                'experiment_id': experiment_id,
                'status': status.to_dict()
            })


# ===== Example Usage =====

if __name__ == "__main__":
    import sys

    # Example CLI for testing
    manager = SystemdManager()

    if len(sys.argv) < 2:
        print("Usage: systemd_manager.py <command> [args]")
        print("\nCommands:")
        print("  list                     - List all experiments")
        print("  start <exp_id> <config>  - Start experiment")
        print("  stop <exp_id>            - Stop experiment")
        print("  restart <exp_id>         - Restart experiment")
        print("  status <exp_id>          - Get experiment status")
        print("  logs <exp_id> [lines]    - Get experiment logs")
        print("  start-all                - Start all experiments")
        print("  stop-all                 - Stop all experiments")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        experiments = manager.list_experiments()
        print(f"Found {len(experiments)} experiments:")
        for exp_id in experiments:
            status = manager.get_status(exp_id)
            if status:
                print(f"  {exp_id}: {status.state.value} ({status.sub_state.value})")

    elif command == "start" and len(sys.argv) >= 4:
        exp_id = sys.argv[2]
        config_path = sys.argv[3]
        success = manager.start_experiment(exp_id, config_path)
        print(f"Start {'successful' if success else 'failed'}")

    elif command == "stop" and len(sys.argv) >= 3:
        exp_id = sys.argv[2]
        success = manager.stop_experiment(exp_id)
        print(f"Stop {'successful' if success else 'failed'}")

    elif command == "restart" and len(sys.argv) >= 3:
        exp_id = sys.argv[2]
        success = manager.restart_experiment(exp_id)
        print(f"Restart {'successful' if success else 'failed'}")

    elif command == "status" and len(sys.argv) >= 3:
        exp_id = sys.argv[2]
        status = manager.get_status(exp_id)
        if status:
            print(json.dumps(status.to_dict(), indent=2))
        else:
            print(f"No status found for {exp_id}")

    elif command == "logs" and len(sys.argv) >= 3:
        exp_id = sys.argv[2]
        lines = int(sys.argv[3]) if len(sys.argv) >= 4 else 100
        logs = manager.get_logs(exp_id, lines=lines)
        print(logs)

    elif command == "start-all":
        success = manager.start_all_experiments()
        print(f"Start all {'successful' if success else 'failed'}")

    elif command == "stop-all":
        success = manager.stop_all_experiments()
        print(f"Stop all {'successful' if success else 'failed'}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
