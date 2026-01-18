#!/usr/bin/env python3
"""
Thermal Watchdog for Jetson Orin
Monitors temperature zones and kills process before hardware damage occurs
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path
from datetime import datetime


class ThermalWatchdog:
    """Monitor Jetson thermal zones and kill process if temperatures exceed safe limits"""

    # Jetson Orin thermal zones
    THERMAL_ZONES = {
        'cpu': 0,
        'gpu': 1,
        'cv0': 2,
        'cv1': 3,
        'cv2': 4,
        'soc0': 5,
        'soc1': 6,
        'soc2': 7,
        'tj': 8  # Junction temperature
    }

    def __init__(self, threshold_celsius=85, check_interval=5, pid=None, log_file='logs/thermal_events.log'):
        """
        Initialize thermal watchdog

        Args:
            threshold_celsius: Kill process when any zone exceeds this temperature (default 85°C)
            check_interval: How often to check temperature in seconds (default 5s)
            pid: Process ID to monitor (default: current process)
            log_file: Path to thermal events log file
        """
        self.threshold_celsius = threshold_celsius
        self.check_interval = check_interval
        self.pid = pid or os.getpid()
        self.running = True
        self.monitoring_thread = None
        self.log_file = log_file

        # Create logs directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir:  # Only create if directory path is not empty
            os.makedirs(log_dir, exist_ok=True)

        # Check if thermal zones are available
        self.zones_available = self._check_thermal_zones()

    def _check_thermal_zones(self):
        """Check which thermal zones are available"""
        available = {}
        for name, zone_id in self.THERMAL_ZONES.items():
            zone_path = f'/sys/class/thermal/thermal_zone{zone_id}/temp'
            if os.path.exists(zone_path):
                available[name] = zone_id
        return available

    def get_temperature(self, zone_name):
        """
        Get temperature for a specific thermal zone

        Args:
            zone_name: Name of the thermal zone (cpu, gpu, cv0, etc.)

        Returns:
            float: Temperature in Celsius, or -1 if unavailable
        """
        if zone_name not in self.zones_available:
            return -1

        try:
            zone_id = self.zones_available[zone_name]
            temp_path = f'/sys/class/thermal/thermal_zone{zone_id}/temp'

            with open(temp_path, 'r', encoding='utf-8') as f:
                temp_str = f.read().strip()
                if not temp_str:
                    return -1
                # Temperature is in millidegrees Celsius
                temp_millidegrees = int(temp_str)
                return temp_millidegrees / 1000.0

        except (FileNotFoundError, ValueError, PermissionError, TypeError) as e:
            return -1

    def get_all_temperatures(self):
        """
        Get temperatures for all available zones

        Returns:
            dict: {zone_name: temperature_celsius}
        """
        temps = {}
        for zone_name in self.zones_available.keys():
            temp = self.get_temperature(zone_name)
            if temp >= 0:
                temps[zone_name] = temp
        return temps

    def get_max_temperature(self):
        """
        Get the maximum temperature across all zones

        Returns:
            tuple: (max_temp, zone_name) or (-1, None) if unavailable
        """
        temps = self.get_all_temperatures()
        if not temps:
            return -1, None

        max_zone = max(temps.items(), key=lambda x: x[1])
        return max_zone[1], max_zone[0]

    def _log_event(self, message, level='INFO'):
        """Log thermal event to file"""
        try:
            timestamp = datetime.now().isoformat()
            with open(self.log_file, 'a') as f:
                f.write(f"{timestamp} [{level}] {message}\n")
        except Exception as e:
            print(f"[Thermal Watchdog] Error logging event: {e}", file=sys.stderr)

    def _monitoring_loop(self):
        """Background monitoring loop"""
        print(f"[Thermal Watchdog] Starting monitoring (PID: {self.pid}, threshold: {self.threshold_celsius}°C)")
        self._log_event(f"Thermal watchdog started - PID: {self.pid}, threshold: {self.threshold_celsius}°C")

        if not self.zones_available:
            print("[Thermal Watchdog] ⚠️  No thermal zones available - watchdog disabled")
            self._log_event("No thermal zones available - watchdog disabled", level='WARNING')
            return

        print(f"[Thermal Watchdog] Monitoring zones: {', '.join(self.zones_available.keys())}")

        while self.running:
            try:
                # Get all temperatures
                temps = self.get_all_temperatures()
                max_temp, max_zone = self.get_max_temperature()

                # Log current temperatures
                temp_str = ', '.join([f"{zone}: {temp:.1f}°C" for zone, temp in temps.items()])
                print(f"[Thermal Watchdog] {temp_str}")

                # Check threshold
                if max_temp >= self.threshold_celsius:
                    critical_msg = f"⚠️  CRITICAL: {max_zone} temperature at {max_temp:.1f}°C (threshold: {self.threshold_celsius}°C)"
                    print(f"\n[Thermal Watchdog] {critical_msg}", file=sys.stderr)
                    self._log_event(critical_msg, level='CRITICAL')

                    kill_msg = f"🛑 Killing process {self.pid} to prevent hardware damage"
                    print(f"[Thermal Watchdog] {kill_msg}", file=sys.stderr)
                    self._log_event(kill_msg, level='CRITICAL')

                    self._kill_process()
                    return

                # Warning at 80% of threshold
                warning_threshold = self.threshold_celsius * 0.8
                if max_temp >= warning_threshold:
                    warning_msg = f"⚠️  WARNING: {max_zone} temperature at {max_temp:.1f}°C"
                    print(f"[Thermal Watchdog] {warning_msg}", file=sys.stderr)
                    self._log_event(warning_msg, level='WARNING')

                time.sleep(self.check_interval)

            except Exception as e:
                error_msg = f"Error in monitoring loop: {e}"
                print(f"[Thermal Watchdog] {error_msg}", file=sys.stderr)
                self._log_event(error_msg, level='ERROR')
                time.sleep(self.check_interval)

    def _kill_process(self):
        """Kill the monitored process"""
        try:
            os.kill(self.pid, signal.SIGTERM)
            time.sleep(2)

            # If still alive, force kill
            try:
                os.kill(self.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already dead

        except ProcessLookupError:
            print(f"[Thermal Watchdog] Process {self.pid} already terminated")
            self._log_event(f"Process {self.pid} already terminated")
        except Exception as e:
            error_msg = f"Error killing process: {e}"
            print(f"[Thermal Watchdog] {error_msg}", file=sys.stderr)
            self._log_event(error_msg, level='ERROR')

    def start(self):
        """Start background monitoring"""
        if not self.running:
            return

        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="ThermalWatchdog"
        )
        self.monitoring_thread.start()

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)


def test_watchdog():
    """Test the thermal watchdog functionality"""
    print("Testing Thermal Watchdog...")

    watchdog = ThermalWatchdog(threshold_celsius=85, check_interval=2)

    print("\nAvailable thermal zones:")
    for zone_name in watchdog.zones_available.keys():
        print(f"  {zone_name}")

    temps = watchdog.get_all_temperatures()
    max_temp, max_zone = watchdog.get_max_temperature()

    print(f"\nCurrent Temperatures:")
    for zone, temp in temps.items():
        print(f"  {zone}: {temp:.1f}°C")

    print(f"\nMaximum: {max_zone} at {max_temp:.1f}°C")
    print(f"\nWatchdog will kill process if any zone exceeds {watchdog.threshold_celsius}°C")
    print(f"\nStarting 10-second monitoring test...")

    watchdog.start()
    time.sleep(10)
    watchdog.stop()

    print("Test complete!")


if __name__ == '__main__':
    test_watchdog()
