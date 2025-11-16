# Thermal Watchdog Integration Guide

## Overview

The `ThermalWatchdog` module monitors system thermal zones and provides emergency shutdown capabilities to prevent physical hardware damage from overheating during intensive AI workloads.

## Features

- **Multi-Zone Monitoring**: Detects and monitors all available thermal zones (`/sys/class/thermal/thermal_zone*/temp`)
- **Jetson-Specific Detection**: Automatically categorizes CPU, GPU, SOC, PMIC, and CV zones
- **Dual Threshold System**: Warning alerts at 75°C, emergency shutdown at 85°C
- **Background Monitoring**: Non-blocking thread-based monitoring
- **Event Logging**: Records thermal events to `logs/thermal_events.log`
- **Web UI Ready**: Provides `get_thermal_status()` for real-time display

## Integration into Neural Link

### Basic Integration (Parallel to GPU Watchdog)

Add to `src/core/neural_link.py`:

```python
from src.utils.thermal_watchdog import ThermalWatchdog

class NeuralLinkSystem:
    def __init__(self, args):
        # ... existing initialization ...

        # Initialize GPU watchdog (existing)
        self.gpu_watchdog = GPUMemoryWatchdog(
            threshold_percent=85,
            check_interval=5
        )
        self.gpu_watchdog.start()

        # Initialize Thermal watchdog (NEW)
        self.thermal_watchdog = ThermalWatchdog(
            warning_threshold=75.0,  # Warning at 75°C
            kill_threshold=85.0,      # Emergency shutdown at 85°C
            check_interval=5          # Check every 5 seconds
        )
        self.thermal_watchdog.start()
        self.console.print("[yellow]Thermal Watchdog started - will terminate if temp exceeds 85°C[/yellow]")
```

### Update State Tracking

Add thermal status to system state:

```python
self.state = {
    # ... existing state fields ...
    "thermal_status": {},  # Will hold thermal metrics
}
```

### Update Status Method

Modify the status update loop to include thermal data:

```python
def update_status(self):
    """Update system status including thermal monitoring"""
    # ... existing status updates ...

    # Get thermal status
    if hasattr(self, 'thermal_watchdog'):
        thermal_status = self.thermal_watchdog.get_thermal_status()
        self.state['thermal_status'] = thermal_status

        # Update display with thermal info
        if thermal_status['max_temp'] is not None:
            self.state['cpu_temp'] = thermal_status['max_temp']
```

### Cleanup on Shutdown

Add cleanup to shutdown handler:

```python
def cleanup(self):
    """Cleanup resources on shutdown"""
    # Stop watchdogs
    if hasattr(self, 'gpu_watchdog'):
        self.gpu_watchdog.stop()

    if hasattr(self, 'thermal_watchdog'):
        self.thermal_watchdog.stop()

    # ... existing cleanup ...
```

## Web Interface Integration

### Update Flask Routes

Add thermal endpoint to `src/web/app.py`:

```python
@app.route('/api/thermal')
@token_required
def get_thermal_status():
    """Get thermal status for all running instances"""
    thermal_data = {}

    for name, system in systems.items():
        if hasattr(system, 'thermal_watchdog'):
            status = system.thermal_watchdog.get_thermal_status()
            thermal_data[name] = status

    return jsonify(thermal_data)
```

### WebSocket Updates

Include thermal data in real-time updates:

```python
def emit_system_update(system_name, system):
    """Emit real-time system update via WebSocket"""
    update = {
        'name': system_name,
        'state': system.state,
        'thermal': system.thermal_watchdog.get_thermal_status() if hasattr(system, 'thermal_watchdog') else None
    }
    socketio.emit('system_update', update)
```

## UI Display Example

### Terminal UI (Rich)

```python
from rich.panel import Panel
from rich.text import Text

def create_thermal_panel(thermal_status):
    """Create thermal status panel for terminal UI"""
    if not thermal_status or thermal_status['max_temp'] is None:
        return Panel("Thermal monitoring unavailable", title="🌡️ Temperature")

    max_temp = thermal_status['max_temp']
    max_zone = thermal_status['max_zone']

    # Color based on temperature
    if thermal_status['critical']:
        color = "red"
        status_icon = "🔥"
    elif thermal_status['warning']:
        color = "yellow"
        status_icon = "⚠️ "
    else:
        color = "green"
        status_icon = "✓"

    # Build display text
    text = Text()
    text.append(f"{status_icon} {max_temp:.1f}°C ", style=f"bold {color}")
    text.append(f"({max_zone})\n", style="dim")

    # Show by zone type
    for zone_type, avg_temp in sorted(thermal_status['type_averages'].items()):
        text.append(f"{zone_type}: {avg_temp:.1f}°C\n", style=color)

    return Panel(text, title="🌡️ Temperature")
```

