#!/usr/bin/env python3
"""
Thermal Watchdog
Monitors system thermal zones and kills the process before hardware overheating
Critical for preventing physical damage to Jetson/Pi devices under heavy AI workload
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ThermalWatchdog')


class ThermalWatchdog:
    """Monitor thermal zones and kill process if temperatures exceed safe limits"""

    # Jetson-specific thermal zone name patterns
    JETSON_ZONE_PATTERNS = {
        'CPU': ['CPU-therm', 'MCPU', 'cpu-thermal', 'cpu'],
        'GPU': ['GPU-therm', 'GPU', 'gpu'],
        'SOC': ['SOC', 'thermal', 'AO-therm', 'AUX'],
        'PMIC': ['PMIC', 'Tboard', 'Tdiode'],
        'CV': ['CV', 'CV0', 'CV1', 'CV2']  # Computer Vision engines
    }

    def __init__(self,
                 warning_threshold=75.0,
                 kill_threshold=85.0,
                 check_interval=5,
                 pid=None):
        """
        Initialize Thermal Watchdog

        Args:
            warning_threshold: Temperature in °C to start logging warnings (default 75°C)
            kill_threshold: Temperature in °C to kill process (default 85°C)
            check_interval: How often to check temperature in seconds (default 5s)
            pid: Process ID to monitor (default: current process)
        """
        self.warning_threshold = warning_threshold
        self.kill_threshold = kill_threshold
        self.check_interval = check_interval
        self.pid = pid or os.getpid()
        self.running = True
        self.monitoring_thread = None

        # Detect all thermal zones
        self.thermal_zones = self.get_all_thermal_zones()

        # Log detected zones
        if self.thermal_zones:
            logger.info(f"Detected {len(self.thermal_zones)} thermal zones")
            for zone_id, zone_info in self.thermal_zones.items():
                logger.info(f"  {zone_id}: {zone_info['name']} ({zone_info['type']})")
        else:
            logger.warning("No thermal zones detected - monitoring disabled")

    def get_all_thermal_zones(self) -> Dict[str, Dict]:
        """
        Detect all available thermal zones from sysfs

        Returns:
            Dictionary of thermal zones with their metadata
            Format: {
                'zone0': {
                    'path': '/sys/class/thermal/thermal_zone0/temp',
                    'name': 'CPU-therm',
                    'type': 'CPU',
                    'hwmon': False
                },
                ...
            }
        """
        thermal_zones = {}
        thermal_base = Path('/sys/class/thermal')

        if not thermal_base.exists():
            logger.warning(f"Thermal sysfs path not found: {thermal_base}")
            return thermal_zones

        # Scan thermal_zone* directories
        for zone_dir in sorted(thermal_base.glob('thermal_zone*')):
            zone_id = zone_dir.name
            temp_path = zone_dir / 'temp'
            type_path = zone_dir / 'type'

            if not temp_path.exists():
                continue

            # Read zone type/name
            zone_type = 'unknown'
            if type_path.exists():
                try:
                    zone_type = type_path.read_text().strip()
                except Exception as e:
                    logger.debug(f"Could not read type for {zone_id}: {e}")

            # Categorize zone based on name patterns
            category = self._categorize_zone(zone_type)

            thermal_zones[zone_id] = {
                'path': str(temp_path),
                'name': zone_type,
                'type': category,
                'hwmon': False
            }

        # Also check hwmon sensors (alternative thermal interface)
        hwmon_base = Path('/sys/class/hwmon')
        if hwmon_base.exists():
            for hwmon_dir in sorted(hwmon_base.glob('hwmon*')):
                name_path = hwmon_dir / 'name'
                if name_path.exists():
                    try:
                        hwmon_name = name_path.read_text().strip()
                        # Look for temp inputs
                        for temp_file in sorted(hwmon_dir.glob('temp*_input')):
                            zone_id = f"hwmon_{hwmon_dir.name}_{temp_file.name}"
                            category = self._categorize_zone(hwmon_name)

                            thermal_zones[zone_id] = {
                                'path': str(temp_file),
                                'name': hwmon_name,
                                'type': category,
                                'hwmon': True
                            }
                    except Exception as e:
                        logger.debug(f"Could not read hwmon {hwmon_dir}: {e}")

        return thermal_zones

    def _categorize_zone(self, zone_name: str) -> str:
        """
        Categorize a thermal zone based on its name

        Args:
            zone_name: Name/type string from sysfs

        Returns:
            Category string (CPU, GPU, SOC, PMIC, CV, or OTHER)
        """
        zone_lower = zone_name.lower()

        for category, patterns in self.JETSON_ZONE_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in zone_lower:
                    return category

        return 'OTHER'

    def read_temperature(self, zone_path: str, is_hwmon: bool = False) -> Optional[float]:
        """
        Read temperature from a thermal zone file

        Args:
            zone_path: Path to temperature file
            is_hwmon: Whether this is a hwmon sensor (different units)

        Returns:
            Temperature in Celsius, or None if read failed
        """
        try:
            with open(zone_path, 'r') as f:
                raw_value = int(f.read().strip())

            # Convert to Celsius
            # thermal_zone sensors are in millidegrees (e.g., 45000 = 45.0°C)
            # hwmon sensors are also typically in millidegrees
            temp_c = raw_value / 1000.0

            return temp_c
        except (FileNotFoundError, ValueError, PermissionError) as e:
            logger.debug(f"Could not read temperature from {zone_path}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error reading {zone_path}: {e}")
            return None

    def get_all_temperatures(self) -> Dict[str, Optional[float]]:
        """
        Read temperatures from all detected thermal zones

        Returns:
            Dictionary mapping zone_id to temperature in Celsius
        """
        temperatures = {}

        for zone_id, zone_info in self.thermal_zones.items():
            temp = self.read_temperature(
                zone_info['path'],
                is_hwmon=zone_info['hwmon']
            )
            temperatures[zone_id] = temp

        return temperatures

    def get_max_temperature(self) -> Tuple[Optional[float], Optional[str], Optional[str]]:
        """
        Get the maximum temperature across all thermal zones

        Returns:
            Tuple of (max_temp, zone_id, zone_name)
            Returns (None, None, None) if no valid readings
        """
        max_temp = None
        max_zone_id = None
        max_zone_name = None

        temps = self.get_all_temperatures()

        for zone_id, temp in temps.items():
            if temp is not None:
                if max_temp is None or temp > max_temp:
                    max_temp = temp
                    max_zone_id = zone_id
                    max_zone_name = self.thermal_zones[zone_id]['name']

        return max_temp, max_zone_id, max_zone_name

    def get_thermal_status(self) -> Dict:
        """
        Get comprehensive thermal status for UI display

        Returns:
            Dictionary with thermal metrics:
            {
                'max_temp': float,
                'max_zone': str,
                'all_temps': dict,
                'warning': bool,
                'critical': bool,
                'zones_by_type': dict
            }
        """
        temps = self.get_all_temperatures()
        max_temp, max_zone_id, max_zone_name = self.get_max_temperature()

        # Group temperatures by type (CPU, GPU, SOC, etc.)
        zones_by_type = {}
        for zone_id, temp in temps.items():
            if temp is None:
                continue

            zone_type = self.thermal_zones[zone_id]['type']
            if zone_type not in zones_by_type:
                zones_by_type[zone_type] = []

            zones_by_type[zone_type].append({
                'zone_id': zone_id,
                'name': self.thermal_zones[zone_id]['name'],
                'temp': temp
            })

        # Calculate average per type
        type_averages = {}
        for zone_type, zones in zones_by_type.items():
            temps_list = [z['temp'] for z in zones]
            type_averages[zone_type] = sum(temps_list) / len(temps_list)

        return {
            'max_temp': max_temp,
            'max_zone': max_zone_name or 'Unknown',
            'max_zone_id': max_zone_id,
            'all_temps': temps,
            'warning': max_temp is not None and max_temp >= self.warning_threshold,
            'critical': max_temp is not None and max_temp >= self.kill_threshold,
            'zones_by_type': zones_by_type,
            'type_averages': type_averages
        }

    def _monitoring_loop(self):
        """Background monitoring loop"""
        logger.info(f"Starting thermal monitoring (PID: {self.pid})")
        logger.info(f"Thresholds - Warning: {self.warning_threshold}°C, Kill: {self.kill_threshold}°C")

        while self.running:
            try:
                status = self.get_thermal_status()
                max_temp = status['max_temp']
                max_zone = status['max_zone']

                if max_temp is None:
                    logger.debug("No thermal readings available")
                    time.sleep(self.check_interval)
                    continue

                # Log current temperature status
                type_str = " | ".join([
                    f"{t}: {avg:.1f}°C"
                    for t, avg in sorted(status['type_averages'].items())
                ])

                if status['critical']:
                    # CRITICAL - exceeds kill threshold
                    logger.critical(f"🔥 CRITICAL THERMAL EVENT 🔥")
                    logger.critical(f"Temperature: {max_temp:.1f}°C (Zone: {max_zone})")
                    logger.critical(f"Kill threshold ({self.kill_threshold}°C) exceeded!")
                    logger.critical(f"All zones: {type_str}")
                    logger.critical(f"🛑 Killing process {self.pid} to prevent hardware damage")

                    # Log thermal event
                    self._log_thermal_event('CRITICAL_SHUTDOWN', status)

                    # Kill the process
                    self._kill_process()
                    return

                elif status['warning']:
                    # WARNING - approaching danger zone
                    logger.warning(f"⚠️  THERMAL WARNING")
                    logger.warning(f"Temperature: {max_temp:.1f}°C (Zone: {max_zone})")
                    logger.warning(f"Approaching kill threshold ({self.kill_threshold}°C)")
                    logger.warning(f"All zones: {type_str}")

                    # Log thermal event
                    self._log_thermal_event('WARNING', status)

                else:
                    # Normal operation
                    logger.info(f"[Thermal] Max: {max_temp:.1f}°C ({max_zone}) | {type_str}")

                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(self.check_interval)

    def _log_thermal_event(self, event_type: str, status: Dict):
        """
        Log thermal events to file

        Args:
            event_type: Event severity (WARNING, CRITICAL_SHUTDOWN)
            status: Thermal status dictionary
        """
        try:
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)

            log_file = log_dir / 'thermal_events.log'

            event = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'event_type': event_type,
                'max_temp': status['max_temp'],
                'max_zone': status['max_zone'],
                'max_zone_id': status['max_zone_id'],
                'type_averages': status['type_averages'],
                'all_temps': {
                    zone_id: temp
                    for zone_id, temp in status['all_temps'].items()
                    if temp is not None
                },
                'pid': self.pid
            }

            with open(log_file, 'a') as f:
                import json
                f.write(json.dumps(event) + '\n')

        except Exception as e:
            logger.error(f"Failed to log thermal event: {e}")

    def _kill_process(self):
        """Kill the monitored process"""
        try:
            logger.critical(f"Sending SIGTERM to process {self.pid}")
            os.kill(self.pid, signal.SIGTERM)
            time.sleep(2)

            # If still alive, force kill
            try:
                logger.critical(f"Sending SIGKILL to process {self.pid}")
                os.kill(self.pid, signal.SIGKILL)
            except ProcessLookupError:
                logger.info(f"Process {self.pid} terminated successfully")

        except ProcessLookupError:
            logger.warning(f"Process {self.pid} already terminated")
        except Exception as e:
            logger.error(f"Error killing process: {e}", exc_info=True)

    def start(self):
        """Start background monitoring"""
        if not self.running:
            logger.warning("Watchdog not running - cannot start")
            return

        if not self.thermal_zones:
            logger.warning("No thermal zones detected - monitoring disabled")
            return

        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="ThermalWatchdog"
        )
        self.monitoring_thread.start()
        logger.info("Thermal watchdog started")

    def stop(self):
        """Stop monitoring"""
        logger.info("Stopping thermal watchdog")
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)


def test_watchdog():
    """Test the thermal watchdog functionality"""
    print("=" * 60)
    print("THERMAL WATCHDOG TEST")
    print("=" * 60)

    watchdog = ThermalWatchdog(
        warning_threshold=75.0,
        kill_threshold=85.0,
        check_interval=2
    )

    print(f"\nDetected Thermal Zones: {len(watchdog.thermal_zones)}")
    print("-" * 60)

    # Display all zones
    for zone_id, zone_info in watchdog.thermal_zones.items():
        print(f"{zone_id:20s} | {zone_info['type']:8s} | {zone_info['name']}")

    print("\n" + "=" * 60)
    print("CURRENT TEMPERATURES")
    print("=" * 60)

    # Get current status
    status = watchdog.get_thermal_status()

    if status['max_temp'] is None:
        print("⚠️  No temperature readings available")
    else:
        print(f"\nMax Temperature: {status['max_temp']:.1f}°C ({status['max_zone']})")
        print(f"Status: ", end="")
        if status['critical']:
            print("🔥 CRITICAL")
        elif status['warning']:
            print("⚠️  WARNING")
        else:
            print("✓ NORMAL")

        print("\nBy Zone Type:")
        print("-" * 60)
        for zone_type, avg_temp in sorted(status['type_averages'].items()):
            print(f"{zone_type:10s}: {avg_temp:6.1f}°C")

        print("\nAll Zones:")
        print("-" * 60)
        for zone_id, temp in sorted(status['all_temps'].items()):
            if temp is not None:
                zone_name = watchdog.thermal_zones[zone_id]['name']
                zone_type = watchdog.thermal_zones[zone_id]['type']
                print(f"{zone_id:20s} | {zone_type:8s} | {temp:6.1f}°C | {zone_name}")

    print("\n" + "=" * 60)
    print("WATCHDOG CONFIGURATION")
    print("=" * 60)
    print(f"Warning Threshold: {watchdog.warning_threshold}°C")
    print(f"Kill Threshold:    {watchdog.kill_threshold}°C")
    print(f"Check Interval:    {watchdog.check_interval}s")
    print(f"Monitored PID:     {watchdog.pid}")

    print("\n" + "=" * 60)
    print("STARTING 10-SECOND MONITORING TEST")
    print("=" * 60)

    watchdog.start()

    try:
        for i in range(5):
            time.sleep(2)
            status = watchdog.get_thermal_status()
            if status['max_temp'] is not None:
                print(f"[{i+1}/5] Max temp: {status['max_temp']:.1f}°C ({status['max_zone']})")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")

    watchdog.stop()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    test_watchdog()
