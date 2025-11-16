#!/usr/bin/env python3
"""
Example: Integrating ThermalWatchdog into Neural Link System

This example demonstrates how to add thermal monitoring to the Brain in a Jar
system, following the same pattern as the GPU watchdog.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.thermal_watchdog import ThermalWatchdog
import time


class ExampleNeuralLinkSystem:
    """Simplified example of neural link with thermal monitoring"""

    def __init__(self):
        print("=" * 60)
        print("INITIALIZING NEURAL LINK WITH THERMAL MONITORING")
        print("=" * 60)

        # Initialize thermal watchdog
        self.thermal_watchdog = ThermalWatchdog(
            warning_threshold=75.0,  # Start logging warnings at 75°C
            kill_threshold=85.0,      # Emergency shutdown at 85°C
            check_interval=5          # Check every 5 seconds
        )

        # Start thermal monitoring
        self.thermal_watchdog.start()

        if self.thermal_watchdog.thermal_zones:
            print(f"\n✓ Thermal Watchdog started")
            print(f"  - Monitoring {len(self.thermal_watchdog.thermal_zones)} thermal zones")
            print(f"  - Warning threshold: {self.thermal_watchdog.warning_threshold}°C")
            print(f"  - Kill threshold: {self.thermal_watchdog.kill_threshold}°C")
        else:
            print("\n⚠️  No thermal zones detected (not on Jetson/Pi)")

        # System state
        self.state = {
            "thermal_status": {},
            "running": True
        }

    def update_status(self):
        """Update system status including thermal monitoring"""
        # Get thermal status for UI display
        if hasattr(self, 'thermal_watchdog') and self.thermal_watchdog.thermal_zones:
            thermal_status = self.thermal_watchdog.get_thermal_status()
            self.state['thermal_status'] = thermal_status

            # Display thermal info
            if thermal_status['max_temp'] is not None:
                print(f"\n[Thermal] Max: {thermal_status['max_temp']:.1f}°C ({thermal_status['max_zone']})")

                # Show by zone type
                for zone_type, avg_temp in sorted(thermal_status['type_averages'].items()):
                    status_icon = "✓"
                    if thermal_status['critical']:
                        status_icon = "🔥"
                    elif thermal_status['warning']:
                        status_icon = "⚠️ "

                    print(f"  {status_icon} {zone_type}: {avg_temp:.1f}°C")

    def run(self, duration=10):
        """Run the system for a specified duration"""
        print(f"\n{'=' * 60}")
        print(f"RUNNING FOR {duration} SECONDS")
        print(f"{'=' * 60}\n")

        try:
            for i in range(duration):
                self.update_status()
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")

    def cleanup(self):
        """Clean up resources"""
        print("\n" + "=" * 60)
        print("SHUTTING DOWN")
        print("=" * 60)

        # Stop thermal watchdog
        if hasattr(self, 'thermal_watchdog'):
            self.thermal_watchdog.stop()
            print("✓ Thermal watchdog stopped")


def example_basic_usage():
    """Example: Basic thermal watchdog usage"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 1: BASIC USAGE")
    print("=" * 60)

    # Create and start watchdog
    watchdog = ThermalWatchdog()

    # Get current thermal status
    status = watchdog.get_thermal_status()

    if status['max_temp'] is not None:
        print(f"\nMax Temperature: {status['max_temp']:.1f}°C")
        print(f"Zone: {status['max_zone']}")
        print(f"Warning: {status['warning']}")
        print(f"Critical: {status['critical']}")

        print("\nBy Type:")
        for zone_type, avg in sorted(status['type_averages'].items()):
            print(f"  {zone_type}: {avg:.1f}°C")
    else:
        print("\nNo thermal data available (not on Jetson/Pi)")


