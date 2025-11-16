#!/usr/bin/env python3
"""
Real-time Performance Monitor for Season 3

Monitors system performance during experiment execution:
- CPU/GPU/RAM usage per process
- Temperature monitoring (critical on Jetson)
- Throttling detection
- Network latency (multi-node experiments)
- Real-time alerts for issues
"""

import time
import psutil
import threading
import queue
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from pathlib import Path
import warnings


@dataclass
class PerformanceMetrics:
    """Snapshot of system performance metrics"""
    timestamp: float

    # CPU
    cpu_percent: float
    cpu_per_core: List[float]
    cpu_freq_mhz: Optional[float]
    cpu_temp_c: Optional[float]

    # Memory
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    swap_percent: float

    # GPU (Jetson)
    gpu_percent: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    gpu_temp_c: Optional[float] = None
    gpu_power_watts: Optional[float] = None

    # Process-specific
    process_cpu_percent: Optional[float] = None
    process_memory_mb: Optional[float] = None
    process_threads: Optional[int] = None

    # System health
    thermal_throttling: bool = False
    disk_space_percent: Optional[float] = None

    # Network (for multi-node)
    network_latency_ms: Optional[float] = None
    network_bandwidth_mbps: Optional[float] = None


@dataclass
class Alert:
    """Performance alert"""
    timestamp: float
    severity: str  # 'warning', 'critical'
    category: str  # 'memory', 'cpu', 'gpu', 'thermal', 'disk'
    message: str
    value: Any
    threshold: Any


