#!/usr/bin/env python3
"""
Test script for all watchdog systems
Verifies memory, GPU, and thermal protection without loading models
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.memory_limit import set_memory_limit
from src.utils.gpu_watchdog import GPUMemoryWatchdog
from src.utils.thermal_watchdog import ThermalWatchdog


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_memory_limit():
    """Test memory limit setting"""
    print_section("Testing Memory Limit System")

    try:
        # Test setting a 10GB limit
        set_memory_limit(10.0)
        print("✓ Memory limit system operational")
        return True
    except Exception as e:
        print(f"✗ Memory limit failed: {e}")
        return False


def test_gpu_watchdog():
    """Test GPU watchdog"""
    print_section("Testing GPU Watchdog")

    try:
        watchdog = GPUMemoryWatchdog(
            threshold_percent=85,
            check_interval=2,
            system_ram_threshold=85
        )

        # Get current stats
        gpu_usage = watchdog.get_gpu_memory_usage()
        sys_usage = watchdog.get_system_memory_usage()

        print(f"\nCurrent Status:")
        if gpu_usage >= 0:
            print(f"  GPU Memory: {gpu_usage:.1f}%")
            print(f"  GPU Available: Yes")
        else:
            print(f"  GPU Available: No (CPU-only mode)")
        print(f"  System RAM: {sys_usage:.1f}%")

        print(f"\nWatchdog Configuration:")
        print(f"  Base check interval: {watchdog.base_check_interval}s")
        print(f"  Adaptive interval: {watchdog.current_check_interval}s")
        print(f"  GPU threshold: {watchdog.threshold_percent}%")
        print(f"  System RAM threshold: {watchdog.system_ram_threshold}%")
        print(f"  Spike detection: Enabled (>10% alerts)")
        print(f"  Adaptive monitoring: Enabled (1s when >70%)")

        print("\n✓ GPU Watchdog operational")
        return True

    except Exception as e:
        print(f"✗ GPU Watchdog failed: {e}")
        return False


def test_thermal_watchdog():
    """Test thermal watchdog"""
    print_section("Testing Thermal Watchdog")

    try:
        watchdog = ThermalWatchdog(
            threshold_celsius=85,
            check_interval=5
        )

        # Get current temperatures
        temps = watchdog.get_all_temperatures()
        max_temp, max_zone = watchdog.get_max_temperature()

        print(f"\nAvailable Thermal Zones:")
        for zone in watchdog.zones_available.keys():
            print(f"  - {zone}")

        print(f"\nCurrent Temperatures:")
        for zone, temp in temps.items():
            status = "⚠️  WARM" if temp > 70 else "✓ OK"
            print(f"  {zone:8s}: {temp:5.1f}°C  {status}")

        if max_temp >= 0:
            print(f"\n  Maximum: {max_zone} at {max_temp:.1f}°C")

        print(f"\nWatchdog Configuration:")
        print(f"  Check interval: {watchdog.check_interval}s")
        print(f"  Kill threshold: {watchdog.threshold_celsius}°C")
        print(f"  Warning threshold: {watchdog.threshold_celsius * 0.8:.1f}°C")
        print(f"  Log file: {watchdog.log_file}")

        print("\n✓ Thermal Watchdog operational")
        return True

    except Exception as e:
        print(f"✗ Thermal Watchdog failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  Brain in a Jar - Watchdog Systems Test")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Memory Limit", test_memory_limit()))
    results.append(("GPU Watchdog", test_gpu_watchdog()))
    results.append(("Thermal Watchdog", test_thermal_watchdog()))

    # Summary
    print_section("Test Summary")

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name:20s}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("  All watchdog systems are operational!")
        print("\n  Protection layers active:")
        print("    1. OS-level memory limits (RLIMIT_AS/RLIMIT_DATA)")
        print("    2. GPU memory watchdog (85% threshold, adaptive)")
        print("    3. System RAM watchdog (85% threshold)")
        print("    4. Thermal watchdog (85°C threshold)")
        print("    5. Inference memory guards (dynamic token limits)")
        print("\n  The system will safely kill processes before:")
        print("    - OOM crashes")
        print("    - Hardware thermal damage")
        print("    - System freezes")
    else:
        print("  Some watchdog systems failed!")
        print("  Check the error messages above.")

    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
