#!/usr/bin/env python3
"""
Experiment Profiler for Season 3

Profiles experiment execution to identify performance bottlenecks:
- Time per cycle
- LLM inference timing
- Memory usage tracking
- GPU utilization (Jetson)
- Database query times
- Mode-specific overhead
"""

import time
import psutil
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
import json
import statistics


@dataclass
class TimingMeasurement:
    """Single timing measurement"""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self):
        """Mark measurement as complete"""
        if self.end_time is None:
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time


@dataclass
class MemorySnapshot:
    """Memory usage snapshot"""
    timestamp: float
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    percent: float
    available_mb: float
    gpu_used_mb: Optional[float] = None
    gpu_total_mb: Optional[float] = None


@dataclass
class CycleProfile:
    """Performance profile for a single experiment cycle"""
    cycle_number: int
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None

    # Timing breakdowns
    timings: List[TimingMeasurement] = field(default_factory=list)

    # Memory tracking
    memory_snapshots: List[MemorySnapshot] = field(default_factory=list)
    peak_memory_mb: float = 0.0

    # LLM metrics
    llm_inference_count: int = 0
    llm_total_time: float = 0.0
    tokens_generated: int = 0
    tokens_per_second: float = 0.0

    # Database metrics
    db_queries: int = 0
    db_total_time: float = 0.0

    # Mode-specific
    mode_overhead_ms: float = 0.0
    intervention_time_ms: float = 0.0

    # GPU metrics (Jetson)
    gpu_utilization_percent: Optional[float] = None
    gpu_temperature_c: Optional[float] = None
    cpu_temperature_c: Optional[float] = None

    # Metadata
    crashed: bool = False
    crash_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self):
        """Mark cycle as complete and calculate metrics"""
        if self.end_time is None:
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time

        # Calculate tokens per second
        if self.llm_total_time > 0:
            self.tokens_per_second = self.tokens_generated / self.llm_total_time


@dataclass
class ExperimentProfile:
    """Complete performance profile for an experiment"""
    experiment_id: str
    experiment_name: str
    mode: str
    start_time: float
    end_time: Optional[float] = None
    total_duration: Optional[float] = None

    # Cycle profiles
    cycles: List[CycleProfile] = field(default_factory=list)

    # Aggregate metrics
    total_llm_time: float = 0.0
    total_db_time: float = 0.0
    total_tokens: int = 0
    avg_tokens_per_second: float = 0.0

    # Resource usage
    peak_memory_mb: float = 0.0
    avg_memory_mb: float = 0.0

    # Bottleneck analysis
    bottlenecks: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # System info
    system_info: Dict[str, Any] = field(default_factory=dict)

    def complete(self):
        """Finalize profile and calculate aggregate metrics"""
        if self.end_time is None:
            self.end_time = time.time()
            self.total_duration = self.end_time - self.start_time

        # Calculate aggregates
        if self.cycles:
            self.total_llm_time = sum(c.llm_total_time for c in self.cycles)
            self.total_db_time = sum(c.db_total_time for c in self.cycles)
            self.total_tokens = sum(c.tokens_generated for c in self.cycles)

            if self.total_llm_time > 0:
                self.avg_tokens_per_second = self.total_tokens / self.total_llm_time

            # Memory stats
            all_memory = [s.rss_mb for c in self.cycles for s in c.memory_snapshots]
            if all_memory:
                self.peak_memory_mb = max(all_memory)
                self.avg_memory_mb = statistics.mean(all_memory)