### Web UI (JavaScript)

```javascript
function updateThermalDisplay(thermalStatus) {
    if (!thermalStatus || thermalStatus.max_temp === null) {
        return;
    }

    const maxTemp = thermalStatus.max_temp;
    const maxZone = thermalStatus.max_zone;

    // Determine status color
    let statusClass = 'normal';
    let statusIcon = '✓';

    if (thermalStatus.critical) {
        statusClass = 'critical';
        statusIcon = '🔥';
    } else if (thermalStatus.warning) {
        statusClass = 'warning';
        statusIcon = '⚠️';
    }

    // Update display
    const thermalDiv = document.getElementById('thermal-status');
    thermalDiv.className = `thermal-status ${statusClass}`;
    thermalDiv.innerHTML = `
        <div class="thermal-header">
            <span class="status-icon">${statusIcon}</span>
            <span class="temp-value">${maxTemp.toFixed(1)}°C</span>
            <span class="temp-zone">${maxZone}</span>
        </div>
        <div class="thermal-zones">
            ${Object.entries(thermalStatus.type_averages)
                .map(([type, temp]) => `
                    <div class="zone-item">
                        <span class="zone-name">${type}</span>
                        <span class="zone-temp">${temp.toFixed(1)}°C</span>
                    </div>
                `).join('')}
        </div>
    `;
}
```

## Jetson-Specific Thermal Zones

On NVIDIA Jetson devices, you'll typically see these zones:

### Jetson Orin AGX
- **CPU-therm**: CPU complex temperature
- **GPU-therm**: GPU die temperature
- **SOC**: System-on-Chip overall temperature
- **CV0/CV1/CV2**: Computer Vision engine temperatures
- **Tboard**: Board temperature sensor
- **PMIC**: Power Management IC temperature

### Jetson Xavier NX
- **MCPU**: Main CPU cluster
- **GPU**: GPU temperature
- **AUX**: Auxiliary sensors
- **AO-therm**: Always-On domain

### Example Output

```
Detected Thermal Zones: 8
------------------------------------------------------------
thermal_zone0        | CPU      | CPU-therm
thermal_zone1        | GPU      | GPU-therm
thermal_zone2        | SOC      | SOC
thermal_zone3        | CV       | CV0
thermal_zone4        | CV       | CV1
thermal_zone5        | CV       | CV2
thermal_zone6        | PMIC     | Tboard
thermal_zone7        | OTHER    | AUX

============================================================
CURRENT TEMPERATURES
============================================================

Max Temperature: 52.3°C (GPU-therm)
Status: ✓ NORMAL

By Zone Type:
------------------------------------------------------------
CPU       :   48.5°C
GPU       :   52.3°C
SOC       :   45.2°C
CV        :   46.8°C
PMIC      :   42.0°C
OTHER     :   41.5°C
```

## Configuration Recommendations

### Jetson Orin AGX (64GB)
```python
ThermalWatchdog(
    warning_threshold=75.0,  # Start logging warnings
    kill_threshold=85.0,     # Emergency shutdown
    check_interval=5         # Check every 5 seconds
)
```

### Jetson Xavier NX
```python
ThermalWatchdog(
    warning_threshold=70.0,  # More conservative
    kill_threshold=80.0,     # Lower threshold for smaller device
    check_interval=3         # Check more frequently
)
```

### Raspberry Pi 5
```python
ThermalWatchdog(
    warning_threshold=70.0,  # Pi throttles at ~80°C
    kill_threshold=78.0,     # Shutdown before throttling
    check_interval=3
)
```

## Thermal Event Log Format

Events are logged to `logs/thermal_events.log` in JSON format:

```json
{
  "timestamp": "2025-11-16 14:32:15",
  "event_type": "WARNING",
  "max_temp": 76.5,
  "max_zone": "GPU-therm",
  "max_zone_id": "thermal_zone1",
  "type_averages": {
    "CPU": 72.3,
    "GPU": 76.5,
    "SOC": 68.4
  },
  "all_temps": {
    "thermal_zone0": 72.3,
    "thermal_zone1": 76.5,
    "thermal_zone2": 68.4
  },
  "pid": 12345
}
```