def example_custom_thresholds():
    """Example: Custom thresholds for different hardware"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: CUSTOM THRESHOLDS")
    print("=" * 60)

    # Jetson Orin AGX (higher thermal capacity)
    print("\nJetson Orin AGX Configuration:")
    watchdog_orin = ThermalWatchdog(
        warning_threshold=75.0,
        kill_threshold=85.0,
        check_interval=5
    )
    print(f"  Warning: {watchdog_orin.warning_threshold}°C")
    print(f"  Kill: {watchdog_orin.kill_threshold}°C")

    # Jetson Xavier NX (more conservative)
    print("\nJetson Xavier NX Configuration:")
    watchdog_xavier = ThermalWatchdog(
        warning_threshold=70.0,
        kill_threshold=80.0,
        check_interval=3
    )
    print(f"  Warning: {watchdog_xavier.warning_threshold}°C")
    print(f"  Kill: {watchdog_xavier.kill_threshold}°C")

    # Raspberry Pi 5 (most conservative)
    print("\nRaspberry Pi 5 Configuration:")
    watchdog_pi = ThermalWatchdog(
        warning_threshold=70.0,
        kill_threshold=78.0,
        check_interval=3
    )
    print(f"  Warning: {watchdog_pi.warning_threshold}°C")
    print(f"  Kill: {watchdog_pi.kill_threshold}°C")


def example_monitoring_loop():
    """Example: Background monitoring with status display"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: BACKGROUND MONITORING")
    print("=" * 60)

    watchdog = ThermalWatchdog(check_interval=2)

    print("\nStarting background monitoring...")
    watchdog.start()

    try:
        for i in range(5):
            time.sleep(2)

            status = watchdog.get_thermal_status()
            if status['max_temp'] is not None:
                print(f"[{i+1}/5] {status['max_temp']:.1f}°C ({status['max_zone']})", end="")

                if status['critical']:
                    print(" 🔥 CRITICAL")
                elif status['warning']:
                    print(" ⚠️  WARNING")
                else:
                    print(" ✓ OK")
            else:
                print(f"[{i+1}/5] No thermal data")

    except KeyboardInterrupt:
        print("\nInterrupted")

    watchdog.stop()
    print("Monitoring stopped")


def example_web_ui_integration():
    """Example: Data format for web UI"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: WEB UI DATA FORMAT")
    print("=" * 60)

    watchdog = ThermalWatchdog()
    status = watchdog.get_thermal_status()

    # This is the format you'd send to the web UI
    web_data = {
        'thermal': {
            'max_temp': status['max_temp'],
            'max_zone': status['max_zone'],
            'warning': status['warning'],
            'critical': status['critical'],
            'zones_by_type': {
                zone_type: [
                    {
                        'name': z['name'],
                        'temp': z['temp']
                    }
                    for z in zones
                ]
                for zone_type, zones in status['zones_by_type'].items()
            }
        }
    }

    print("\nData for web UI:")
    import json
    print(json.dumps(web_data, indent=2))


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("THERMAL WATCHDOG INTEGRATION EXAMPLES")
    print("Brain in a Jar - Thermal Protection System")
    print("=" * 60)

    # Example 1: Basic usage
    example_basic_usage()

    # Example 2: Custom thresholds
    example_custom_thresholds()

    # Example 3: Monitoring loop
    example_monitoring_loop()

    # Example 4: Web UI integration
    example_web_ui_integration()

    # Example 5: Full neural link integration
    print("\n\n" + "=" * 60)
    print("EXAMPLE 5: FULL NEURAL LINK INTEGRATION")
    print("=" * 60)

    system = ExampleNeuralLinkSystem()
    system.run(duration=5)
    system.cleanup()

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETE")
    print("=" * 60)
    print("\nFor production integration, add to src/core/neural_link.py:")
    print("  1. Import ThermalWatchdog")
    print("  2. Initialize in __init__")
    print("  3. Start watchdog")
    print("  4. Update state with thermal status")
    print("  5. Display in UI")
    print("\nSee docs/THERMAL_WATCHDOG_INTEGRATION.md for details")


if __name__ == '__main__':
    main()