class ExperimentProfiler:
    """
    Main profiler for experiments

    Usage:
        profiler = ExperimentProfiler(experiment_id, experiment_name, mode)

        # In experiment runner
        profiler.start_experiment()

        for cycle in cycles:
            profiler.start_cycle(cycle_num)

            with profiler.time("llm_inference"):
                # Run LLM
                pass

            with profiler.time("database_write"):
                # Write to DB
                pass

            profiler.end_cycle()

        profiler.end_experiment()
        profile = profiler.get_profile()
    """

    def __init__(self, experiment_id: str, experiment_name: str, mode: str,
                 enable_jetson_profiling: bool = False):
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        self.mode = mode
        self.enable_jetson_profiling = enable_jetson_profiling

        # Profile data
        self.profile = ExperimentProfile(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            mode=mode,
            start_time=0.0,
            system_info=self._collect_system_info()
        )

        # Current cycle
        self.current_cycle: Optional[CycleProfile] = None

        # Memory monitoring thread
        self._memory_monitor_thread: Optional[threading.Thread] = None
        self._monitoring = False
        self._monitor_interval = 0.5  # seconds

        # GPU monitoring (Jetson)
        self.gpu_monitor = None
        if enable_jetson_profiling:
            try:
                from .jetson_gpu_monitor import JetsonGPUMonitor
                self.gpu_monitor = JetsonGPUMonitor()
            except ImportError:
                pass

    def start_experiment(self):
        """Start profiling an experiment"""
        self.profile.start_time = time.time()
        self._start_memory_monitoring()

    def end_experiment(self):
        """End experiment profiling"""
        self._stop_memory_monitoring()
        self.profile.complete()
        self._analyze_bottlenecks()
        self._generate_recommendations()

    def start_cycle(self, cycle_number: int):
        """Start profiling a cycle"""
        if self.current_cycle:
            # End previous cycle if not ended
            self.end_cycle()

        self.current_cycle = CycleProfile(
            cycle_number=cycle_number,
            start_time=time.time()
        )

    def end_cycle(self, crashed: bool = False, crash_reason: Optional[str] = None):
        """End current cycle profiling"""
        if not self.current_cycle:
            return

        self.current_cycle.crashed = crashed
        self.current_cycle.crash_reason = crash_reason
        self.current_cycle.complete()

        # Get GPU metrics if available
        if self.gpu_monitor:
            gpu_stats = self.gpu_monitor.get_stats()
            self.current_cycle.gpu_utilization_percent = gpu_stats.get('gpu_utilization')
            self.current_cycle.gpu_temperature_c = gpu_stats.get('gpu_temp')
            self.current_cycle.cpu_temperature_c = gpu_stats.get('cpu_temp')

        self.profile.cycles.append(self.current_cycle)
        self.current_cycle = None

    def time(self, name: str, **metadata):
        """Context manager for timing code blocks"""
        return TimingContext(self, name, metadata)

    def record_timing(self, name: str, duration: float, **metadata):
        """Manually record a timing measurement"""
        if not self.current_cycle:
            return

        measurement = TimingMeasurement(
            name=name,
            start_time=time.time() - duration,
            end_time=time.time(),
            duration=duration,
            metadata=metadata
        )
        self.current_cycle.timings.append(measurement)

        # Update cycle metrics
        if "llm" in name.lower():
            self.current_cycle.llm_inference_count += 1
            self.current_cycle.llm_total_time += duration
            if 'tokens' in metadata:
                self.current_cycle.tokens_generated += metadata['tokens']

        elif "db" in name.lower() or "database" in name.lower():
            self.current_cycle.db_queries += 1
            self.current_cycle.db_total_time += duration

        elif "mode" in name.lower():
            self.current_cycle.mode_overhead_ms += duration * 1000

        elif "intervention" in name.lower():
            self.current_cycle.intervention_time_ms += duration * 1000

    def record_memory_snapshot(self):
        """Record current memory usage"""
        if not self.current_cycle:
            return

        # CPU memory
        process = psutil.Process()
        mem_info = process.memory_info()
        vm = psutil.virtual_memory()

        snapshot = MemorySnapshot(
            timestamp=time.time(),
            rss_mb=mem_info.rss / (1024 * 1024),
            vms_mb=mem_info.vms / (1024 * 1024),
            percent=process.memory_percent(),
            available_mb=vm.available / (1024 * 1024)
        )

        # GPU memory (Jetson)
        if self.gpu_monitor:
            gpu_mem = self.gpu_monitor.get_memory_usage()
            snapshot.gpu_used_mb = gpu_mem.get('used_mb')
            snapshot.gpu_total_mb = gpu_mem.get('total_mb')

        self.current_cycle.memory_snapshots.append(snapshot)

        # Update peak
        if snapshot.rss_mb > self.current_cycle.peak_memory_mb:
            self.current_cycle.peak_memory_mb = snapshot.rss_mb

    def get_profile(self) -> ExperimentProfile:
        """Get the complete profile"""
        return self.profile

    def export_json(self, output_path: str):
        """Export profile to JSON"""
        data = {
            'experiment_id': self.profile.experiment_id,
            'experiment_name': self.profile.experiment_name,
            'mode': self.profile.mode,
            'start_time': self.profile.start_time,
            'end_time': self.profile.end_time,
            'total_duration': self.profile.total_duration,
            'system_info': self.profile.system_info,
            'aggregate_metrics': {
                'total_cycles': len(self.profile.cycles),
                'total_llm_time': self.profile.total_llm_time,
                'total_db_time': self.profile.total_db_time,
                'total_tokens': self.profile.total_tokens,
                'avg_tokens_per_second': self.profile.avg_tokens_per_second,
                'peak_memory_mb': self.profile.peak_memory_mb,
                'avg_memory_mb': self.profile.avg_memory_mb,
            },
            'cycles': [self._cycle_to_dict(c) for c in self.profile.cycles],
            'bottlenecks': self.profile.bottlenecks,
            'recommendations': self.profile.recommendations
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _cycle_to_dict(self, cycle: CycleProfile) -> Dict[str, Any]:
        """Convert cycle profile to dict"""
        return {
            'cycle_number': cycle.cycle_number,
            'duration': cycle.duration,
            'crashed': cycle.crashed,
            'crash_reason': cycle.crash_reason,
            'llm_metrics': {
                'inference_count': cycle.llm_inference_count,
                'total_time': cycle.llm_total_time,
                'tokens_generated': cycle.tokens_generated,
                'tokens_per_second': cycle.tokens_per_second
            },
            'db_metrics': {
                'queries': cycle.db_queries,
                'total_time': cycle.db_total_time
            },
            'memory_metrics': {
                'peak_mb': cycle.peak_memory_mb,
                'snapshots': len(cycle.memory_snapshots)
            },
            'gpu_metrics': {
                'utilization_percent': cycle.gpu_utilization_percent,
                'temperature_c': cycle.gpu_temperature_c
            } if cycle.gpu_utilization_percent else None,
            'timings': [
                {
                    'name': t.name,
                    'duration': t.duration,
                    'metadata': t.metadata
                }
                for t in cycle.timings
            ]
        }

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        import platform

        info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'total_memory_gb': psutil.virtual_memory().total / (1024**3),
        }

        # Check if Jetson
        if Path('/etc/nv_tegra_release').exists():
            info['is_jetson'] = True
            try:
                with open('/etc/nv_tegra_release', 'r') as f:
                    info['jetson_version'] = f.read().strip()
            except:
                pass

        return info

    def _start_memory_monitoring(self):
        """Start background memory monitoring"""
        self._monitoring = True
        self._memory_monitor_thread = threading.Thread(
            target=self._memory_monitor_loop,
            daemon=True
        )
        self._memory_monitor_thread.start()

    def _stop_memory_monitoring(self):
        """Stop background memory monitoring"""
        self._monitoring = False
        if self._memory_monitor_thread:
            self._memory_monitor_thread.join(timeout=2.0)

    def _memory_monitor_loop(self):
        """Background loop for memory monitoring"""
        while self._monitoring:
            if self.current_cycle:
                self.record_memory_snapshot()
            time.sleep(self._monitor_interval)

    def _analyze_bottlenecks(self):
        """Analyze performance data to identify bottlenecks"""
        if not self.profile.cycles:
            return

        # Calculate average cycle time
        cycle_times = [c.duration for c in self.profile.cycles if c.duration]
        if not cycle_times:
            return

        avg_cycle_time = statistics.mean(cycle_times)

        # LLM bottleneck
        avg_llm_time = statistics.mean([c.llm_total_time for c in self.profile.cycles])
        llm_percentage = (avg_llm_time / avg_cycle_time * 100) if avg_cycle_time > 0 else 0

        if llm_percentage > 60:
            self.profile.bottlenecks.append({
                'type': 'llm_inference',
                'severity': 'high',
                'percentage_of_cycle': llm_percentage,
                'avg_time_seconds': avg_llm_time,
                'description': f'LLM inference takes {llm_percentage:.1f}% of cycle time'
            })

        # Database bottleneck
        avg_db_time = statistics.mean([c.db_total_time for c in self.profile.cycles])
        db_percentage = (avg_db_time / avg_cycle_time * 100) if avg_cycle_time > 0 else 0

        if db_percentage > 15:
            self.profile.bottlenecks.append({
                'type': 'database',
                'severity': 'medium' if db_percentage < 30 else 'high',
                'percentage_of_cycle': db_percentage,
                'avg_time_seconds': avg_db_time,
                'description': f'Database operations take {db_percentage:.1f}% of cycle time'
            })

        # Mode overhead
        avg_mode_time = statistics.mean([c.mode_overhead_ms / 1000 for c in self.profile.cycles])
        mode_percentage = (avg_mode_time / avg_cycle_time * 100) if avg_cycle_time > 0 else 0

        if mode_percentage > 10:
            self.profile.bottlenecks.append({
                'type': 'mode_overhead',
                'severity': 'medium',
                'percentage_of_cycle': mode_percentage,
                'avg_time_seconds': avg_mode_time,
                'description': f'Mode processing overhead is {mode_percentage:.1f}% of cycle time'
            })

        # Memory pressure
        if self.profile.peak_memory_mb > self.profile.system_info['total_memory_gb'] * 1024 * 0.8:
            self.profile.bottlenecks.append({
                'type': 'memory_pressure',
                'severity': 'high',
                'peak_mb': self.profile.peak_memory_mb,
                'system_total_mb': self.profile.system_info['total_memory_gb'] * 1024,
                'description': 'Peak memory usage exceeds 80% of system memory'
            })

        # Slow cycles
        max_cycle_time = max(cycle_times)
        if max_cycle_time > avg_cycle_time * 2:
            slow_cycles = [c for c in self.profile.cycles
                          if c.duration and c.duration > avg_cycle_time * 1.5]
            self.profile.bottlenecks.append({
                'type': 'slow_cycles',
                'severity': 'medium',
                'slow_cycle_count': len(slow_cycles),
                'slowest_duration': max_cycle_time,
                'avg_duration': avg_cycle_time,
                'description': f'{len(slow_cycles)} cycles significantly slower than average'
            })

    def _generate_recommendations(self):
        """Generate optimization recommendations based on bottlenecks"""
        recommendations = []

        for bottleneck in self.profile.bottlenecks:
            if bottleneck['type'] == 'llm_inference':
                recommendations.extend([
                    "Consider reducing context window size to speed up inference",
                    "Try quantizing model to Q4_0 or Q4_1 if not already",
                    "Increase GPU layers if running on Jetson to offload work",
                    "Reduce max_tokens_per_response to decrease generation time"
                ])

            elif bottleneck['type'] == 'database':
                recommendations.extend([
                    "Batch database writes instead of writing each message individually",
                    "Add indexes to frequently queried columns",
                    "Consider using in-memory database for hot data",
                    "Reduce logging verbosity to decrease DB writes"
                ])

            elif bottleneck['type'] == 'mode_overhead':
                recommendations.extend([
                    f"Optimize {self.mode} mode's memory processing logic",
                    "Cache frequently accessed mode state",
                    "Reduce complexity of memory corruption algorithms"
                ])

            elif bottleneck['type'] == 'memory_pressure':
                recommendations.extend([
                    "Reduce RAM limit in experiment config",
                    "Decrease context window to reduce memory usage",
                    "Clear conversation history more aggressively",
                    "Use smaller model variant"
                ])

            elif bottleneck['type'] == 'slow_cycles':
                recommendations.append(
                    "Investigate specific slow cycles to identify anomalies"
                )

        # Add general recommendations
        if self.profile.avg_tokens_per_second < 5:
            recommendations.append(
                f"Token generation speed is low ({self.profile.avg_tokens_per_second:.2f} tok/s). "
                "Consider model optimization or hardware upgrade"
            )

        self.profile.recommendations = list(set(recommendations))  # Remove duplicates


class TimingContext:
    """Context manager for timing operations"""

    def __init__(self, profiler: ExperimentProfiler, name: str, metadata: Dict[str, Any]):
        self.profiler = profiler
        self.name = name
        self.metadata = metadata
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.profiler.record_timing(self.name, duration, **self.metadata)
        return False


# Decorator for profiling functions
def profile_function(profiler: ExperimentProfiler, name: Optional[str] = None):
    """Decorator to profile a function"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            func_name = name or func.__name__
            with profiler.time(func_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
