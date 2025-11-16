#!/usr/bin/env python3
"""
Remote Runner for SSH-based Experiment Execution

Executes experiments on remote nodes via SSH:
- Deploy code to remote node
- Start experiment runner
- Monitor via SSH tunnel
- Stream logs back to coordinator
- Handle crashes and cleanup
"""

import asyncio
import asyncssh
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import tarfile
import io


logger = logging.getLogger(__name__)


class RemoteRunner:
    """
    Executes experiments on remote nodes via SSH

    Features:
    - Code deployment via rsync or tar
    - Remote process management
    - Log streaming
    - Port forwarding for monitoring
    - Automatic cleanup
    """

    def __init__(self, host: str, username: str, port: int = 22,
                 key_path: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize remote runner

        Args:
            host: SSH host (IP or hostname)
            username: SSH username
            port: SSH port (default 22)
            key_path: Path to SSH private key (optional)
            password: SSH password (optional, prefer keys)
        """
        self.host = host
        self.username = username
        self.port = port
        self.key_path = key_path
        self.password = password

        self.connection: Optional[asyncssh.SSHClientConnection] = None
        self.processes: Dict[str, asyncssh.SSHClientProcess] = {}

    async def connect(self):
        """Establish SSH connection"""
        try:
            logger.info(f"Connecting to {self.username}@{self.host}:{self.port}...")

            # Build connection options
            options = {
                'host': self.host,
                'port': self.port,
                'username': self.username,
                'known_hosts': None  # Disable host key checking (for lab environment)
            }

            if self.key_path:
                options['client_keys'] = [self.key_path]
            elif self.password:
                options['password'] = self.password

            self.connection = await asyncssh.connect(**options)
            logger.info(f"Connected to {self.host}")

        except Exception as e:
            logger.error(f"Failed to connect to {self.host}: {e}")
            raise

    async def disconnect(self):
        """Close SSH connection"""
        if self.connection:
            # Kill all running processes
            for proc_name, proc in self.processes.items():
                logger.info(f"Terminating process: {proc_name}")
                proc.terminate()

            self.connection.close()
            await self.connection.wait_closed()
            logger.info(f"Disconnected from {self.host}")

    async def execute_command(self, command: str, timeout: Optional[int] = 30) -> Dict[str, Any]:
        """
        Execute a single command and wait for completion

        Args:
            command: Shell command to execute
            timeout: Timeout in seconds (None = no timeout)

        Returns:
            Dict with 'success', 'stdout', 'stderr', 'exit_code'
        """
        if not self.connection:
            await self.connect()

        try:
            result = await asyncio.wait_for(
                self.connection.run(command, check=False),
                timeout=timeout
            )

            return {
                'success': result.exit_status == 0,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'exit_code': result.exit_status
            }

        except asyncio.TimeoutError:
            logger.error(f"Command timed out: {command}")
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'exit_code': -1
            }
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1
            }

    async def deploy_code(self, local_path: str, remote_path: str,
                         exclude: Optional[List[str]] = None) -> bool:
        """
        Deploy code to remote node using rsync over SSH

        Args:
            local_path: Local directory to deploy
            remote_path: Remote destination directory
            exclude: List of patterns to exclude (optional)

        Returns:
            True if successful
        """
        logger.info(f"Deploying {local_path} -> {self.host}:{remote_path}")

        # Build rsync command
        exclude_args = []
        if exclude:
            for pattern in exclude:
                exclude_args.extend(['--exclude', pattern])

        rsync_cmd = [
            'rsync',
            '-avz',
            '--delete',
            *exclude_args,
            '-e', f'ssh -p {self.port} -o StrictHostKeyChecking=no',
            f'{local_path}/',
            f'{self.username}@{self.host}:{remote_path}/'
        ]

        # Run rsync locally (not over SSH)
        proc = await asyncio.create_subprocess_exec(
            *rsync_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            logger.info(f"Deployment successful: {remote_path}")
            return True
        else:
            logger.error(f"Deployment failed: {stderr.decode()}")
            return False

    async def start_experiment(self, experiment_config: str, remote_work_dir: str,
                              instance_id: str, db_path: str = "logs/experiments.db") -> str:
        """
        Start an experiment on the remote node

        Args:
            experiment_config: Path to experiment config (relative to remote_work_dir)
            remote_work_dir: Working directory on remote node
            instance_id: Unique instance identifier
            db_path: Path to database on remote node

        Returns:
            Process ID key for tracking
        """
        if not self.connection:
            await self.connect()

        logger.info(f"Starting experiment {instance_id} on {self.host}")

        # Build command
        cmd = (
            f"cd {remote_work_dir} && "
            f"python3 -m src.runner.experiment_runner "
            f"--config {experiment_config} "
            f"--db {db_path} "
            f"> logs/{instance_id}.log 2>&1"
        )

        # Start process in background
        process = await self.connection.create_process(cmd)

        # Store process reference
        self.processes[instance_id] = process

        logger.info(f"Experiment {instance_id} started (PID: {process.get_pid()})")

        return instance_id

    async def monitor_experiment(self, instance_id: str,
                                callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Monitor a running experiment

        Args:
            instance_id: Instance identifier
            callback: Optional callback for log lines

        Returns:
            Dict with 'running', 'exit_code', 'output'
        """
        if instance_id not in self.processes:
            logger.error(f"No process found for {instance_id}")
            return {'running': False, 'exit_code': -1, 'output': ''}

        process = self.processes[instance_id]

        # Check if still running
        if process.exit_status is not None:
            return {
                'running': False,
                'exit_code': process.exit_status,
                'output': ''
            }

        return {
            'running': True,
            'exit_code': None,
            'output': ''
        }

    async def stream_logs(self, instance_id: str, remote_work_dir: str,
                         callback: callable):
        """
        Stream logs from remote experiment

        Args:
            instance_id: Instance identifier
            remote_work_dir: Working directory on remote
            callback: Function to call with each log line
        """
        log_path = f"{remote_work_dir}/logs/{instance_id}.log"

        # Use tail -f to stream logs
        cmd = f"tail -f {log_path}"

        process = await self.connection.create_process(cmd)

        try:
            async for line in process.stdout:
                callback(line.strip())

        except Exception as e:
            logger.error(f"Log streaming error: {e}")

    async def stop_experiment(self, instance_id: str, graceful: bool = True) -> bool:
        """
        Stop a running experiment

        Args:
            instance_id: Instance identifier
            graceful: If True, send SIGTERM; if False, send SIGKILL

        Returns:
            True if stopped successfully
        """
        if instance_id not in self.processes:
            logger.warning(f"No process found for {instance_id}")
            return False

        process = self.processes[instance_id]

        try:
            if graceful:
                logger.info(f"Stopping {instance_id} gracefully (SIGTERM)...")
                process.terminate()
            else:
                logger.info(f"Killing {instance_id} (SIGKILL)...")
                process.kill()

            # Wait for termination (with timeout)
            await asyncio.wait_for(process.wait(), timeout=30)

            logger.info(f"Experiment {instance_id} stopped")
            del self.processes[instance_id]
            return True

        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for {instance_id} to stop")
            process.kill()  # Force kill
            return False

        except Exception as e:
            logger.error(f"Error stopping {instance_id}: {e}")
            return False

    async def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information from remote node

        Returns:
            Dict with CPU, RAM, GPU info
        """
        if not self.connection:
            await self.connect()

        info = {}

        # CPU info
        result = await self.execute_command("nproc")
        if result['success']:
            info['cpu_cores'] = int(result['stdout'])

        # RAM info (GB)
        result = await self.execute_command("free -g | grep Mem | awk '{print $2}'")
        if result['success']:
            info['ram_total_gb'] = float(result['stdout'])

        result = await self.execute_command("free -g | grep Mem | awk '{print $3}'")
        if result['success']:
            info['ram_used_gb'] = float(result['stdout'])

        # GPU info (if available)
        result = await self.execute_command("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits")
        if result['success']:
            try:
                info['gpu_memory_mb'] = int(result['stdout'])
                info['gpu_available'] = True
            except ValueError:
                info['gpu_available'] = False
        else:
            info['gpu_available'] = False

        # Disk info
        result = await self.execute_command("df -h / | tail -1 | awk '{print $4}'")
        if result['success']:
            info['disk_available'] = result['stdout']

        return info

    async def setup_port_forwarding(self, remote_port: int, local_port: int):
        """
        Setup SSH port forwarding

        Args:
            remote_port: Port on remote host
            local_port: Port on local host
        """
        if not self.connection:
            await self.connect()

        logger.info(f"Forwarding localhost:{local_port} -> {self.host}:{remote_port}")

        listener = await self.connection.forward_local_port(
            '', local_port,
            self.host, remote_port
        )

        return listener

    async def fetch_file(self, remote_path: str, local_path: str) -> bool:
        """
        Fetch a file from remote node

        Args:
            remote_path: Path on remote node
            local_path: Local destination path

        Returns:
            True if successful
        """
        if not self.connection:
            await self.connect()

        try:
            async with self.connection.start_sftp_client() as sftp:
                await sftp.get(remote_path, local_path)
                logger.info(f"Downloaded {remote_path} -> {local_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to fetch {remote_path}: {e}")
            return False

    async def put_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload a file to remote node

        Args:
            local_path: Local file path
            remote_path: Destination on remote node

        Returns:
            True if successful
        """
        if not self.connection:
            await self.connect()

        try:
            async with self.connection.start_sftp_client() as sftp:
                await sftp.put(local_path, remote_path)
                logger.info(f"Uploaded {local_path} -> {remote_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False


# ===== Convenience Functions =====

async def deploy_and_run(host: str, username: str,
                        local_code_dir: str, remote_work_dir: str,
                        experiment_config: str, instance_id: str,
                        ssh_key_path: Optional[str] = None) -> RemoteRunner:
    """
    Deploy code and start experiment (convenience function)

    Args:
        host: Remote host
        username: SSH username
        local_code_dir: Local code directory to deploy
        remote_work_dir: Remote working directory
        experiment_config: Experiment config path (relative to work dir)
        instance_id: Unique instance ID
        ssh_key_path: SSH key path (optional)

    Returns:
        RemoteRunner instance
    """
    runner = RemoteRunner(host, username, ssh_key_path=ssh_key_path)

    await runner.connect()

    # Deploy code
    exclude = [
        '*.pyc',
        '__pycache__',
        '.git',
        'logs/*',
        'test_outputs/*',
        '*.db'
    ]

    await runner.deploy_code(local_code_dir, remote_work_dir, exclude=exclude)

    # Create logs directory
    await runner.execute_command(f"mkdir -p {remote_work_dir}/logs")

    # Start experiment
    await runner.start_experiment(experiment_config, remote_work_dir, instance_id)

    return runner


# ===== Example Usage =====

async def main():
    """Example: Run experiment on remote Jetson"""

    # Initialize runner
    runner = RemoteRunner(
        host='192.168.1.100',  # Jetson IP
        username='jetson',
        ssh_key_path='~/.ssh/id_rsa'
    )

    try:
        # Connect
        await runner.connect()

        # Get system info
        info = await runner.get_system_info()
        print("Remote System Info:")
        print(json.dumps(info, indent=2))

        # Deploy code
        await runner.deploy_code(
            local_path='/home/user/brain-in-jar',
            remote_path='/home/jetson/brain-in-jar',
            exclude=['*.pyc', '__pycache__', '.git', 'logs/*']
        )

        # Start experiment
        await runner.start_experiment(
            experiment_config='experiments/examples/split_brain_001_brain_A.json',
            remote_work_dir='/home/jetson/brain-in-jar',
            instance_id='split_brain_A_jetson'
        )

        # Monitor for 10 seconds
        for i in range(10):
            await asyncio.sleep(1)
            status = await runner.monitor_experiment('split_brain_A_jetson')
            print(f"Status: {status}")

        # Stop experiment
        await runner.stop_experiment('split_brain_A_jetson')

    finally:
        await runner.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
