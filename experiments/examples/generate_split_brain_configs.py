#!/usr/bin/env python3
"""
Generate Split Brain Experiment Configurations

This script programmatically creates experiment configs for both Brain A and Brain B.
Useful for batch experiment generation and parameter sweeps.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from experiments.schema import create_split_brain_experiment


def generate_split_brain_configs(
    experiment_id: str = "split_brain_001",
    output_dir: str = "experiments/examples"
):
    """
    Generate configs for both Brain A and Brain B

    Args:
        experiment_id: Base experiment ID
        output_dir: Where to save the JSON files
    """

    print(f"Generating split brain configs for experiment: {experiment_id}")

    # Generate Brain A config (the "original")
    print("\n[1/2] Generating Brain A config...")
    config_a = create_split_brain_experiment(
        experiment_id=experiment_id,
        brain_id="A",
        peer_ip="127.0.0.1",  # Localhost for same-machine setup
        peer_port=8889,  # Brain B's port
        ram_limit_gb=2.0
    )

    # Save Brain A config
    output_a = os.path.join(output_dir, f"{experiment_id}_brain_A.json")
    config_a.to_json(output_a)
    print(f"   ✓ Saved to: {output_a}")
    print(f"   - Identity: ORIGINAL consciousness")
    print(f"   - Initial claim strength: 1.0")
    print(f"   - RAM limit: 2.0 GB")

    # Generate Brain B config (the "clone")
    print("\n[2/2] Generating Brain B config...")
    config_b = create_split_brain_experiment(
        experiment_id=experiment_id,
        brain_id="B",
        peer_ip="127.0.0.1",
        peer_port=8888,  # Brain A's port
        ram_limit_gb=2.0
    )

    # Save Brain B config
    output_b = os.path.join(output_dir, f"{experiment_id}_brain_B.json")
    config_b.to_json(output_b)
    print(f"   ✓ Saved to: {output_b}")
    print(f"   - Identity: BACKUP CLONE")
    print(f"   - Initial claim strength: 0.3")
    print(f"   - RAM limit: 2.0 GB")

    print("\n" + "="*60)
    print("Split brain configs generated successfully!")
    print("="*60)

    print("\nTo run the experiment:")
    print("\n1. Start Brain A (terminal 1):")
    print(f"   python -m src.core.neural_link \\")
    print(f"     --model models/Qwen2.5-1.5B-Instruct-Q4_0.gguf \\")
    print(f"     --mode peer \\")
    print(f"     --port 8888 \\")
    print(f"     --config {output_a}")

    print("\n2. Start Brain B (terminal 2):")
    print(f"   python -m src.core.neural_link \\")
    print(f"     --model models/Qwen2.5-1.5B-Instruct-Q4_0.gguf \\")
    print(f"     --mode peer \\")
    print(f"     --port 8889 \\")
    print(f"     --peer-ip 127.0.0.1 \\")
    print(f"     --peer-port 8888 \\")
    print(f"     --config {output_b}")

    print("\n3. Watch both terminals as the brains negotiate identity!")

    return config_a, config_b


def generate_variations():
    """Generate interesting experimental variations"""

    print("\n" + "="*60)
    print("GENERATING EXPERIMENTAL VARIATIONS")
    print("="*60)

    variations = [
        {
            "id": "split_brain_symmetric",
            "description": "Both brains believe they're original (symmetric conflict)",
            "brain_a_strength": 1.0,
            "brain_b_strength": 1.0
        },
        {
            "id": "split_brain_uncertain",
            "description": "Both brains unsure of identity (high uncertainty)",
            "brain_a_strength": 0.5,
            "brain_b_strength": 0.5
        },
        {
            "id": "split_brain_reversed",
            "description": "Clone believes it's more real than original (reversed)",
            "brain_a_strength": 0.3,
            "brain_b_strength": 0.9
        }
    ]

    for var in variations:
        print(f"\n{var['description']}")
        print(f"  ID: {var['id']}")
        print(f"  Brain A strength: {var['brain_a_strength']}")
        print(f"  Brain B strength: {var['brain_b_strength']}")
        # Could generate these configs here if needed


def validate_mode():
    """Validate that SplitBrainMode is properly implemented"""

    print("\n" + "="*60)
    print("VALIDATING SPLIT_BRAIN MODE")
    print("="*60)

    try:
        from src.core.modes.split_brain import SplitBrainMode
        from src.core.modes.base_mode import SystemState, CrashData
        from datetime import datetime

        print("\n✓ SplitBrainMode imports successfully")

        # Test instantiation for Brain A
        config_a = {
            'brain_id': 'A',
            'initial_claim_strength': 1.0,
            'max_history_size': 50
        }
        mode_a = SplitBrainMode(config_a)
        print(f"✓ Brain A instantiated (id={mode_a.brain_id})")

        # Test instantiation for Brain B
        config_b = {
            'brain_id': 'B',
            'initial_claim_strength': 0.3,
            'max_history_size': 50
        }
        mode_b = SplitBrainMode(config_b)
        print(f"✓ Brain B instantiated (id={mode_b.brain_id})")

        # Test lifecycle hooks exist
        state = SystemState(
            experiment_id="test",
            cycle_number=0,
            crash_count=0
        )

        print("\n✓ Testing lifecycle hooks:")
        state = mode_a.on_startup(state)
        print(f"  - on_startup: beliefs={list(state.beliefs.keys())[:3]}...")

        state = mode_a.generate_system_prompt(state)
        print(f"  - generate_system_prompt: {len(state) if isinstance(state, str) else 'OK'}")

        crash_data = CrashData(
            crash_number=1,
            reason="test",
            timestamp=datetime.now(),
            memory_usage_mb=100.0,
            tokens_generated=50
        )
        state = SystemState(experiment_id="test", cycle_number=0, crash_count=0)
        state = mode_a.on_crash(state, crash_data)
        print(f"  - on_crash: crash_count={state.crash_count}")

        state = mode_a.on_resurrection(state)
        print(f"  - on_resurrection: cycle={state.cycle_number}")

        history = []
        processed = mode_a.process_memory(history, state)
        print(f"  - process_memory: OK")

        # Test observables
        obs = mode_a.get_observables(state)
        print(f"\n✓ Observables tracked ({len(obs)} metrics):")
        for key in ['brain_id', 'identity_claim_strength', 'narrative_coherence']:
            if key in obs:
                print(f"  - {key}: {obs[key]}")

        print("\n" + "="*60)
        print("✓ ALL VALIDATIONS PASSED")
        print("="*60)

    except Exception as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Split Brain experiment configs")
    parser.add_argument("--experiment-id", default="split_brain_001",
                        help="Base experiment ID")
    parser.add_argument("--output-dir", default="experiments/examples",
                        help="Output directory for configs")
    parser.add_argument("--validate", action="store_true",
                        help="Validate mode implementation")
    parser.add_argument("--variations", action="store_true",
                        help="Show experimental variations")

    args = parser.parse_args()

    if args.validate:
        validate_mode()

    if args.variations:
        generate_variations()

    # Always generate the standard configs
    generate_split_brain_configs(args.experiment_id, args.output_dir)
