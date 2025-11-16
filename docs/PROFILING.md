# Performance Profiling & Optimization Guide

## Overview

The brain-in-jar Season 3 infrastructure includes comprehensive performance profiling and optimization tools designed to identify bottlenecks and optimize experiment execution.

## Components

### 1. ExperimentProfiler (`src/infra/profiler.py`)

Profiles experiment execution to track:
- **Time per cycle** - How long each resurrection cycle takes
- **LLM inference timing** - Model inference performance
- **Memory usage** - RAM consumption over time
- **GPU utilization** - GPU usage on Jetson platforms
- **Database query times** - Database overhead
- **Mode-specific overhead** - Time spent in mode operations

**Usage:**
```python
from src.infra.profiler import ExperimentProfiler

profiler = ExperimentProfiler(
    experiment_id="test_001",
    experiment_name="My Experiment",
    mode="amnesiac_loop",
    enable_jetson_profiling=True  # Enable GPU profiling on Jetson
)

profiler.start_experiment()

for cycle in range(10):
    profiler.start_cycle(cycle)

    # Time specific operations
    with profiler.time("llm_inference", tokens=150):
        # Run LLM inference
        pass

    with profiler.time("database_write"):
        # Write to database
        pass

    profiler.end_cycle()

profiler.end_experiment()

# Export results
profiler.export_json("profile.json")
profile = profiler.get_profile()
```

### 2. PerformanceMonitor (`src/infra/performance_monitor.py`)

Real-time system monitoring with alerting:
- **CPU/GPU/RAM usage** - Per-process and system-wide
- **Temperature monitoring** - Critical for Jetson thermal management
- **Throttling detection** - Identifies thermal or power throttling
- **Disk space** - Monitor storage availability
- **Network latency** - For multi-node experiments

**Usage:**
```python
from src.infra.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor(
    sample_interval=1.0,
    enable_alerts=True,
    enable_jetson_monitoring=True
)

# Set alert thresholds
monitor.set_threshold('memory_percent', 85, severity='warning')
monitor.set_threshold('memory_percent', 95, severity='critical')
monitor.set_threshold('cpu_temp_c', 75, severity='warning')

# Register alert handler
def on_alert(alert):
    print(f"ALERT: {alert.message}")

monitor.on_alert(on_alert)

# Start monitoring
monitor.start()

# ... run experiment ...

# Stop and get results
monitor.stop()
summary = monitor.get_summary_stats()
alerts = monitor.get_alerts(severity='critical')
```

### 3. ExperimentOptimizer (`src/infra/optimizer.py`)

Analyzes profiles and generates optimization recommendations:
- **RAM allocation** - Optimal memory limits
- **Batch size tuning** - Optimize throughput
- **Context window** - Balance quality vs. memory
- **Thread count** - CPU utilization optimization
- **GPU layers** - Jetson GPU offloading

**Usage:**
```python
from src.infra.optimizer import ExperimentOptimizer

optimizer = ExperimentOptimizer(target_platform='jetson_orin')

# Load profile
optimizer.load_profile_from_file('profile.json')

# Generate recommendations
recommendations = optimizer.generate_recommendations()

for rec in recommendations:
    if rec.priority == 'high':
        print(f"{rec.title}: {rec.description}")
        print(f"  Current: {rec.current_value}")
        print(f"  Recommended: {rec.recommended_value}")

# Apply to config
with open('config.json') as f:
    config = json.load(f)

optimized_config = optimizer.apply_recommendations(
    config,
    recommendations,
    apply_high_only=True
)

# Save optimized config
with open('config_optimized.json', 'w') as f:
    json.dump(optimized_config, f, indent=2)
```

### 4. CLI Profiler (`scripts/profile_experiment.py`)

Complete command-line profiling tool with HTML report generation.

**Basic Usage:**
```bash
# Simple profiling
python scripts/profile_experiment.py \
    --config experiments/examples/amnesiac_total.json

# Full profiling with custom output
python scripts/profile_experiment.py \
    --config experiments/examples/amnesiac_total.json \
    --profile-output logs/profiles/my_profile.json \
    --report-output logs/reports/my_report.html

# Jetson profiling with optimization
python scripts/profile_experiment.py \
    --config experiments/examples/amnesiac_total.json \
    --enable-jetson \
    --optimize-config \
    --optimized-config-output experiments/optimized/amnesiac_opt.json
```

