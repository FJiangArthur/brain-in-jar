#!/usr/bin/env python3
"""
Cluster Orchestrator for Multi-Node Experiments

Distributes experiment instances across heterogeneous compute nodes:
- Jetson Orin AGX: 64GB RAM, CUDA support, can run 3-4 instances
- Raspberry Pi 5: 8GB RAM, CPU-only, can run 1 instance
- Host machine: Variable resources, can run multiple instances

Features:
- Intelligent placement based on RAM, GPU, network topology
- SSH-based remote execution
- Node health monitoring
- Automatic failover and rebalancing
"""

import yaml
import asyncio
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set
from pathlib import Path
from datetime import datetime
from enum import Enum
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Type of compute node"""
    JETSON_ORIN = "jetson_orin"
    RASPBERRY_PI = "raspberry_pi"
    HOST = "host"
    GENERIC = "generic"


class NodeStatus(Enum):
    """Node health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"  # Overloaded but functional
    UNAVAILABLE = "unavailable"  # Unreachable or failed
    MAINTENANCE = "maintenance"  # Manually disabled


class InstanceStatus(Enum):
    """Status of experiment instance"""
    PENDING = "pending"
    RUNNING = "running"
    CRASHED = "crashed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class NodeConfig:
    """Configuration for a compute node"""
    name: str
    host: str
    node_type: NodeType
    ram_gb: float
    gpu: bool = False
    gpu_memory_gb: float = 0.0
    cpu_cores: int = 4

    # Network
    ssh_port: int = 22
    ssh_user: str = "user"
    ssh_key_path: Optional[str] = None

    # Limits
    max_instances: int = 1
    reserved_ram_gb: float = 1.0  # OS overhead

    # Runtime state (not in config)
    status: NodeStatus = field(default=NodeStatus.HEALTHY)
    current_instances: int = field(default=0)
    allocated_ram_gb: float = field(default=0.0)
    allocated_gpu_memory_gb: float = field(default=0.0)
    last_health_check: Optional[datetime] = None

    @property
    def available_ram_gb(self) -> float:
        """RAM available for new allocations"""
        return self.ram_gb - self.reserved_ram_gb - self.allocated_ram_gb

    @property
    def available_gpu_memory_gb(self) -> float:
        """GPU memory available for new allocations"""
        if not self.gpu:
            return 0.0
        return self.gpu_memory_gb - self.allocated_gpu_memory_gb

    @property
    def can_accept_instance(self) -> bool:
        """Can this node accept another instance?"""
        return (
            self.status == NodeStatus.HEALTHY and
            self.current_instances < self.max_instances and
            self.available_ram_gb > 0
        )

    @property
    def is_localhost(self) -> bool:
        """Is this the local host?"""
        return self.host in ('localhost', '127.0.0.1', '::1')

    def to_dict(self) -> Dict:
        """Convert to dict for serialization"""
        d = asdict(self)
        d['node_type'] = self.node_type.value
        d['status'] = self.status.value
        if self.last_health_check:
            d['last_health_check'] = self.last_health_check.isoformat()
        return d


@dataclass
class ExperimentInstance:
    """Single experiment instance to be scheduled"""
    instance_id: str
    experiment_config_path: str

    # Resource requirements
    ram_gb: float
    gpu_required: bool = False
    gpu_memory_gb: float = 0.0

    # Placement hints
    preferred_node: Optional[str] = None
    anti_affinity: List[str] = field(default_factory=list)  # Don't place with these instances
    affinity: List[str] = field(default_factory=list)  # Prefer to place with these instances

    # Runtime state
    status: InstanceStatus = InstanceStatus.PENDING
    assigned_node: Optional[str] = None
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['status'] = self.status.value
        if self.start_time:
            d['start_time'] = self.start_time.isoformat()
        if self.end_time:
            d['end_time'] = self.end_time.isoformat()
        return d