class PerformanceMonitor:
    """
    Real-time performance monitoring with alerting

    Usage:
        monitor = PerformanceMonitor(
            sample_interval=1.0,
            enable_alerts=True
        )

        # Set alert thresholds
        monitor.set_threshold('memory_percent', 85, severity='warning')
        monitor.set_threshold('memory_percent', 95, severity='critical')
        monitor.set_threshold('cpu_temp_c', 75, severity='warning')

        # Register alert handlers
        monitor.on_alert(lambda alert: print(f"ALERT: {alert.message}"))

        # Start monitoring
        monitor.start()

        # ... run experiment ...

        # Stop monitoring
        monitor.stop()
        metrics_history = monitor.get_metrics_history()
    """

    def __init__(self,
                 sample_interval: float = 1.0,
                 enable_alerts: bool = True,
                 enable_jetson_monitoring: bool = False,
                 track_process: bool = True):
        """
        Initialize performance monitor

        Args:
            sample_interval: Seconds between samples
            enable_alerts: Enable alert system
            enable_jetson_monitoring: Enable Jetson-specific GPU monitoring
            track_process: Track current process metrics
        """
        self.sample_interval = sample_interval
        self.enable_alerts = enable_alerts
        self.enable_jetson = enable_jetson_monitoring
        self.track_process = track_process

        # Metrics storage
        self.metrics_history: List[PerformanceMetrics] = []
        self.alerts: List[Alert] = []

        # Alert thresholds
        self.thresholds: Dict[str, List[Dict[str, Any]]] = {}

        # Alert handlers
        self.alert_handlers: List[Callable[[Alert], None]] = []

        # Monitoring thread
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitoring = False
        self._stop_event = threading.Event()

        # Process reference
        self.process = psutil.Process() if track_process else None

        # Jetson GPU monitor
        self.jetson_monitor = None
        if enable_jetson_monitoring:
            try:
                from .jetson_gpu_monitor import JetsonGPUMonitor
                self.jetson_monitor = JetsonGPUMonitor()
            except ImportError:
                warnings.warn("Jetson GPU monitoring requested but module not available")

        # Baseline metrics for throttling detection
        self._baseline_cpu_freq: Optional[float] = None

    def start(self):
        """Start monitoring in background thread"""
        if self._monitoring:
            return

        self._monitoring = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="PerformanceMonitor"
        )
        self._monitor_thread.start()

        # Capture baseline
        time.sleep(0.1)  # Let it collect one sample
        if self.metrics_history:
            self._baseline_cpu_freq = self.metrics_history[0].cpu_freq_mhz

    def stop(self):
        """Stop monitoring"""
        if not self._monitoring:
            return

        self._monitoring = False
        self._stop_event.set()

        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get most recent metrics snapshot"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None

    def get_metrics_history(self) -> List[PerformanceMetrics]:
        """Get complete metrics history"""
        return self.metrics_history.copy()

    def get_alerts(self, severity: Optional[str] = None) -> List[Alert]:
        """Get alerts, optionally filtered by severity"""
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts.copy()

    def set_threshold(self, metric: str, threshold: Any,
                     severity: str = 'warning',
                     comparison: str = 'greater'):
        """
        Set alert threshold for a metric

        Args:
            metric: Metric name (e.g., 'memory_percent', 'cpu_temp_c')
            threshold: Threshold value
            severity: 'warning' or 'critical'
            comparison: 'greater', 'less', 'equal'
        """
        if metric not in self.thresholds:
            self.thresholds[metric] = []

        self.thresholds[metric].append({
            'threshold': threshold,
            'severity': severity,
            'comparison': comparison
        })

    def on_alert(self, handler: Callable[[Alert], None]):
        """Register alert handler callback"""
        self.alert_handlers.append(handler)

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from metrics history"""
        if not self.metrics_history:
            return {}

        import statistics

        cpu_values = [m.cpu_percent for m in self.metrics_history]
        mem_values = [m.memory_percent for m in self.metrics_history]

        stats = {
            'duration_seconds': self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp,
            'samples_collected': len(self.metrics_history),
            'cpu': {
                'avg_percent': statistics.mean(cpu_values),
                'max_percent': max(cpu_values),
                'min_percent': min(cpu_values),
            },
            'memory': {
                'avg_percent': statistics.mean(mem_values),
                'max_percent': max(mem_values),
                'peak_mb': max(m.memory_used_mb for m in self.metrics_history),
            },
            'alerts': {
                'total': len(self.alerts),
                'warnings': len([a for a in self.alerts if a.severity == 'warning']),
                'critical': len([a for a in self.alerts if a.severity == 'critical']),
            }
        }

        # GPU stats if available
        gpu_values = [m.gpu_percent for m in self.metrics_history if m.gpu_percent is not None]
        if gpu_values:
            stats['gpu'] = {
                'avg_percent': statistics.mean(gpu_values),
                'max_percent': max(gpu_values),
            }

        # Temperature stats
        cpu_temps = [m.cpu_temp_c for m in self.metrics_history if m.cpu_temp_c is not None]
        if cpu_temps:
            stats['cpu']['avg_temp_c'] = statistics.mean(cpu_temps)
            stats['cpu']['max_temp_c'] = max(cpu_temps)

        gpu_temps = [m.gpu_temp_c for m in self.metrics_history if m.gpu_temp_c is not None]
        if gpu_temps:
            stats['gpu'] = stats.get('gpu', {})
            stats['gpu']['avg_temp_c'] = statistics.mean(gpu_temps)
            stats['gpu']['max_temp_c'] = max(gpu_temps)

        # Throttling detection
        throttle_events = sum(1 for m in self.metrics_history if m.thermal_throttling)
        if throttle_events > 0:
            stats['thermal_throttling_events'] = throttle_events

        return stats

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring and not self._stop_event.is_set():
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)

                # Check thresholds
                if self.enable_alerts:
                    self._check_thresholds(metrics)

            except Exception as e:
                warnings.warn(f"Error collecting metrics: {e}")

            # Wait for next sample
            self._stop_event.wait(self.sample_interval)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        timestamp = time.time()

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

        # CPU frequency
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else None

        # CPU temperature
        cpu_temp = self._get_cpu_temperature()

        # Memory
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk
        disk = psutil.disk_usage('/')

        # Process-specific metrics
        process_cpu = None
        process_mem = None
        process_threads = None

        if self.process:
            try:
                process_cpu = self.process.cpu_percent()
                process_mem = self.process.memory_info().rss / (1024 * 1024)
                process_threads = self.process.num_threads()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # GPU metrics (Jetson)
        gpu_percent = None
        gpu_memory = None
        gpu_temp = None
        gpu_power = None

        if self.jetson_monitor:
            gpu_stats = self.jetson_monitor.get_stats()
            gpu_percent = gpu_stats.get('gpu_utilization')
            gpu_temp = gpu_stats.get('gpu_temp')
            gpu_power = gpu_stats.get('power_watts')

            gpu_mem = self.jetson_monitor.get_memory_usage()
            gpu_memory = gpu_mem.get('used_mb')

        # Throttling detection
        thermal_throttling = self._detect_throttling(cpu_freq_mhz, cpu_temp)

        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            cpu_per_core=cpu_per_core,
            cpu_freq_mhz=cpu_freq_mhz,
            cpu_temp_c=cpu_temp,
            memory_percent=vm.percent,
            memory_used_mb=vm.used / (1024 * 1024),
            memory_available_mb=vm.available / (1024 * 1024),
            swap_percent=swap.percent,
            gpu_percent=gpu_percent,
            gpu_memory_mb=gpu_memory,
            gpu_temp_c=gpu_temp,
            gpu_power_watts=gpu_power,
            process_cpu_percent=process_cpu,
            process_memory_mb=process_mem,
            process_threads=process_threads,
            thermal_throttling=thermal_throttling,
            disk_space_percent=disk.percent
        )

    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature"""
        try:
            temps = psutil.sensors_temperatures()

            # Try common sensor names
            for sensor_name in ['coretemp', 'cpu_thermal', 'k10temp', 'zenpower']:
                if sensor_name in temps:
                    entries = temps[sensor_name]
                    if entries:
                        # Return highest temperature
                        return max(e.current for e in entries)

            # Jetson-specific
            if 'thermal-fan-est' in temps:
                return temps['thermal-fan-est'][0].current

        except (AttributeError, KeyError):
            pass

        return None

    def _detect_throttling(self, current_freq: Optional[float],
                          current_temp: Optional[float]) -> bool:
        """Detect if CPU is thermally throttling"""
        if not current_freq or not self._baseline_cpu_freq:
            return False

        # If frequency dropped by more than 20% from baseline
        freq_drop_percent = (self._baseline_cpu_freq - current_freq) / self._baseline_cpu_freq * 100

        if freq_drop_percent > 20:
            # Also check if temperature is high
            if current_temp and current_temp > 70:
                return True

        return False

    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check if any metrics exceed thresholds"""
        for metric_name, thresholds in self.thresholds.items():
            # Get metric value
            value = getattr(metrics, metric_name, None)
            if value is None:
                continue

            for threshold_config in thresholds:
                threshold = threshold_config['threshold']
                severity = threshold_config['severity']
                comparison = threshold_config['comparison']

                # Check threshold
                triggered = False
                if comparison == 'greater' and value > threshold:
                    triggered = True
                elif comparison == 'less' and value < threshold:
                    triggered = True
                elif comparison == 'equal' and value == threshold:
                    triggered = True

                if triggered:
                    alert = Alert(
                        timestamp=metrics.timestamp,
                        severity=severity,
                        category=self._get_metric_category(metric_name),
                        message=self._format_alert_message(metric_name, value, threshold, comparison),
                        value=value,
                        threshold=threshold
                    )

                    self.alerts.append(alert)

                    # Call alert handlers
                    for handler in self.alert_handlers:
                        try:
                            handler(alert)
                        except Exception as e:
                            warnings.warn(f"Alert handler error: {e}")

    def _get_metric_category(self, metric_name: str) -> str:
        """Determine alert category from metric name"""
        if 'memory' in metric_name or 'swap' in metric_name:
            return 'memory'
        elif 'cpu' in metric_name and 'temp' not in metric_name:
            return 'cpu'
        elif 'gpu' in metric_name and 'temp' not in metric_name:
            return 'gpu'
        elif 'temp' in metric_name or 'throttl' in metric_name:
            return 'thermal'
        elif 'disk' in metric_name:
            return 'disk'
        elif 'network' in metric_name:
            return 'network'
        else:
            return 'system'

    def _format_alert_message(self, metric: str, value: Any,
                             threshold: Any, comparison: str) -> str:
        """Format alert message"""
        metric_display = metric.replace('_', ' ').title()

        if comparison == 'greater':
            return f"{metric_display} is {value:.1f} (threshold: {threshold})"
        elif comparison == 'less':
            return f"{metric_display} is {value:.1f} (minimum: {threshold})"
        else:
            return f"{metric_display} is {value:.1f}"


class JetsonGPUMonitor:
    """
    Jetson-specific GPU monitoring using tegrastats and jtop

    Fallback implementation if jtop not available
    """

    def __init__(self):
        self.use_jtop = False

        # Try to use jtop (jetson-stats package)
        try:
            from jtop import jtop
            self.jtop = jtop()
            self.jtop.start()
            self.use_jtop = True
        except ImportError:
            # Fallback to parsing tegrastats
            warnings.warn("jtop not available, using tegrastats fallback")

    def get_stats(self) -> Dict[str, Any]:
        """Get GPU utilization and temperature"""
        if self.use_jtop:
            return self._get_stats_jtop()
        else:
            return self._get_stats_tegrastats()

    def get_memory_usage(self) -> Dict[str, float]:
        """Get GPU memory usage"""
        if self.use_jtop:
            return self._get_memory_jtop()
        else:
            return self._get_memory_tegrastats()

    def _get_stats_jtop(self) -> Dict[str, Any]:
        """Get stats using jtop"""
        try:
            stats = self.jtop.stats
            return {
                'gpu_utilization': stats.get('GPU', 0),
                'gpu_temp': stats.get('Temp GPU', None),
                'cpu_temp': stats.get('Temp CPU', None),
                'power_watts': stats.get('Power tot', None),
            }
        except:
            return {}

    def _get_memory_jtop(self) -> Dict[str, float]:
        """Get memory using jtop"""
        try:
            mem = self.jtop.memory
            return {
                'used_mb': mem['GPU']['used'] / 1024,
                'total_mb': mem['GPU']['total'] / 1024,
            }
        except:
            return {}

    def _get_stats_tegrastats(self) -> Dict[str, Any]:
        """Fallback: parse tegrastats output"""
        # This would parse /sys/devices/virtual/thermal/thermal_zone*/temp
        # and nvidia-smi equivalent for Jetson
        # Simplified implementation
        try:
            # Read temperature from thermal zones
            thermal_zones = Path('/sys/devices/virtual/thermal').glob('thermal_zone*')
            temps = []
            for zone in thermal_zones:
                temp_file = zone / 'temp'
                if temp_file.exists():
                    temp = int(temp_file.read_text().strip()) / 1000
                    temps.append(temp)

            return {
                'gpu_utilization': None,  # Not easily available without jtop
                'gpu_temp': max(temps) if temps else None,
                'cpu_temp': max(temps) if temps else None,
                'power_watts': None,
            }
        except:
            return {}

    def _get_memory_tegrastats(self) -> Dict[str, float]:
        """Fallback: estimate GPU memory from system"""
        # On Jetson, GPU shares memory with CPU
        vm = psutil.virtual_memory()
        return {
            'used_mb': 0,  # Not easily available
            'total_mb': vm.total / (1024 * 1024) / 2  # Rough estimate
        }

    def __del__(self):
        """Cleanup"""
        if self.use_jtop:
            try:
                self.jtop.close()
            except:
                pass
