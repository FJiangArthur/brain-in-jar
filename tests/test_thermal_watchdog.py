#!/usr/bin/env python3
"""
Unit tests for ThermalWatchdog module
Tests thermal zone detection, temperature reading, and threshold monitoring
"""

import unittest
import tempfile
import shutil
import time
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.thermal_watchdog import ThermalWatchdog


class TestThermalWatchdog(unittest.TestCase):
    """Test cases for ThermalWatchdog"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.thermal_base = Path(self.test_dir) / "sys" / "class" / "thermal"
        self.thermal_base.mkdir(parents=True)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_mock_thermal_zone(self, zone_id, zone_type, temp_millidegrees):
        """
        Create a mock thermal zone for testing

        Args:
            zone_id: Zone identifier (e.g., 'thermal_zone0')
            zone_type: Zone type name (e.g., 'CPU-therm')
            temp_millidegrees: Temperature in millidegrees (e.g., 45000 = 45.0°C)
        """
        zone_dir = self.thermal_base / zone_id
        zone_dir.mkdir()

        # Create type file
        type_file = zone_dir / "type"
        type_file.write_text(zone_type)

        # Create temp file
        temp_file = zone_dir / "temp"
        temp_file.write_text(str(temp_millidegrees))

        return zone_dir

    @patch('src.utils.thermal_watchdog.Path')
    def test_no_thermal_zones(self, mock_path):
        """Test behavior when no thermal zones are available"""
        # Mock Path to point to non-existent directory
        mock_thermal_base = MagicMock()
        mock_thermal_base.exists.return_value = False
        mock_path.return_value = mock_thermal_base

        watchdog = ThermalWatchdog()

        # Should have no zones detected
        self.assertEqual(len(watchdog.thermal_zones), 0)

    def test_zone_categorization(self):
        """Test thermal zone categorization"""
        watchdog = ThermalWatchdog()

        # Test CPU patterns
        self.assertEqual(watchdog._categorize_zone('CPU-therm'), 'CPU')
        self.assertEqual(watchdog._categorize_zone('MCPU'), 'CPU')
        self.assertEqual(watchdog._categorize_zone('cpu-thermal'), 'CPU')

        # Test GPU patterns
        self.assertEqual(watchdog._categorize_zone('GPU-therm'), 'GPU')
        self.assertEqual(watchdog._categorize_zone('gpu'), 'GPU')

        # Test SOC patterns
        self.assertEqual(watchdog._categorize_zone('SOC'), 'SOC')
        self.assertEqual(watchdog._categorize_zone('AO-therm'), 'SOC')

        # Test PMIC patterns
        self.assertEqual(watchdog._categorize_zone('PMIC'), 'PMIC')
        self.assertEqual(watchdog._categorize_zone('Tboard'), 'PMIC')

        # Test CV patterns
        self.assertEqual(watchdog._categorize_zone('CV0'), 'CV')
        self.assertEqual(watchdog._categorize_zone('CV1'), 'CV')

        # Test unknown
        self.assertEqual(watchdog._categorize_zone('unknown-sensor'), 'OTHER')

    def test_temperature_reading(self):
        """Test reading temperature from mock zones"""
        # Create mock zones
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU-therm', 45000)
        zone1 = self.create_mock_thermal_zone('thermal_zone1', 'GPU-therm', 52500)

        watchdog = ThermalWatchdog()

        # Manually set thermal zones for testing
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            },
            'zone1': {
                'path': str(zone1 / 'temp'),
                'name': 'GPU-therm',
                'type': 'GPU',
                'hwmon': False
            }
        }

        # Read temperatures
        temps = watchdog.get_all_temperatures()

        # Verify temperatures
        self.assertAlmostEqual(temps['zone0'], 45.0, places=1)
        self.assertAlmostEqual(temps['zone1'], 52.5, places=1)

    def test_max_temperature(self):
        """Test getting maximum temperature"""
        # Create mock zones
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU-therm', 45000)
        zone1 = self.create_mock_thermal_zone('thermal_zone1', 'GPU-therm', 72500)
        zone2 = self.create_mock_thermal_zone('thermal_zone2', 'SOC', 38000)

        watchdog = ThermalWatchdog()

        # Manually set thermal zones
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            },
            'zone1': {
                'path': str(zone1 / 'temp'),
                'name': 'GPU-therm',
                'type': 'GPU',
                'hwmon': False
            },
            'zone2': {
                'path': str(zone2 / 'temp'),
                'name': 'SOC',
                'type': 'SOC',
                'hwmon': False
            }
        }

        # Get max temperature
        max_temp, max_zone_id, max_zone_name = watchdog.get_max_temperature()

        # Should be GPU at 72.5°C
        self.assertAlmostEqual(max_temp, 72.5, places=1)
        self.assertEqual(max_zone_id, 'zone1')
        self.assertEqual(max_zone_name, 'GPU-therm')

    def test_thermal_status(self):
        """Test comprehensive thermal status"""
        # Create mock zones
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU-therm', 65000)
        zone1 = self.create_mock_thermal_zone('thermal_zone1', 'GPU-therm', 78000)

        watchdog = ThermalWatchdog(warning_threshold=75.0, kill_threshold=85.0)

        # Manually set thermal zones
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            },
            'zone1': {
                'path': str(zone1 / 'temp'),
                'name': 'GPU-therm',
                'type': 'GPU',
                'hwmon': False
            }
        }

        # Get status
        status = watchdog.get_thermal_status()

        # Verify status
        self.assertAlmostEqual(status['max_temp'], 78.0, places=1)
        self.assertEqual(status['max_zone'], 'GPU-therm')
        self.assertTrue(status['warning'])  # Above 75°C
        self.assertFalse(status['critical'])  # Below 85°C

        # Verify zones by type
        self.assertIn('CPU', status['zones_by_type'])
        self.assertIn('GPU', status['zones_by_type'])

        # Verify type averages
        self.assertAlmostEqual(status['type_averages']['CPU'], 65.0, places=1)
        self.assertAlmostEqual(status['type_averages']['GPU'], 78.0, places=1)

    def test_warning_threshold(self):
        """Test warning threshold detection"""
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU-therm', 76000)

        watchdog = ThermalWatchdog(warning_threshold=75.0, kill_threshold=85.0)
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            }
        }

        status = watchdog.get_thermal_status()

        # Should be in warning state
        self.assertTrue(status['warning'])
        self.assertFalse(status['critical'])

    def test_critical_threshold(self):
        """Test critical threshold detection"""
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU-therm', 86000)

        watchdog = ThermalWatchdog(warning_threshold=75.0, kill_threshold=85.0)
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            }
        }

        status = watchdog.get_thermal_status()

        # Should be in critical state
        self.assertTrue(status['warning'])
        self.assertTrue(status['critical'])

    def test_normal_threshold(self):
        """Test normal operation below warning threshold"""
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU-therm', 50000)

        watchdog = ThermalWatchdog(warning_threshold=75.0, kill_threshold=85.0)
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            }
        }

        status = watchdog.get_thermal_status()

        # Should be in normal state
        self.assertFalse(status['warning'])
        self.assertFalse(status['critical'])

    def test_invalid_temperature_file(self):
        """Test handling of invalid temperature file"""
        zone_dir = self.thermal_base / "thermal_zone0"
        zone_dir.mkdir()

        # Create type file
        type_file = zone_dir / "type"
        type_file.write_text("CPU-therm")

        # Create invalid temp file
        temp_file = zone_dir / "temp"
        temp_file.write_text("invalid_number")

        watchdog = ThermalWatchdog()
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(temp_file),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            }
        }

        # Should return None for invalid temperature
        temp = watchdog.read_temperature(str(temp_file))
        self.assertIsNone(temp)

    def test_missing_temperature_file(self):
        """Test handling of missing temperature file"""
        watchdog = ThermalWatchdog()

        # Try to read non-existent file
        temp = watchdog.read_temperature('/nonexistent/path/temp')
        self.assertIsNone(temp)

    def test_start_stop_watchdog(self):
        """Test starting and stopping the watchdog"""
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU-therm', 45000)

        watchdog = ThermalWatchdog(check_interval=1)
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            }
        }

        # Start watchdog
        watchdog.start()
        self.assertIsNotNone(watchdog.monitoring_thread)
        self.assertTrue(watchdog.running)

        # Let it run briefly
        time.sleep(0.5)

        # Stop watchdog
        watchdog.stop()
        self.assertFalse(watchdog.running)

    def test_no_zones_prevents_monitoring(self):
        """Test that monitoring doesn't start if no zones detected"""
        watchdog = ThermalWatchdog()
        watchdog.thermal_zones = {}  # No zones

        # Try to start
        watchdog.start()

        # Should not have started monitoring thread
        self.assertIsNone(watchdog.monitoring_thread)

    @patch('os.kill')
    def test_process_kill(self, mock_kill):
        """Test that process is killed at critical temperature"""
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU-therm', 86000)

        watchdog = ThermalWatchdog(
            warning_threshold=75.0,
            kill_threshold=85.0,
            check_interval=1
        )
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU-therm',
                'type': 'CPU',
                'hwmon': False
            }
        }

        # Manually call kill process
        watchdog._kill_process()

        # Verify kill was called with SIGTERM
        import signal
        mock_kill.assert_called()
        # First call should be SIGTERM
        first_call = mock_kill.call_args_list[0]
        self.assertEqual(first_call[0][1], signal.SIGTERM)

    def test_multiple_zones_same_type(self):
        """Test averaging multiple zones of same type"""
        # Create multiple CPU zones
        zone0 = self.create_mock_thermal_zone('thermal_zone0', 'CPU0-therm', 60000)
        zone1 = self.create_mock_thermal_zone('thermal_zone1', 'CPU1-therm', 64000)

        watchdog = ThermalWatchdog()
        watchdog.thermal_zones = {
            'zone0': {
                'path': str(zone0 / 'temp'),
                'name': 'CPU0-therm',
                'type': 'CPU',
                'hwmon': False
            },
            'zone1': {
                'path': str(zone1 / 'temp'),
                'name': 'CPU1-therm',
                'type': 'CPU',
                'hwmon': False
            }
        }

        status = watchdog.get_thermal_status()

        # Should have 2 CPU zones
        self.assertEqual(len(status['zones_by_type']['CPU']), 2)

        # Average should be (60 + 64) / 2 = 62
        self.assertAlmostEqual(status['type_averages']['CPU'], 62.0, places=1)