class PlacementStrategy:
    """Strategy for placing instances on nodes"""

    @staticmethod
    def score_node(node: NodeConfig, instance: ExperimentInstance,
                   current_placements: Dict[str, str]) -> float:
        """
        Score a node for placing an instance (higher = better)

        Scoring factors:
        - Resource fit (RAM, GPU)
        - Current load
        - Network locality (affinity/anti-affinity)
        - Node type preferences

        Returns:
            Score (0-100), or -1 if placement impossible
        """

        # Check hard constraints
        if not node.can_accept_instance:
            return -1.0

        if instance.ram_gb > node.available_ram_gb:
            return -1.0

        if instance.gpu_required and not node.gpu:
            return -1.0

        if instance.gpu_required and instance.gpu_memory_gb > node.available_gpu_memory_gb:
            return -1.0

        # Start scoring
        score = 0.0

        # 1. Resource efficiency (0-30 points)
        # Prefer nodes where this instance uses 30-70% of available resources
        ram_utilization = instance.ram_gb / node.available_ram_gb
        if 0.3 <= ram_utilization <= 0.7:
            score += 30.0
        elif ram_utilization < 0.3:
            score += 20.0  # Slightly wasteful
        else:
            score += 10.0  # Will be tight

        # 2. Load balancing (0-20 points)
        # Prefer less loaded nodes
        load_factor = node.current_instances / node.max_instances
        score += 20.0 * (1.0 - load_factor)

        # 3. GPU preference (0-15 points)
        if instance.gpu_required and node.gpu:
            score += 15.0
        elif not instance.gpu_required and not node.gpu:
            score += 5.0  # Slight preference for CPU-only workloads on CPU nodes

        # 4. Affinity/Anti-affinity (0-25 points)
        affinity_score = 0.0

        # Check anti-affinity: strong penalty if conflicting instance on this node
        for inst_id in instance.anti_affinity:
            if current_placements.get(inst_id) == node.name:
                return -1.0  # Hard constraint

        # Check affinity: bonus for being on same node
        affinity_count = 0
        for inst_id in instance.affinity:
            if current_placements.get(inst_id) == node.name:
                affinity_count += 1

        if affinity_count > 0:
            affinity_score = min(25.0, affinity_count * 10.0)

        score += affinity_score

        # 5. Preferred node (0-10 points)
        if instance.preferred_node == node.name:
            score += 10.0

        return score

    @staticmethod
    def place_instances(nodes: List[NodeConfig],
                       instances: List[ExperimentInstance]) -> Dict[str, str]:
        """
        Place instances on nodes using greedy algorithm

        Returns:
            Dict mapping instance_id -> node_name
        """
        placements = {}

        # Sort instances by resource requirements (descending)
        # Place heavy workloads first
        sorted_instances = sorted(
            instances,
            key=lambda i: (i.gpu_required, i.ram_gb),
            reverse=True
        )

        for instance in sorted_instances:
            # Score all nodes
            scores = [
                (node, PlacementStrategy.score_node(node, instance, placements))
                for node in nodes
            ]

            # Filter valid placements
            valid = [(node, score) for node, score in scores if score >= 0]

            if not valid:
                raise RuntimeError(
                    f"Cannot place instance {instance.instance_id}: "
                    f"No suitable node found. Requires {instance.ram_gb}GB RAM, "
                    f"GPU={instance.gpu_required}"
                )

            # Pick best node
            best_node, best_score = max(valid, key=lambda x: x[1])

            # Assign
            placements[instance.instance_id] = best_node.name
            instance.assigned_node = best_node.name

            # Update node state
            best_node.current_instances += 1
            best_node.allocated_ram_gb += instance.ram_gb
            if instance.gpu_required:
                best_node.allocated_gpu_memory_gb += instance.gpu_memory_gb

            logger.info(
                f"Placed {instance.instance_id} on {best_node.name} "
                f"(score: {best_score:.1f}, RAM: {instance.ram_gb}GB)"
            )

        return placements


