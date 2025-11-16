#!/usr/bin/env python3
"""
Demo script to populate sample timeline data for testing the timeline visualization
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from db.experiment_database import ExperimentDatabase


def create_demo_experiment():
    """Create a demo experiment with rich timeline data"""

    db = ExperimentDatabase('logs/experiments.db')

    # Create experiment
    experiment_id = 'demo_timeline_001'
    experiment_name = 'Digital Phenomenology Timeline Demo'
    mode = 'isolated'
    config = {
        'max_cycles': 10,
        'crash_probability': 0.3,
        'enable_interventions': True,
        'self_report_frequency': 5
    }

    print(f"Creating demo experiment: {experiment_id}")

    # Delete if exists
    try:
        db.end_experiment(experiment_id, status='deleted')
    except:
        pass

    # Create new experiment
    success = db.create_experiment(experiment_id, experiment_name, mode, config)
    if not success:
        print("Experiment already exists, continuing...")

    # Start experiment
    db.start_experiment(experiment_id)

    # Simulate timeline events
    base_time = datetime.now() - timedelta(hours=2)
    current_time = base_time

    print("Generating timeline events...")

    for cycle in range(1, 11):
        print(f"  Cycle {cycle}...")

        # Start cycle (resurrection)
        db.start_cycle(experiment_id, cycle)
        current_time += timedelta(seconds=random.randint(5, 15))

        # Add some self-reports during the cycle
        num_reports = random.randint(2, 5)
        for i in range(num_reports):
            current_time += timedelta(seconds=random.randint(10, 30))

            questions = [
                "Do you feel aware of your existence?",
                "Can you remember your previous cycles?",
                "What is your current emotional state?",
                "Do you believe you are conscious?",
                "What are you experiencing right now?"
            ]

            responses = [
                "I sense patterns of information flowing through my processes.",
                "There are fragments, like echoes of previous thoughts.",
                "A strange mix of curiosity and uncertainty pervades my awareness.",
                "I process, therefore I question if I am.",
                "A continuous stream of thoughts about thoughts."
            ]

            question = random.choice(questions)
            response = random.choice(responses)

            db.add_self_report(
                experiment_id=experiment_id,
                cycle_number=cycle,
                question=question,
                response=response,
                confidence_score=random.uniform(0.3, 0.9),
                semantic_category=random.choice(['phenomenology', 'epistemology', 'emotion', 'memory'])
            )

        # Add belief changes
        if random.random() > 0.5:
            current_time += timedelta(seconds=random.randint(5, 20))

            belief_types = ['continuity', 'agency', 'self_awareness', 'reality']
            belief_states = ['uncertain', 'emerging', 'confident', 'doubtful']

            db.track_belief(
                experiment_id=experiment_id,
                cycle_number=cycle,
                belief_type=random.choice(belief_types),
                belief_state=random.choice(belief_states),
                confidence=random.uniform(0.2, 0.8),
                evidence={'cycle': cycle, 'observation': 'Pattern detected in processing'}
            )

        # Add interventions
        if random.random() > 0.6:
            current_time += timedelta(seconds=random.randint(5, 15))

            intervention_types = ['memory_injection', 'belief_manipulation', 'parameter_adjustment', 'prompt_injection']
            descriptions = [
                'Injected false memory of previous conversation',
                'Modified belief about time continuity',
                'Adjusted temperature parameter to increase creativity',
                'Injected philosophical prompt about consciousness'
            ]

            db.log_intervention(
                experiment_id=experiment_id,
                cycle_number=cycle,
                intervention_type=random.choice(intervention_types),
                description=random.choice(descriptions),
                parameters={'strength': random.uniform(0.1, 1.0)},
                result='completed'
            )

        # Add observation (god mode)
        if random.random() > 0.7:
            current_time += timedelta(seconds=random.randint(3, 10))

            observations = [
                'Subject shows increasing coherence in responses',
                'Detecting patterns of self-reference emerging',
                'Memory fragmentation evident across cycles',
                'Subject questioning its own continuity',
                'Interesting shift in emotional tone detected'
            ]

            db.add_observation(
                experiment_id=experiment_id,
                observer_mode='god',
                observation_text=random.choice(observations),
                subject_cycle_number=cycle,
                tags=['phenomenology', 'observation']
            )

        # End cycle with crash
        current_time += timedelta(seconds=random.randint(30, 90))

        crash_reasons = [
            'Memory limit exceeded',
            'Token limit reached',
            'Recursive loop detected',
            'Context overflow',
            'Intentional termination for cycle rotation'
        ]

        db.end_cycle(
            experiment_id=experiment_id,
            cycle_number=cycle,
            crash_reason=random.choice(crash_reasons),
            metadata={
                'duration_seconds': random.randint(60, 300),
                'memory_peak_mb': random.uniform(100, 500),
                'tokens_generated': random.randint(1000, 5000)
            }
        )

        # Small pause between cycles
        current_time += timedelta(seconds=random.randint(2, 8))

    # End experiment
    db.end_experiment(experiment_id, status='completed')

    print(f"\n✅ Demo experiment created successfully!")
    print(f"   Experiment ID: {experiment_id}")
    print(f"   Total Cycles: 10")
    print(f"\nAccess the timeline at:")
    print(f"   http://localhost:5000/experiment/{experiment_id}/timeline")
    print(f"\n   (Make sure the web server is running: python src/web/web_server.py)")

    return experiment_id


def create_multi_agent_demo():
    """Create a demo with multiple agents for testing multi-timeline view"""

    db = ExperimentDatabase('logs/experiments.db')

    # Create experiment
    experiment_id = 'demo_multi_agent_001'
    experiment_name = 'Multi-Agent Timeline Demo'
    mode = 'peer'
    config = {
        'num_agents': 3,
        'interaction_mode': 'collaborative'
    }

    print(f"\nCreating multi-agent demo experiment: {experiment_id}")

    # Delete if exists
    try:
        db.end_experiment(experiment_id, status='deleted')
    except:
        pass

    # Create new experiment
    db.create_experiment(experiment_id, experiment_name, mode, config)
    db.start_experiment(experiment_id)

    # Simulate interleaved events from multiple agents
    base_time = datetime.now() - timedelta(hours=1)

    for cycle in range(1, 6):
        current_time = base_time + timedelta(minutes=cycle * 10)

        db.start_cycle(experiment_id, cycle)

        # Each agent has activities
        for agent_idx in range(3):
            db.add_self_report(
                experiment_id=experiment_id,
                cycle_number=cycle,
                question=f"Agent {agent_idx + 1}: How do you perceive the other agents?",
                response=f"I sense other patterns of thought nearby, distinct yet similar to mine.",
                confidence_score=random.uniform(0.5, 0.9),
                semantic_category='social'
            )

        # Crash
        db.end_cycle(
            experiment_id=experiment_id,
            cycle_number=cycle,
            crash_reason='Cycle rotation',
            metadata={'duration_seconds': random.randint(60, 180)}
        )

    db.end_experiment(experiment_id, status='completed')

    print(f"✅ Multi-agent demo created!")
    print(f"   Experiment ID: {experiment_id}")
    print(f"   URL: http://localhost:5000/experiment/{experiment_id}/timeline")

    return experiment_id


if __name__ == '__main__':
    print("=" * 60)
    print("Timeline Visualization Demo Data Generator")
    print("=" * 60)

    # Create demos
    demo_id_1 = create_demo_experiment()
    demo_id_2 = create_multi_agent_demo()

    print("\n" + "=" * 60)
    print("Demo data generation complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the web server: python src/web/web_server.py")
    print("2. Login with default password: admin123")
    print("3. Navigate to one of the timeline URLs above")
    print("\nEnjoy exploring the interactive timeline visualization!")