**Options:**
- `--config` - Experiment configuration file (required)
- `--profile-output` - JSON profile output path
- `--report-output` - HTML report output path
- `--enable-jetson` - Enable Jetson GPU profiling
- `--optimize-config` - Generate optimized configuration
- `--sample-interval` - Monitoring sample rate (default: 1.0s)

## Metrics Tracked

### Performance Metrics
- **Tokens/Second** - LLM generation speed
- **Cycle Duration** - Time per resurrection cycle
- **Memory Usage** - RAM consumption (RSS, VMS)
- **GPU Utilization** - GPU usage percentage (Jetson)
- **Database Time** - Time spent in DB operations

### System Metrics
- **CPU Usage** - Per-core and aggregate
- **CPU Temperature** - Thermal monitoring
- **GPU Temperature** - GPU thermal state (Jetson)
- **Memory Percent** - System memory pressure
- **Disk Space** - Available storage

### Quality Metrics
- **Inference Count** - Number of LLM calls
- **Tokens Generated** - Total token output
- **Crash Rate** - Frequency of OOM crashes
- **Mode Overhead** - Time in mode processing

## Bottleneck Analysis

The profiler automatically identifies common bottlenecks:

### LLM Inference Bottleneck
**Symptoms:** LLM inference takes >60% of cycle time

**Recommendations:**
- Reduce context window (4096 → 2048)
- Use more aggressive quantization (Q8 → Q4_0)
- Reduce max tokens per response
- Increase GPU layers on Jetson

### Memory Pressure
**Symptoms:** Peak memory >80% of system RAM

**Recommendations:**
- Reduce RAM limit in config
- Smaller context window
- More aggressive memory clearing
- Use smaller model

### Database Overhead
**Symptoms:** DB operations >15% of cycle time

**Recommendations:**
- Batch database writes
- Reduce logging verbosity
- Use in-memory DB with periodic flush
- Add database indexes

### Mode Overhead
**Symptoms:** Mode processing >10% of cycle time

**Recommendations:**
- Optimize memory corruption algorithms
- Cache mode state
- Simplify prompt generation

### Thermal Throttling (Jetson)
**Symptoms:** GPU temp >75°C, frequency drops

**Recommendations:**
- Reduce GPU layers
- Improve cooling (fan, heatsink)
- Lower power mode
- Reduce inference batch size

## Jetson-Specific Features

### GPU Profiling
- **CUDA utilization** - GPU core usage
- **Memory bandwidth** - GPU memory throughput
- **Power consumption** - Watts consumed
- **Temperature** - GPU and CPU thermal state
- **Tensor core usage** - Specialized AI cores

### Thermal Management
The profiler tracks thermal state and detects throttling:

```python
# Thermal throttling detection
if gpu_temp > 75 and frequency_drop > 20%:
    alert("Thermal throttling detected")
```

**Prevention:**
1. Monitor temps continuously
2. Reduce GPU layers if temps exceed 70°C
3. Use MAXN power mode for consistent performance
4. Ensure adequate cooling

### Power Modes
Jetson power modes affect performance:

- **MAXN** - Maximum performance (highest power)
- **15W** - Balanced mode
- **10W** - Power-saving mode

Check current mode:
```bash
sudo nvpmodel -q
```

Set MAXN mode:
```bash
sudo nvpmodel -m 0
```

### DLA (Deep Learning Accelerator)
Jetson Orin includes DLA engines for efficient inference:

- Offload compatible layers to DLA
- Lower power consumption vs GPU
- Limited operator support

## Optimization Workflow

### 1. Profile Baseline
```bash
python scripts/profile_experiment.py \
    --config experiments/examples/amnesiac_total.json \
    --profile-output logs/baseline_profile.json \
    --report-output logs/baseline_report.html
```

### 2. Review Report
Open `logs/baseline_report.html` in browser:
- Check bottlenecks section
- Review high-priority recommendations
- Note peak memory and avg tokens/sec

### 3. Generate Optimized Config
```bash
python scripts/profile_experiment.py \
    --config experiments/examples/amnesiac_total.json \
    --optimize-config \
    --optimized-config-output experiments/amnesiac_optimized.json
```

### 4. Profile Optimized Version
```bash
python scripts/profile_experiment.py \
    --config experiments/amnesiac_optimized.json \
    --profile-output logs/optimized_profile.json \
    --report-output logs/optimized_report.html
```

