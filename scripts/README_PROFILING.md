# Profiling Scripts Quick Reference

## profile_experiment.py

Complete CLI tool for profiling experiments with performance analysis and optimization.

### Quick Start

```bash
# Basic profiling
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

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--config` | Experiment config file (required) | - |
| `--profile-output` | JSON profile output path | `logs/profiles/experiment_profile.json` |
| `--report-output` | HTML report output path | `logs/reports/performance_report.html` |
| `--db` | Database path | `logs/experiments.db` |
| `--enable-jetson` | Enable Jetson GPU profiling | `False` |
| `--optimize-config` | Generate optimized config | `False` |
| `--optimized-config-output` | Optimized config path | Auto-generated |
| `--sample-interval` | Monitor sample rate (seconds) | `1.0` |

### Output Files

1. **Profile JSON** (`logs/profiles/*.json`)
   - Complete performance metrics
   - Cycle-by-cycle breakdown
   - Bottleneck analysis
   - System information

2. **HTML Report** (`logs/reports/*.html`)
   - Interactive charts
   - Visual bottleneck highlights
   - Optimization recommendations
   - System details table

3. **Optimized Config** (`experiments/optimized/*.json`)
   - Auto-tuned configuration
   - Platform-specific optimizations
   - High-priority recommendations applied

### Example Workflow

```bash
# 1. Profile baseline
python scripts/profile_experiment.py \
    --config experiments/examples/amnesiac_total.json \
    --profile-output logs/profiles/baseline.json \
    --report-output logs/reports/baseline.html

# 2. Review report (open in browser)
firefox logs/reports/baseline.html

# 3. Generate optimized config
python scripts/profile_experiment.py \
    --config experiments/examples/amnesiac_total.json \
    --optimize-config \
    --optimized-config-output experiments/optimized/amnesiac_opt.json

# 4. Profile optimized version
python scripts/profile_experiment.py \
    --config experiments/optimized/amnesiac_opt.json \
    --profile-output logs/profiles/optimized.json \
    --report-output logs/reports/optimized.html

# 5. Compare results
# (Open both HTML reports to compare)
```

### Jetson-Specific Usage

On Jetson Orin/Nano platforms:

```bash
# Enable Jetson profiling
python scripts/profile_experiment.py \
    --config experiments/examples/amnesiac_total.json \
    --enable-jetson \
    --profile-output logs/profiles/jetson_profile.json

# Ensure jtop is installed for full GPU monitoring
sudo pip3 install jetson-stats

# Check power mode
sudo nvpmodel -q

# Set MAXN mode for best performance
sudo nvpmodel -m 0
```

### Programmatic Usage

```python
from src.infra import ExperimentProfiler, PerformanceMonitor, ExperimentOptimizer

# Create profiler
profiler = ExperimentProfiler(
    experiment_id="exp_001",
    experiment_name="My Experiment",
    mode="amnesiac_loop",
    enable_jetson_profiling=True
)

# Create monitor
monitor = PerformanceMonitor(
    sample_interval=1.0,
    enable_alerts=True,
    enable_jetson_monitoring=True
)

# Set thresholds
monitor.set_threshold('memory_percent', 85, severity='warning')
monitor.set_threshold('cpu_temp_c', 75, severity='warning')

# Alert handler
monitor.on_alert(lambda alert: print(f"ALERT: {alert.message}"))

# Start profiling
profiler.start_experiment()
monitor.start()

# ... run experiment ...

# Stop profiling
monitor.stop()
profiler.end_experiment()

# Export
profiler.export_json("profile.json")

# Optimize
optimizer = ExperimentOptimizer()
optimizer.load_profile_from_file("profile.json")
recommendations = optimizer.generate_recommendations()
```

### Metrics Tracked

#### Performance
- Cycle duration
- LLM inference time
- Tokens per second
- Database query time
- Mode processing overhead

#### System
- CPU usage (per-core)
- Memory usage (RSS, VMS, %)
- GPU utilization (Jetson)
- Temperature (CPU, GPU)
- Disk space

#### Quality
- Tokens generated
- Crash frequency
- Response variability

### Bottlenecks Detected

1. **LLM Inference** - Slow model performance
2. **Memory Pressure** - High RAM usage
3. **Database Overhead** - Slow DB operations
4. **Mode Overhead** - Expensive mode logic
5. **Thermal Throttling** - Heat-induced slowdown (Jetson)

### Optimization Categories

1. **Memory** - RAM limits, context window
2. **CPU** - Thread count, affinity
3. **GPU** - Layer count, thermal management (Jetson)
4. **Model** - Quantization, token limits
5. **Database** - Batching, indexing

### Performance Targets

#### Jetson Orin AGX
- Tokens/sec: 15-25
- Memory: <50% of 16GB
- GPU temp: <70°C
- GPU util: 70-90%

#### Jetson Nano
- Tokens/sec: 3-7
- Memory: <50% of 4GB
- GPU temp: <65°C
- GPU util: 80-95%

#### x86_64 (CPU)
- Tokens/sec: 5-15
- Memory: <4GB
- CPU util: 70-90%

### Troubleshooting

**Low tokens/sec:**
- Check GPU utilization
- Verify model quantization
- Review thread count
- Check for thermal throttling

**High memory:**
- Reduce context window
- Lower RAM limit
- Use smaller model
- Check for leaks

**Database slowness:**
- Batch writes
- Add indexes
- Use in-memory mode

**Thermal issues (Jetson):**
- Improve cooling
- Reduce GPU layers
- Check fan operation
- Lower power mode

### See Also

- **Full Documentation:** `docs/PROFILING.md`
- **Example Code:** `examples/profiling_demo.py`
- **Example Profile:** `logs/profiles/example_amnesiac_profile.json`

---

*For detailed documentation, see `docs/PROFILING.md`*
