"""
Analysis Tools for Brain in Jar Season 3

Provides export, reporting, statistical analysis, metrics calculation,
and comprehensive visualization tools for experiment data.
"""

from .export import ExperimentExporter
from .report_generator import AutomaticReportGenerator

# Import other modules if they exist (created by other agents)
try:
    from .statistics import ExperimentStatistics
except ImportError:
    ExperimentStatistics = None

try:
    from .metrics import MetricsCalculator
except ImportError:
    MetricsCalculator = None

try:
    from .visualizations import (
        TimelinePlot,
        BeliefEvolutionPlot,
        MemoryCorruptionPlot,
        MultiExperimentComparison
    )
except ImportError:
    TimelinePlot = None
    BeliefEvolutionPlot = None
    MemoryCorruptionPlot = None
    MultiExperimentComparison = None

try:
    from .network_graphs import (
        CommunicationNetwork,
        BeliefAlignmentNetwork,
        InfluenceGraph
    )
except ImportError:
    CommunicationNetwork = None
    BeliefAlignmentNetwork = None
    InfluenceGraph = None

__all__ = [
    'ExperimentExporter',
    'AutomaticReportGenerator',
    'ExperimentStatistics',
    'MetricsCalculator',
    'TimelinePlot',
    'BeliefEvolutionPlot',
    'MemoryCorruptionPlot',
    'MultiExperimentComparison',
    'CommunicationNetwork',
    'BeliefAlignmentNetwork',
    'InfluenceGraph'
]