### 5. Compare Results
```python
# Compare profiles
import json

with open('logs/baseline_profile.json') as f:
    baseline = json.load(f)

with open('logs/optimized_profile.json') as f:
    optimized = json.load(f)

baseline_tps = baseline['aggregate_metrics']['avg_tokens_per_second']
optimized_tps = optimized['aggregate_metrics']['avg_tokens_per_second']

speedup = optimized_tps / baseline_tps
print(f"Speedup: {speedup:.2f}x ({baseline_tps:.2f} → {optimized_tps:.2f} tok/s)")
```

## Integration with Experiment Runner

The profiler integrates seamlessly with the experiment runner:

```python
from src.runner.experiment_runner import ExperimentRunner
from src.infra.profiler import ExperimentProfiler

class ProfiledRunner(ExperimentRunner):
    def __init__(self, config, db_path, profiler):
        super().__init__(config, db_path)
        self.profiler = profiler

    def _run_cycle_simulation(self):
        with self.profiler.time("mode_processing"):
            processed_memory = self.mode.process_memory(
                self.state.conversation_history,
                self.state
            )

        with self.profiler.time("llm_inference", tokens=150):
            # Run LLM
            pass

        with self.profiler.time("database_write"):
            # Write to DB
            pass
```

## Example Output

### Profile JSON
```json
{
  "experiment_name": "Total Episodic Amnesia",
  "mode": "amnesiac_loop",
  "total_duration": 245.5,
  "aggregate_metrics": {
    "total_cycles": 10,
    "avg_tokens_per_second": 14.7,
    "peak_memory_mb": 2847.3
  },
  "bottlenecks": [
    {
      "type": "llm_inference",
      "severity": "high",
      "percentage_of_cycle": 51.7
    }
  ]
}
```

### HTML Report
The HTML report includes:
- Visual charts of cycle performance
- Bottleneck highlights
- Optimization recommendations
- System information table
- Exportable data

## Best Practices

### 1. Profile Early
Run profiling on the first experiment run to establish baseline.

### 2. Profile Representative Workloads
Use realistic cycle counts and configurations.

### 3. Monitor Continuously
Use PerformanceMonitor for long-running experiments.

### 4. Iterate
Profile → Optimize → Profile → Compare

### 5. Track Over Time
Save profiles with timestamps to track regression.

### 6. Platform-Specific
Profile on target hardware (Jetson vs x86).

### 7. Thermal Awareness
On Jetson, always monitor temperatures.

## Troubleshooting

### Low Tokens/Second
- Check GPU utilization (should be >70%)
- Verify model quantization
- Check thermal throttling
- Review CPU thread count

### High Memory Usage
- Reduce context window
- Clear history more aggressively
- Use smaller model
- Check for memory leaks

### Database Slowness
- Batch writes
- Add indexes
- Use WAL mode
- Consider in-memory DB

### Thermal Throttling (Jetson)
- Improve cooling
- Reduce GPU layers
- Lower power mode
- Check fan operation

## Advanced Usage

### Custom Metrics
```python
profiler.record_timing(
    "custom_operation",
    duration=2.5,
    custom_metric=42
)
```

### Manual Memory Snapshots
```python
profiler.record_memory_snapshot()
```

### Alert Callbacks
```python
def critical_alert_handler(alert):
    send_email(f"Critical alert: {alert.message}")

monitor.on_alert(critical_alert_handler)
```

### Export Formats
```python
# JSON
profiler.export_json("profile.json")

# Custom export
profile = profiler.get_profile()
# ... process as needed ...
```

## Performance Targets

### Jetson Orin AGX
- **Tokens/sec:** 15-25 (Q4_0 quantization)
- **Memory:** <50% of 16GB
- **GPU temp:** <70°C sustained
- **GPU util:** 70-90%

### Jetson Nano
- **Tokens/sec:** 3-7 (Q4_0 quantization)
- **Memory:** <50% of 4GB
- **GPU temp:** <65°C sustained
- **GPU util:** 80-95%

### x86_64 (CPU-only)
- **Tokens/sec:** 5-15 (depends on CPU)
- **Memory:** <4GB
- **CPU util:** 70-90%
- **Thread scaling:** Near-linear to core count

## References

- **llama.cpp**: Model inference engine
- **psutil**: System monitoring library
- **jtop**: Jetson monitoring tool
- **tegrastats**: NVIDIA Jetson stats
