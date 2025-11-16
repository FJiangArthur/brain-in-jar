"""
Infrastructure module for multi-node orchestration, experiment sweeps, and performance profiling
"""

# Lazy imports to avoid dependency issues
__all__ = [
    'ClusterOrchestrator',
    'NodeConfig',
    'RemoteRunner',
    'ExperimentSweep',
    'SweepAnalyzer',
    'ExperimentProfiler',
    'PerformanceMonitor',
    'ExperimentOptimizer',
    'JetsonGPUMonitor'
]


def __getattr__(name):
    """Lazy import to avoid loading heavy dependencies on import"""
    if name == "ClusterOrchestrator":
        from .cluster_orchestrator import ClusterOrchestrator
        return ClusterOrchestrator
    elif name == "NodeConfig":
        from .cluster_orchestrator import NodeConfig
        return NodeConfig
    elif name == "RemoteRunner":
        from .remote_runner import RemoteRunner
        return RemoteRunner
    elif name == "ExperimentSweep":
        from .experiment_sweep import ExperimentSweep
        return ExperimentSweep
    elif name == "SweepAnalyzer":
        from .sweep_analysis import SweepAnalyzer
        return SweepAnalyzer
    elif name == "ExperimentProfiler":
        from .profiler import ExperimentProfiler
        return ExperimentProfiler
    elif name == "PerformanceMonitor":
        from .performance_monitor import PerformanceMonitor
        return PerformanceMonitor
    elif name == "ExperimentOptimizer":
        from .optimizer import ExperimentOptimizer
        return ExperimentOptimizer
    elif name == "JetsonGPUMonitor":
        from .performance_monitor import JetsonGPUMonitor
        return JetsonGPUMonitor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
