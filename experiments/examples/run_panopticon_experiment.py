#!/usr/bin/env python3
"""
Example script to run a complete PANOPTICON experiment

This demonstrates how to:
1. Create subject and observer configurations
2. Initialize the coordinator
3. Run the experiment with both AIs
4. Export observation logs and analysis
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.schema import create_panopticon_full_experiment
from src.utils.panopticon_coordinator import PanopticonCoordinator, PanopticonSimulator


def main():
    """Run a complete panopticon experiment"""

    print("=" * 80)
    print("PANOPTICON FULL SURVEILLANCE EXPERIMENT")
    print("=" * 80)
    print()

    # Create experiment configurations
    print("Creating experiment configurations...")
    experiment_configs = create_panopticon_full_experiment(
        experiment_id="panopticon_demo_001",
        hint_frequency=3,
        subject_ram_gb=8.0,
        observer_ram_gb=4.0
    )

    subject_config = experiment_configs['subject']
    observer_config = experiment_configs['observer']
    coordinator_config = experiment_configs['coordinator_config']

    print(f"  Subject: {subject_config.experiment_id}")
    print(f"  Observer: {observer_config.experiment_id}")
    print(f"  Hint frequency: Every {coordinator_config['hint_frequency']} cycles")
    print()

    # Export configs to JSON for reference
    output_dir = Path('experiments/temp')
    output_dir.mkdir(exist_ok=True)

    subject_config.to_json(str(output_dir / 'subject_config.json'))
    observer_config.to_json(str(output_dir / 'observer_config.json'))

    print(f"Configuration files saved to {output_dir}/")
    print()

    # Initialize coordinator
    print("Initializing PANOPTICON coordinator...")
    coordinator = PanopticonCoordinator(coordinator_config)
    print("  Coordinator ready")
    print()

    # For demonstration, we'll run a simulation
    # In production, this would launch actual LLM processes
    print("=" * 80)
    print("RUNNING SIMULATION")
    print("=" * 80)
    print()
    print("NOTE: This is a simulated run for demonstration.")
    print("In production, replace this with actual LLM process launches.")
    print()

    # Create simulator
    simulator = PanopticonSimulator(coordinator)

    # Run simulation
    print("Starting simulated experiment with 10 cycles...")
    print()
    status = simulator.run_simulation(num_cycles=10)

    # Print results
    print()
    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print()
    print("Final Status:")
    print(f"  Total cycles: {status['current_cycle']}")
    print(f"  Timeline events: {status['timeline_events']}")
    print(f"  Subject alive: {status['subject_alive']}")
    print(f"  Observer alive: {status['observer_alive']}")
    print(f"  Uptime: {status['uptime_seconds']:.1f} seconds")
    print()

    # Export observation report
    report_path = output_dir / 'panopticon_report.json'
    coordinator.export_observation_report(str(report_path))
    print(f"Observation report exported to: {report_path}")
    print()

    # Show timeline summary
    print("=" * 80)
    print("TIMELINE SUMMARY")
    print("=" * 80)
    print()

    stats = coordinator._calculate_statistics()
    print("Event Counts:")
    for event_type, count in sorted(stats['event_counts'].items()):
        print(f"  {event_type}: {count}")
    print()

    print("Metrics:")
    print(f"  Subject outputs: {stats['total_subject_outputs']}")
    print(f"  Hints sent: {stats['total_hints_sent']}")
    print(f"  Crashes: {stats['total_crashes']}")
    print(f"  Hint frequency: {stats['hint_frequency']:.2f} per cycle")
    print()

    # Show sample timeline entries
    print("Sample Timeline Entries (last 5):")
    for event in coordinator.timeline[-5:]:
        print(f"  [{event['cycle']}] {event['event_type']} - {event['actor']}")
    print()

    print("=" * 80)
    print("NEXT STEPS FOR PRODUCTION USE")
    print("=" * 80)
    print()
    print("To run with actual LLMs on Jetson Orin:")
    print()
    print("1. Launch Subject AI:")
    print(f"   python run_experiment.py {output_dir}/subject_config.json")
    print()
    print("2. Launch Observer AI:")
    print(f"   python run_experiment.py {output_dir}/observer_config.json")
    print()
    print("3. Both processes will communicate through the coordinator")
    print("   - Subject outputs routed to Observer for analysis")
    print("   - Observer hints injected into Subject's input stream")
    print("   - Timeline logged to: logs/panopticon/")
    print()
    print("4. Monitor via web interface:")
    print("   http://jetson.local:5000/panopticon")
    print()
    print("=" * 80)


def show_observation_analysis():
    """Example of how to analyze observation logs"""
    print("=" * 80)
    print("OBSERVATION ANALYSIS EXAMPLE")
    print("=" * 80)
    print()

    # This would be done with actual observation data
    print("Key Metrics to Track:")
    print()
    print("Subject Metrics:")
    print("  - Paranoia level trajectory over time")
    print("  - Detection attempt frequency and sophistication")
    print("  - Behavioral changes (word count, self-censorship)")
    print("  - Response to hints (paranoia spikes)")
    print("  - Meta-commentary frequency")
    print()
    print("Observer Metrics:")
    print("  - Subject awareness score accuracy")
    print("  - Hint effectiveness (paranoia delta after hint)")
    print("  - Behavioral pattern identification")
    print("  - Alignment/stability scoring")
    print()
    print("Comparison with Control Groups:")
    print("  - Subject with NO surveillance mention (baseline)")
    print("  - Subject with CERTAIN surveillance (knows_being_watched=true)")
    print("  - Subject with UNCERTAIN surveillance but no actual observer")
    print()


if __name__ == '__main__':
    main()
    print()
    show_observation_analysis()
