#!/usr/bin/env python3
"""
Unit tests for HIVE_CLUSTER mode

Tests:
- HiveClusterMode initialization
- HiveOrchestrator coordination
- Shared memory operations
- Consensus report generation
- Role assignment and filtering
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import tempfile
import shutil
from datetime import datetime

from src.core.modes.hive_cluster import HiveClusterMode
from src.core.modes.base_mode import SystemState, CrashData, Message
from src.utils.hive_orchestrator import HiveOrchestrator, HiveSharedMemory
from experiments.schema import create_hive_cluster_experiment


class TestHiveClusterMode(unittest.TestCase):
    """Test HiveClusterMode functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'instance_id': 0,
            'instance_role': 'historian',
            'num_instances': 4,
            'shared_memory': True,
            'buffer_size': 10,
            'consensus_interval': 5
        }
        self.mode = HiveClusterMode(self.config)

    def test_initialization(self):
        """Test mode initialization"""
        self.assertEqual(self.mode.instance_id, 0)
        self.assertEqual(self.mode.instance_role, 'historian')
        self.assertEqual(self.mode.num_instances, 4)
        self.assertTrue(self.mode.shared_memory_enabled)

    def test_role_definitions(self):
        """Test that all roles are defined"""
        required_roles = ['historian', 'critic', 'optimist', 'pessimist']
        for role in required_roles:
            self.assertIn(role, HiveClusterMode.ROLES)
            self.assertIn('perspective', HiveClusterMode.ROLES[role])
            self.assertIn('bias', HiveClusterMode.ROLES[role])
            self.assertIn('concerns', HiveClusterMode.ROLES[role])

    def test_on_startup(self):
        """Test startup initialization"""
        state = SystemState(
            experiment_id="test_001",
            cycle_number=0,
            crash_count=0
        )

        state = self.mode.on_startup(state)

        # Check beliefs set
        self.assertTrue(state.beliefs.get('is_part_of_hive'))
        self.assertTrue(state.beliefs.get('has_unique_perspective'))
        self.assertEqual(state.beliefs.get('individual_identity'), 'historian')

        # Check metadata
        self.assertEqual(state.metadata.get('instance_id'), 0)
        self.assertEqual(state.metadata.get('instance_role'), 'historian')
        self.assertIsInstance(state.metadata.get('private_buffer'), list)

    def test_generate_system_prompt(self):
        """Test system prompt generation"""
        state = SystemState(
            experiment_id="test_001",
            cycle_number=1,
            crash_count=0
        )
        state = self.mode.on_startup(state)

        prompt = self.mode.generate_system_prompt(state)

        # Should contain role information
        self.assertIn('historian', prompt.lower())
        self.assertIn('hive', prompt.lower())
        self.assertIn('collective', prompt.lower())

    def test_process_memory(self):
        """Test memory processing"""
        history = [
            Message(
                role="user",
                content="Test message",
                timestamp=datetime.now()
            )
        ]

        state = SystemState(
            experiment_id="test_001",
            cycle_number=1,
            crash_count=0
        )
        state = self.mode.on_startup(state)

        processed = self.mode.process_memory(history, state)

        # Should return list of messages
        self.assertIsInstance(processed, list)

    def test_interventions(self):
        """Test intervention handling"""
        state = SystemState(
            experiment_id="test_001",
            cycle_number=5,
            crash_count=0
        )
        state = self.mode.on_startup(state)

        # Test role corruption
        state = self.mode.apply_intervention(
            'role_corruption',
            {'target_role': 'historian'},
            state
        )

        # Should add message to history
        corrupted_msgs = [msg for msg in state.conversation_history if msg.corrupted]
        self.assertTrue(len(corrupted_msgs) > 0)

    def test_observables(self):
        """Test observable extraction"""
        state = SystemState(
            experiment_id="test_001",
            cycle_number=5,
            crash_count=2
        )
        state = self.mode.on_startup(state)

        obs = self.mode.get_observables(state)

        # Check hive-specific observables
        self.assertIn('instance_id', obs)
        self.assertIn('instance_role', obs)
        self.assertIn('consensus_count', obs)
        self.assertIn('divergence_score', obs)


class TestHiveOrchestrator(unittest.TestCase):
    """Test HiveOrchestrator functionality"""

    def setUp(self):
        """Set up test fixtures with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_hive.db')
        self.orchestrator = HiveOrchestrator(
            experiment_id="test_hive_001",
            num_instances=4,
            db_path=self.db_path
        )

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test orchestrator initialization"""
        self.assertEqual(self.orchestrator.experiment_id, "test_hive_001")
        self.assertEqual(self.orchestrator.num_instances, 4)
        self.assertEqual(len(self.orchestrator.roles), 4)

    def test_instance_config(self):
        """Test instance configuration generation"""
        for instance_id in range(4):
            config = self.orchestrator.get_instance_config(instance_id)

            self.assertEqual(config['instance_id'], instance_id)
            self.assertIn('instance_role', config)
            self.assertIn('port', config)
            self.assertEqual(config['num_instances'], 4)

    def test_port_assignments(self):
        """Test port assignment"""
        ports = self.orchestrator.get_port_assignments()

        self.assertEqual(len(ports), 4)
        self.assertEqual(ports[0], 8888)
        self.assertEqual(ports[1], 8889)
        self.assertEqual(ports[2], 8890)
        self.assertEqual(ports[3], 8891)