class ClusterOrchestrator:
    """
    Orchestrates experiment execution across multiple nodes

    Responsibilities:
    - Load cluster configuration
    - Place experiment instances on nodes
    - Monitor node health
    - Handle failures and rebalancing
    - Coordinate multi-instance experiments
    """

    def __init__(self, config_path: str):
        """
        Initialize orchestrator

        Args:
            config_path: Path to cluster_config.yaml
        """
        self.config_path = Path(config_path)
        self.nodes: List[NodeConfig] = []
        self.instances: List[ExperimentInstance] = []
        self.placements: Dict[str, str] = {}  # instance_id -> node_name
        self.remote_runners: Dict[str, 'RemoteRunner'] = {}  # node_name -> RemoteRunner

        self._load_config()

    def _load_config(self):
        """Load cluster configuration from YAML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        # Parse nodes
        for node_data in config.get('nodes', []):
            node = NodeConfig(
                name=node_data['name'],
                host=node_data['host'],
                node_type=NodeType(node_data.get('type', 'generic')),
                ram_gb=node_data['ram_gb'],
                gpu=node_data.get('gpu', False),
                gpu_memory_gb=node_data.get('gpu_memory_gb', 0.0),
                cpu_cores=node_data.get('cpu_cores', 4),
                ssh_port=node_data.get('ssh_port', 22),
                ssh_user=node_data.get('ssh_user', 'user'),
                ssh_key_path=node_data.get('ssh_key_path'),
                max_instances=node_data.get('max_instances', 1),
                reserved_ram_gb=node_data.get('reserved_ram_gb', 1.0)
            )
            self.nodes.append(node)

        logger.info(f"Loaded {len(self.nodes)} nodes from {self.config_path}")
        for node in self.nodes:
            logger.info(
                f"  {node.name}: {node.ram_gb}GB RAM, "
                f"{'GPU' if node.gpu else 'CPU'}, "
                f"max {node.max_instances} instances"
            )

    def add_instance(self, instance: ExperimentInstance):
        """Add an experiment instance to be scheduled"""
        self.instances.append(instance)
        logger.info(
            f"Added instance {instance.instance_id}: "
            f"{instance.ram_gb}GB RAM, GPU={instance.gpu_required}"
        )

    def add_instance_from_config(self, config_path: str, instance_id: str,
                                 preferred_node: Optional[str] = None,
                                 gpu_required: bool = False,
                                 gpu_memory_gb: float = 0.0):
        """
        Add instance from experiment config file

        Args:
            config_path: Path to experiment JSON config
            instance_id: Unique instance identifier
            preferred_node: Preferred node name (optional)
            gpu_required: Override GPU requirement
            gpu_memory_gb: GPU memory needed (if gpu_required)
        """
        # Load config to extract RAM requirement
        with open(config_path) as f:
            exp_config = json.load(f)

        ram_gb = exp_config['resource_constraints']['ram_limit_gb']

        # Check if config specifies GPU
        if not gpu_required:
            gpu_required = exp_config['resource_constraints'].get('gpu_layers', 0) > 0

        instance = ExperimentInstance(
            instance_id=instance_id,
            experiment_config_path=config_path,
            ram_gb=ram_gb,
            gpu_required=gpu_required,
            gpu_memory_gb=gpu_memory_gb,
            preferred_node=preferred_node
        )

        self.add_instance(instance)

    def place_all(self) -> Dict[str, str]:
        """
        Place all instances using placement algorithm

        Returns:
            Dict mapping instance_id -> node_name
        """
        logger.info(f"Placing {len(self.instances)} instances on {len(self.nodes)} nodes...")

        # Reset node allocations
        for node in self.nodes:
            node.current_instances = 0
            node.allocated_ram_gb = 0.0
            node.allocated_gpu_memory_gb = 0.0

        # Run placement algorithm
        self.placements = PlacementStrategy.place_instances(self.nodes, self.instances)

        # Log placement summary
        logger.info("\nPlacement Summary:")
        for node in self.nodes:
            instances_on_node = [
                i.instance_id for i in self.instances
                if i.assigned_node == node.name
            ]
            logger.info(
                f"  {node.name}: {len(instances_on_node)} instances, "
                f"{node.allocated_ram_gb:.1f}/{node.ram_gb}GB RAM"
            )
            for inst_id in instances_on_node:
                logger.info(f"    - {inst_id}")

        return self.placements

    async def health_check_node(self, node: NodeConfig) -> NodeStatus:
        """
        Check health of a node

        Returns:
            Updated NodeStatus
        """
        from .remote_runner import RemoteRunner

        try:
            if node.is_localhost:
                # Local health check
                import psutil
                mem = psutil.virtual_memory()
                if mem.percent > 90:
                    return NodeStatus.DEGRADED
                return NodeStatus.HEALTHY
            else:
                # Remote health check via SSH
                runner = RemoteRunner(
                    node.host,
                    node.ssh_user,
                    node.ssh_port,
                    node.ssh_key_path
                )

                # Quick SSH test + memory check
                result = await runner.execute_command(
                    "free -g | grep Mem | awk '{print $3,$2}'"
                )

                if result['success']:
                    used, total = map(float, result['stdout'].split())
                    usage_percent = (used / total) * 100

                    if usage_percent > 90:
                        return NodeStatus.DEGRADED
                    return NodeStatus.HEALTHY
                else:
                    return NodeStatus.UNAVAILABLE

        except Exception as e:
            logger.error(f"Health check failed for {node.name}: {e}")
            return NodeStatus.UNAVAILABLE

    async def health_check_all(self):
        """Check health of all nodes"""
        logger.info("Running health checks on all nodes...")

        tasks = [self.health_check_node(node) for node in self.nodes]
        statuses = await asyncio.gather(*tasks)

        for node, status in zip(self.nodes, statuses):
            node.status = status
            node.last_health_check = datetime.now()
            logger.info(f"  {node.name}: {status.value}")

    def get_placement_report(self) -> Dict[str, Any]:
        """
        Generate placement report

        Returns:
            Dict with placement statistics and recommendations
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_nodes': len(self.nodes),
            'total_instances': len(self.instances),
            'nodes': [],
            'warnings': []
        }

        for node in self.nodes:
            node_info = {
                'name': node.name,
                'status': node.status.value,
                'instances': node.current_instances,
                'max_instances': node.max_instances,
                'ram_allocated_gb': node.allocated_ram_gb,
                'ram_total_gb': node.ram_gb,
                'ram_utilization_percent': (node.allocated_ram_gb / node.ram_gb) * 100,
                'gpu': node.gpu
            }

            report['nodes'].append(node_info)

            # Generate warnings
            if node.allocated_ram_gb > node.ram_gb * 0.9:
                report['warnings'].append(
                    f"{node.name}: RAM utilization very high ({node_info['ram_utilization_percent']:.1f}%)"
                )

            if node.status != NodeStatus.HEALTHY:
                report['warnings'].append(
                    f"{node.name}: Node status is {node.status.value}"
                )

        return report

    def save_state(self, output_path: str):
        """Save cluster state to JSON"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'nodes': [node.to_dict() for node in self.nodes],
            'instances': [inst.to_dict() for inst in self.instances],
            'placements': self.placements
        }

        with open(output_path, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Cluster state saved to {output_path}")

    def load_state(self, input_path: str):
        """Load cluster state from JSON"""
        with open(input_path) as f:
            state = json.load(f)

        # Restore placements
        self.placements = state['placements']

        logger.info(f"Cluster state loaded from {input_path}")


# ===== Example Usage =====

def create_example_cluster_config():
    """Create example cluster configuration"""
    config = {
        'cluster': {
            'name': 'brain-in-jar-cluster',
            'description': 'Multi-node cluster for phenomenology experiments'
        },
        'nodes': [
            {
                'name': 'jetson',
                'host': '192.168.1.100',  # Replace with actual IP
                'type': 'jetson_orin',
                'ram_gb': 64.0,
                'gpu': True,
                'gpu_memory_gb': 64.0,  # Shared with system RAM on Jetson
                'cpu_cores': 12,
                'max_instances': 4,
                'reserved_ram_gb': 4.0,
                'ssh_user': 'jetson',
                'ssh_port': 22,
                'ssh_key_path': '~/.ssh/id_rsa'
            },
            {
                'name': 'rpi1',
                'host': '192.168.1.101',  # Replace with actual IP
                'type': 'raspberry_pi',
                'ram_gb': 8.0,
                'gpu': False,
                'cpu_cores': 4,
                'max_instances': 1,
                'reserved_ram_gb': 1.0,
                'ssh_user': 'pi',
                'ssh_port': 22,
                'ssh_key_path': '~/.ssh/id_rsa'
            },
            {
                'name': 'host',
                'host': 'localhost',
                'type': 'host',
                'ram_gb': 32.0,
                'gpu': False,
                'cpu_cores': 8,
                'max_instances': 3,
                'reserved_ram_gb': 4.0,
                'ssh_user': 'user',
                'ssh_port': 22
            }
        ]
    }

    return config


if __name__ == "__main__":
    # Example: Create and test placement
    import tempfile

    # Create example config
    config = create_example_cluster_config()

    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name

    print(f"Created example config: {config_path}")

    # Initialize orchestrator
    orchestrator = ClusterOrchestrator(config_path)

    # Add some example instances
    orchestrator.add_instance(ExperimentInstance(
        instance_id="split_brain_A",
        experiment_config_path="experiments/examples/split_brain_001_brain_A.json",
        ram_gb=8.0,
        gpu_required=True,
        gpu_memory_gb=8.0
    ))

    orchestrator.add_instance(ExperimentInstance(
        instance_id="split_brain_B",
        experiment_config_path="experiments/examples/split_brain_001_brain_B.json",
        ram_gb=2.0,
        gpu_required=False,
        anti_affinity=["split_brain_A"]  # Don't place on same node as A
    ))

    orchestrator.add_instance(ExperimentInstance(
        instance_id="panopticon_observer",
        experiment_config_path="experiments/examples/panopticon_subject.json",
        ram_gb=4.0,
        gpu_required=False,
        affinity=["split_brain_A"]  # Prefer to be near A
    ))

    # Place instances
    placements = orchestrator.place_all()

    # Generate report
    report = orchestrator.get_placement_report()
    print("\n=== Placement Report ===")
    print(json.dumps(report, indent=2))