class TestThermalWatchdogIntegration(unittest.TestCase):
    """Integration tests for ThermalWatchdog"""

    def test_real_system_zones(self):
        """Test detection on real system (if available)"""
        watchdog = ThermalWatchdog()

        # Check if any zones were detected
        num_zones = len(watchdog.thermal_zones)
        print(f"\nDetected {num_zones} thermal zones on this system")

        if num_zones > 0:
            # Get current status
            status = watchdog.get_thermal_status()

            if status['max_temp'] is not None:
                print(f"Max temperature: {status['max_temp']:.1f}°C ({status['max_zone']})")
                print(f"Type averages: {status['type_averages']}")

                # Basic sanity checks
                self.assertGreater(status['max_temp'], 0)
                self.assertLess(status['max_temp'], 150)  # Should never be this hot!
            else:
                print("No temperature readings available")
        else:
            print("No thermal zones available on this system (expected for non-Jetson/Pi)")

    def test_instantiation_defaults(self):
        """Test default parameter values"""
        watchdog = ThermalWatchdog()

        self.assertEqual(watchdog.warning_threshold, 75.0)
        self.assertEqual(watchdog.kill_threshold, 85.0)
        self.assertEqual(watchdog.check_interval, 5)
        self.assertEqual(watchdog.pid, os.getpid())
        self.assertTrue(watchdog.running)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
