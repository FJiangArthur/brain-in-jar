#!/usr/bin/env python3
"""
Experiment Coordinator for Multi-Experiment Management

Master service that:
- Manages experiment queue
- Enforces global resource limits
- Monitors system health (temperature, memory, CPU)
- Handles Jetson Orin specific power/thermal management
- Provides IPC for experiment coordination
"""

import asyncio
import logging
import json
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SystemResources:
    """Current system resource usage"""
    total_ram_gb: float
    used_ram_gb: float
    available_ram_gb: float
    cpu_percent: float
    temperature_celsius: Optional[float] = None
    gpu_temp_celsius: Optional[float] = None
    power_mode: Optional[str] = None  # Jetson nvpmodel mode


@dataclass
class ExperimentQueueItem:
    """Item in experiment queue"""
    experiment_id: str
    config_path: str
    priority: int = 0
    queued_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    env_vars: Dict[str, str] = field(default_factory=dict)


class ExperimentCoordinator:
    """
    Coordinator service for managing multiple experiments

    Responsibilities:
    - Queue management
    - Resource enforcement
    - Health monitoring
    - Thermal management (Jetson Orin)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize coordinator

        Args:
            config_path: Path to coordinator config (optional)
        """
        self.config = self._load_config(config_path)
        self.queue: List[ExperimentQueueItem] = []
        self.running = False

        # Limits from config
        self.max_concurrent = self.config.get('max_concurrent_experiments', 4)
        self.total_ram_limit_gb = self.config.get('total_ram_limit_gb', 48)
        self.throttle_temp = self.config.get('throttle_temp_celsius', 75)
        self.critical_temp = self.config.get('critical_temp_celsius', 85)

        # State
        self.is_jetson = self._detect_jetson()
        self.queue_file = Path(self.config.get(
            'experiment_queue_path',
            '/home/user/brain-in-jar/logs/experiment_queue.json'
        ))

        # Load queue from disk
        self._load_queue()

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration"""
        # Default config
        config = {
            'max_concurrent_experiments': 4,
            'total_ram_limit_gb': 48,
            'health_check_interval_seconds': 30,
            'temperature_check_interval_seconds': 10,
            'throttle_temp_celsius': 75,
            'critical_temp_celsius': 85,
            'experiment_queue_path': '/home/user/brain-in-jar/logs/experiment_queue.json'
        }

        # Load from env file if exists
        env_file = Path('/etc/brain-in-jar/coordinator.env')
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.lower()
                        if key in config:
                            # Try to parse as appropriate type
                            if isinstance(config[key], int):
                                config[key] = int(value)
                            elif isinstance(config[key], float):
                                config[key] = float(value)
                            else:
                                config[key] = value

        return config

    def _detect_jetson(self) -> bool:
        """Detect if running on Jetson Orin"""
        return Path('/etc/nv_tegra_release').exists()

    def _load_queue(self):
        """Load queue from disk"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file) as f:
                    data = json.load(f)
                    # Reconstruct queue items
                    for item_data in data:
                        self.queue.append(ExperimentQueueItem(
                            experiment_id=item_data['experiment_id'],
                            config_path=item_data['config_path'],
                            priority=item_data.get('priority', 0),
                            queued_at=datetime.fromisoformat(item_data['queued_at']),
                            env_vars=item_data.get('env_vars', {})
                        ))
                logger.info(f"Loaded {len(self.queue)} items from queue")
            except Exception as e:
                logger.error(f"Failed to load queue: {e}")

    def _save_queue(self):
        """Save queue to disk"""
        try:
            self.queue_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.queue_file, 'w') as f:
                data = [
                    {
                        'experiment_id': item.experiment_id,
                        'config_path': item.config_path,
                        'priority': item.priority,
                        'queued_at': item.queued_at.isoformat(),
                        'started_at': item.started_at.isoformat() if item.started_at else None,
                        'env_vars': item.env_vars
                    }
                    for item in self.queue
                ]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save queue: {e}")

    def _get_system_resources(self) -> SystemResources:
        """Get current system resource usage"""
        try:
            import psutil

            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)

            resources = SystemResources(
                total_ram_gb=mem.total / (1024**3),
                used_ram_gb=mem.used / (1024**3),
                available_ram_gb=mem.available / (1024**3),
                cpu_percent=cpu
            )

            # Get temperature (Jetson Orin specific)
            if self.is_jetson:
                try:
                    # Read thermal zones
                    thermal_zone = Path('/sys/class/thermal/thermal_zone0/temp')
                    if thermal_zone.exists():
                        temp = int(thermal_zone.read_text().strip()) / 1000.0
                        resources.temperature_celsius = temp
                except:
                    pass

            return resources

        except ImportError:
            logger.warning("psutil not available, using placeholder values")
            return SystemResources(
                total_ram_gb=64.0,
                used_ram_gb=8.0,
                available_ram_gb=56.0,
                cpu_percent=20.0
            )

    async def _health_check_loop(self):
        """Periodic health check"""
        interval = self.config.get('health_check_interval_seconds', 30)

        while self.running:
            try:
                resources = self._get_system_resources()

                logger.info(
                    f"Health: RAM {resources.used_ram_gb:.1f}/{resources.total_ram_gb:.1f}GB, "
                    f"CPU {resources.cpu_percent:.1f}%"
                    + (f", Temp {resources.temperature_celsius:.1f}°C"
                       if resources.temperature_celsius else "")
                )

                # Check for critical conditions
                if resources.temperature_celsius and resources.temperature_celsius > self.critical_temp:
                    logger.error(
                        f"CRITICAL TEMPERATURE: {resources.temperature_celsius:.1f}°C "
                        f"(threshold: {self.critical_temp}°C)"
                    )
                    # In production: pause experiments or trigger emergency shutdown

                elif resources.temperature_celsius and resources.temperature_celsius > self.throttle_temp:
                    logger.warning(
                        f"High temperature: {resources.temperature_celsius:.1f}°C "
                        f"(throttle threshold: {self.throttle_temp}°C)"
                    )
                    # In production: reduce resource limits or pause new experiments

                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(interval)

    async def _queue_processor_loop(self):
        """Process experiment queue"""
        while self.running:
            try:
                # Process queue (placeholder - actual implementation would use systemd_manager)
                if self.queue:
                    logger.info(f"Queue has {len(self.queue)} items (processing not yet implemented)")

                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                await asyncio.sleep(10)

    def _handle_signal(self, signum, frame):
        """Handle shutdown signal"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def run(self):
        """Main run loop"""
        logger.info("Experiment Coordinator starting...")
        logger.info(f"Max concurrent experiments: {self.max_concurrent}")
        logger.info(f"Total RAM limit: {self.total_ram_limit_gb}GB")
        logger.info(f"Running on Jetson: {self.is_jetson}")

        self.running = True

        # Start background tasks
        tasks = [
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._queue_processor_loop())
        ]

        # Wait for shutdown
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Tasks cancelled")

        # Cleanup
        self._save_queue()
        logger.info("Coordinator shut down cleanly")


async def main():
    """Main entry point"""
    coordinator = ExperimentCoordinator()
    await coordinator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