## Testing

Test the watchdog without running the full system:

```bash
# Run standalone test
python3 -m src.utils.thermal_watchdog

# Check detected zones
python3 -c "
from src.utils.thermal_watchdog import ThermalWatchdog
tw = ThermalWatchdog()
print(f'Detected {len(tw.thermal_zones)} thermal zones')
for zone_id, info in tw.thermal_zones.items():
    print(f'  {zone_id}: {info[\"name\"]} ({info[\"type\"]})')
"

# Monitor current temperature
python3 -c "
from src.utils.thermal_watchdog import ThermalWatchdog
tw = ThermalWatchdog()
status = tw.get_thermal_status()
if status['max_temp']:
    print(f'Max temp: {status[\"max_temp\"]:.1f}°C ({status[\"max_zone\"]})')
else:
    print('No thermal data available')
"
```

## Troubleshooting

### No Thermal Zones Detected

**Symptom**: `WARNING - No thermal zones detected - monitoring disabled`

**Solutions**:
1. Check if `/sys/class/thermal/` exists: `ls -la /sys/class/thermal/`
2. On Jetson, ensure Jetson services are running: `sudo systemctl status jetson_clocks`
3. Check permissions: `ls -la /sys/class/thermal/thermal_zone*/temp`
4. Try hwmon interface: `ls -la /sys/class/hwmon/`

### Permission Denied Reading Temperature

**Symptom**: `Could not read temperature from /sys/class/thermal/thermal_zone0/temp`

**Solutions**:
1. Run with appropriate permissions (usually not needed for read)
2. Check file permissions: `ls -l /sys/class/thermal/thermal_zone*/temp`
3. Add user to appropriate group if needed

### False Thermal Shutdowns

**Symptom**: Process killed at lower temperatures than expected

**Solutions**:
1. Increase `kill_threshold` parameter
2. Verify temperature readings: `cat /sys/class/thermal/thermal_zone*/temp`
3. Check thermal event log: `cat logs/thermal_events.log`
4. Monitor with: `watch -n 1 'cat /sys/class/thermal/thermal_zone*/temp'`

## Performance Impact

- **CPU Usage**: Negligible (~0.1% on background thread)
- **Memory**: <5MB for zone metadata and monitoring thread
- **I/O**: Minimal - reads small sysfs files every 5 seconds
- **Latency**: Does not block main inference loop

## Safety Considerations

1. **Conservative Thresholds**: Default 85°C is safe for Jetson (max spec ~95°C), but leaves margin
2. **Graceful Shutdown**: Uses SIGTERM first, then SIGKILL for clean process termination
3. **Event Logging**: All thermal events logged for post-mortem analysis
4. **Fail-Safe**: If monitoring fails, it logs errors but doesn't crash the system
5. **No False Negatives**: If any zone exceeds threshold, shutdown triggers

## Integration Checklist

- [ ] Import `ThermalWatchdog` in `neural_link.py`
- [ ] Initialize watchdog in `__init__`
- [ ] Start watchdog with `start()` method
- [ ] Add thermal status to system state
- [ ] Update web API to expose thermal data
- [ ] Add thermal display to terminal UI
- [ ] Add thermal display to web UI
- [ ] Update WebSocket emissions with thermal data
- [ ] Test on target hardware (Jetson/Pi)
- [ ] Verify thermal event logging
- [ ] Configure appropriate thresholds for device
- [ ] Document device-specific thermal behavior

## Future Enhancements

Potential improvements for future versions:

1. **Fan Control**: Trigger fan speed increases at warning threshold
2. **Power Throttling**: Reduce model inference rate before shutdown
3. **Thermal History**: Track temperature trends over time
4. **Predictive Shutdown**: Machine learning to predict thermal runaway
5. **Per-Zone Thresholds**: Different limits for CPU vs GPU
6. **Recovery Mode**: Automatic restart after cooldown period
7. **Alert Notifications**: Email/webhook when temperatures spike
8. **Thermal Profiling**: Log thermal behavior per model/workload

## References

- Jetson Thermal Management: https://docs.nvidia.com/jetson/archives/r35.1/DeveloperGuide/text/SD/PlatformPowerAndPerformance/JetsonOrinNxSeriesAndJetsonAgxOrinSeries.html
- Linux Thermal Framework: https://www.kernel.org/doc/html/latest/driver-api/thermal/index.html
- Raspberry Pi Thermal: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#temperature-monitoring
