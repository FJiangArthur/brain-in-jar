# Thermal Watchdog

Emergency thermal protection system for preventing physical hardware damage during intensive AI workloads.

## Quick Start

```python
from src.utils.thermal_watchdog import ThermalWatchdog

# Initialize with default thresholds
watchdog = ThermalWatchdog(
    warning_threshold=75.0,  # Warning at 75°C
    kill_threshold=85.0,      # Emergency shutdown at 85°C
    check_interval=5          # Check every 5 seconds
)

# Start background monitoring
watchdog.start()

# Get current thermal status
status = watchdog.get_thermal_status()
if status['max_temp']:
    print(f"Max temp: {status['max_temp']:.1f}°C ({status['max_zone']})")
    print(f"Warning: {status['warning']}, Critical: {status['critical']}")

# Stop monitoring
watchdog.stop()
```

## Features

- **Multi-Zone Monitoring**: Automatically detects all `/sys/class/thermal/thermal_zone*` sensors
- **Jetson Detection**: Categorizes CPU, GPU, SOC, PMIC, and CV zones
- **Dual Thresholds**: Warning alerts + emergency shutdown
- **Background Thread**: Non-blocking monitoring
- **Event Logging**: Records thermal events to `logs/thermal_events.log`
- **Web UI Ready**: Provides structured status for real-time display

## Hardware Support

### Jetson Orin AGX
Typical zones: CPU-therm, GPU-therm, SOC, CV0-CV2, Tboard, PMIC

### Jetson Xavier NX
Typical zones: MCPU, GPU, AUX, AO-therm

### Raspberry Pi 5
Typical zones: cpu-thermal

## Configuration

### Jetson Orin AGX (64GB)
```python
ThermalWatchdog(warning_threshold=75.0, kill_threshold=85.0, check_interval=5)
```

### Jetson Xavier NX
```python
ThermalWatchdog(warning_threshold=70.0, kill_threshold=80.0, check_interval=3)
```

### Raspberry Pi 5
```python
ThermalWatchdog(warning_threshold=70.0, kill_threshold=78.0, check_interval=3)
```

## Integration Pattern

Follows the same pattern as `GPUMemoryWatchdog`:

1. Import in `neural_link.py`
2. Initialize in `__init__`
3. Start watchdog
4. Update system state with thermal status
5. Display in terminal/web UI
6. Stop in cleanup

See `docs/THERMAL_WATCHDOG_INTEGRATION.md` for detailed integration guide.

## Testing

```bash
# Run standalone test
python3 -m src.utils.thermal_watchdog

# Run unit tests
python3 -m unittest tests.test_thermal_watchdog

# Run integration example
python3 examples/thermal_integration_example.py
```

## API Reference

### `ThermalWatchdog(warning_threshold=75.0, kill_threshold=85.0, check_interval=5, pid=None)`

Main watchdog class.

**Parameters:**
- `warning_threshold`: Temperature (°C) to start logging warnings
- `kill_threshold`: Temperature (°C) to kill process
- `check_interval`: Seconds between checks
- `pid`: Process ID to monitor (default: current process)

### `get_all_thermal_zones() -> Dict`

Detect all available thermal zones.

**Returns:** Dictionary of zone metadata

### `get_all_temperatures() -> Dict[str, float]`

Read temperatures from all zones.

**Returns:** Dictionary mapping zone_id to temperature in °C

### `get_max_temperature() -> Tuple[float, str, str]`

Get maximum temperature across all zones.

**Returns:** `(max_temp, zone_id, zone_name)`

### `get_thermal_status() -> Dict`

Get comprehensive thermal status.

**Returns:**
```python
{
    'max_temp': 52.3,           # Maximum temperature
    'max_zone': 'GPU-therm',    # Name of hottest zone
    'max_zone_id': 'zone1',     # Zone identifier
    'all_temps': {...},         # All zone temperatures
    'warning': False,           # Above warning threshold
    'critical': False,          # Above kill threshold
    'zones_by_type': {...},     # Grouped by type (CPU, GPU, etc.)
    'type_averages': {...}      # Average per type
}
```

### `start()`

Start background monitoring thread.

### `stop()`

Stop monitoring and clean up.

## Thermal Event Log Format

Events are logged to `logs/thermal_events.log` in JSON:

```json
{
  "timestamp": "2025-11-16 14:32:15",
  "event_type": "WARNING",
  "max_temp": 76.5,
  "max_zone": "GPU-therm",
  "max_zone_id": "thermal_zone1",
  "type_averages": {"CPU": 72.3, "GPU": 76.5, "SOC": 68.4},
  "all_temps": {"thermal_zone0": 72.3, "thermal_zone1": 76.5},
  "pid": 12345
}
```

Event types:
- `WARNING`: Temperature exceeded warning threshold
- `CRITICAL_SHUTDOWN`: Temperature exceeded kill threshold, process terminated

## Files

- `src/utils/thermal_watchdog.py` - Main module
- `tests/test_thermal_watchdog.py` - Unit tests
- `docs/THERMAL_WATCHDOG_INTEGRATION.md` - Integration guide
- `examples/thermal_integration_example.py` - Usage examples
- `logs/thermal_events.log` - Event log (created at runtime)

## Safety Notes

1. **Conservative Defaults**: 85°C kill threshold is safe for Jetson (max spec ~95°C)
2. **Graceful Shutdown**: SIGTERM first, then SIGKILL
3. **Fail-Safe**: Monitoring failures log errors but don't crash
4. **No False Negatives**: Any zone exceeding threshold triggers shutdown

## Troubleshooting

**No zones detected**: Check `/sys/class/thermal/` exists and is readable

**Permission denied**: Ensure read access to `/sys/class/thermal/thermal_zone*/temp`

**False shutdowns**: Increase `kill_threshold` or verify readings with:
```bash
cat /sys/class/thermal/thermal_zone*/temp
```

## Performance

- CPU: ~0.1% on background thread
- Memory: <5MB
- I/O: Minimal (reads small sysfs files every 5 seconds)
- No impact on main inference loop

## License

Part of Brain in a Jar project - See main project LICENSE