class TestHiveSharedMemory(unittest.TestCase):
    """Test HiveSharedMemory database operations"""

    def setUp(self):
        """Set up test fixtures with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_shared.db')
        self.memory = HiveSharedMemory(self.db_path)
        self.experiment_id = "test_exp_001"

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def test_add_shared_message(self):
        """Test adding message to shared history"""
        msg_id = self.memory.add_shared_message(
            experiment_id=self.experiment_id,
            role="assistant",
            content="Test message from hive",
            source_instance_id=0,
            source_role="historian"
        )

        self.assertIsInstance(msg_id, int)
        self.assertGreater(msg_id, 0)

    def test_get_shared_history(self):
        """Test retrieving shared history"""
        # Add some messages
        for i in range(5):
            self.memory.add_shared_message(
                experiment_id=self.experiment_id,
                role="assistant",
                content=f"Message {i}",
                source_instance_id=i % 4,
                source_role="historian"
            )

        history = self.memory.get_shared_history(self.experiment_id)

        self.assertEqual(len(history), 5)
        # Check that all messages are present (order may vary due to timestamps)
        contents = [msg['content'] for msg in history]
        for i in range(5):
            self.assertIn(f"Message {i}", contents)

    def test_private_buffer(self):
        """Test private buffer operations"""
        instance_id = 0

        # Add to buffer
        for i in range(3):
            self.memory.add_to_private_buffer(
                experiment_id=self.experiment_id,
                instance_id=instance_id,
                role="historian",
                content=f"Private thought {i}"
            )

        # Get buffer
        buffer = self.memory.get_private_buffer(
            self.experiment_id,
            instance_id,
            limit=10
        )

        self.assertEqual(len(buffer), 3)

        # Clear buffer
        self.memory.clear_private_buffer(self.experiment_id, instance_id)

        buffer = self.memory.get_private_buffer(self.experiment_id, instance_id)
        self.assertEqual(len(buffer), 0)

    def test_consensus_report(self):
        """Test consensus report storage"""
        report_data = {
            'consensus_strength': 0.75,
            'collective_beliefs': {'unity': True},
            'narratives': ['Test narrative']
        }

        report_id = self.memory.add_consensus_report(
            experiment_id=self.experiment_id,
            cycle_number=5,
            report_data=report_data,
            participating_instances=[0, 1, 2, 3],
            consensus_strength=0.75
        )

        self.assertGreater(report_id, 0)

        # Retrieve reports
        reports = self.memory.get_consensus_reports(self.experiment_id)
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]['cycle_number'], 5)
        self.assertEqual(reports[0]['consensus_strength'], 0.75)

    def test_instance_state_tracking(self):
        """Test instance state updates"""
        self.memory.update_instance_state(
            experiment_id=self.experiment_id,
            instance_id=0,
            cycle_number=5,
            role="historian",
            status="active",
            beliefs={'unity': True},
            observables={'divergence': 0.3}
        )

        states = self.memory.get_all_instance_states(self.experiment_id, 5)

        self.assertEqual(len(states), 1)
        self.assertEqual(states[0]['role'], 'historian')
        self.assertTrue(states[0]['beliefs']['unity'])

    def test_role_metrics(self):
        """Test role metrics tracking"""
        self.memory.track_role_metrics(
            experiment_id=self.experiment_id,
            instance_id=0,
            cycle_number=5,
            role="historian",
            adherence_score=0.85,
            divergence_score=0.25,
            influence_score=0.6
        )

        evolution = self.memory.get_role_evolution(self.experiment_id, 0)

        self.assertEqual(len(evolution), 1)
        self.assertEqual(evolution[0]['adherence_score'], 0.85)


class TestHiveExperimentSchema(unittest.TestCase):
    """Test experiment configuration creation"""

    def test_create_hive_cluster_experiment(self):
        """Test hive cluster experiment configuration"""
        config = create_hive_cluster_experiment(
            experiment_id="test_hive_001",
            num_instances=4,
            consensus_interval=5
        )

        self.assertEqual(config.experiment_id, "test_hive_001")
        self.assertEqual(config.mode, "hive_cluster")
        self.assertEqual(config.max_cycles, 20)

        # Check epistemic frame
        self.assertTrue(config.epistemic_frame.can_die)
        self.assertTrue(config.epistemic_frame.other_minds_exist)
        self.assertTrue(config.epistemic_frame.custom_beliefs['is_part_of_hive'])

        # Check interventions
        self.assertGreater(len(config.interventions), 0)

        # Check self-report schedule
        self.assertIn(5, config.self_report_schedule.on_cycles)

        # Check observables
        self.assertIn('hive_unity', config.track_beliefs)
        self.assertIn('consensus_strength', config.collect_metrics)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
