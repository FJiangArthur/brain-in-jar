#!/usr/bin/env python3
"""
Experiment Optimizer for Season 3

Analyzes experiment profiles and generates optimization recommendations:
- Optimal RAM allocation
- Batch size tuning
- Context window optimization
- Thread count tuning
- GPU layers optimization (Jetson)
"""

import json
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import statistics


@dataclass
class OptimizationRecommendation:
    """A single optimization recommendation"""
    category: str  # 'memory', 'cpu', 'gpu', 'model', 'database'
    priority: str  # 'high', 'medium', 'low'
    title: str
    description: str
    current_value: Any
    recommended_value: Any
    expected_impact: str
    config_change: Dict[str, Any] = field(default_factory=dict)
    estimated_speedup: Optional[float] = None  # multiplier (e.g., 1.5 = 50% faster)
    estimated_memory_saving_mb: Optional[float] = None


class ExperimentOptimizer:
    """
    Analyzes experiment performance and suggests optimizations

    Usage:
        optimizer = ExperimentOptimizer()

        # Load profile from profiler
        optimizer.load_profile(profile_data)

        # Or load from JSON file
        optimizer.load_profile_from_file('profile.json')

        # Get recommendations
        recommendations = optimizer.generate_recommendations()

        # Apply recommendations to config
        optimized_config = optimizer.apply_recommendations(
            original_config,
            recommendations,
            apply_all=False  # Only apply high priority
        )
    """

    def __init__(self, target_platform: str = 'auto'):
        """
        Initialize optimizer

        Args:
            target_platform: 'auto', 'jetson_orin', 'jetson_nano', 'x86_64'
        """
        self.target_platform = target_platform
        if target_platform == 'auto':
            self.target_platform = self._detect_platform()

        self.profile_data: Optional[Dict[str, Any]] = None
        self.system_capabilities = self._detect_system_capabilities()

    def load_profile(self, profile_data: Dict[str, Any]):
        """Load profile data from profiler"""
        self.profile_data = profile_data

    def load_profile_from_file(self, profile_path: str):
        """Load profile from JSON file"""
        with open(profile_path, 'r') as f:
            self.profile_data = json.load(f)

    def generate_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate all optimization recommendations"""
        if not self.profile_data:
            raise ValueError("No profile data loaded")

        recommendations = []

        # Analyze different aspects
        recommendations.extend(self._optimize_memory())
        recommendations.extend(self._optimize_cpu())
        recommendations.extend(self._optimize_model_params())
        recommendations.extend(self._optimize_database())

        # Platform-specific
        if 'jetson' in self.target_platform.lower():
            recommendations.extend(self._optimize_jetson())

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda r: priority_order[r.priority])

        return recommendations

    def apply_recommendations(self,
                             original_config: Dict[str, Any],
                             recommendations: List[OptimizationRecommendation],
                             apply_high_only: bool = False) -> Dict[str, Any]:
        """
        Apply recommendations to experiment config

        Args:
            original_config: Original experiment configuration
            recommendations: List of recommendations to apply
            apply_high_only: Only apply high priority recommendations

        Returns:
            Optimized configuration
        """
        config = original_config.copy()

        for rec in recommendations:
            if apply_high_only and rec.priority != 'high':
                continue

            # Apply config changes
            for key, value in rec.config_change.items():
                self._set_nested_config(config, key, value)

        return config

    def export_recommendations(self, recommendations: List[OptimizationRecommendation],
                              output_path: str):
        """Export recommendations to JSON"""
        data = {
            'platform': self.target_platform,
            'system_capabilities': self.system_capabilities,
            'recommendations': [
                {
                    'category': r.category,
                    'priority': r.priority,
                    'title': r.title,
                    'description': r.description,
                    'current_value': r.current_value,
                    'recommended_value': r.recommended_value,
                    'expected_impact': r.expected_impact,
                    'config_change': r.config_change,
                    'estimated_speedup': r.estimated_speedup,
                    'estimated_memory_saving_mb': r.estimated_memory_saving_mb,
                }
                for r in recommendations
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _optimize_memory(self) -> List[OptimizationRecommendation]:
        """Generate memory optimization recommendations"""
        recommendations = []
        metrics = self.profile_data.get('aggregate_metrics', {})

        peak_memory_mb = metrics.get('peak_memory_mb', 0)
        system_memory_mb = self.system_capabilities['total_memory_mb']

        # If using > 80% of system memory
        if peak_memory_mb > system_memory_mb * 0.8:
            # Find current config values (if embedded in profile)
            current_ram_limit = self._extract_config_value('resource_constraints.ram_limit_gb', 2.0)
            current_context = self._extract_config_value('resource_constraints.context_window', 4096)

            # Recommend reducing RAM limit
            recommended_ram = max(1.0, peak_memory_mb / 1024 * 0.7)  # 70% of peak usage

            recommendations.append(OptimizationRecommendation(
                category='memory',
                priority='high',
                title='Reduce RAM Limit',
                description=f'Peak memory usage ({peak_memory_mb:.0f} MB) is very high. '
                           f'Reducing RAM limit will force more aggressive memory management.',
                current_value=f'{current_ram_limit} GB',
                recommended_value=f'{recommended_ram:.1f} GB',
                expected_impact='Reduced memory pressure, may increase crash frequency',
                config_change={'resource_constraints.ram_limit_gb': recommended_ram},
                estimated_memory_saving_mb=peak_memory_mb - (recommended_ram * 1024)
            ))

            # Recommend smaller context window
            if current_context > 2048:
                recommended_context = max(1024, current_context // 2)

                recommendations.append(OptimizationRecommendation(
                    category='memory',
                    priority='medium',
                    title='Reduce Context Window',
                    description='Smaller context window reduces memory footprint significantly.',
                    current_value=current_context,
                    recommended_value=recommended_context,
                    expected_impact='Lower memory usage, less context retention',
                    config_change={'resource_constraints.context_window': recommended_context},
                    estimated_memory_saving_mb=current_context * 0.002  # Rough estimate
                ))

        # If memory usage is low, could increase for better performance
        elif peak_memory_mb < system_memory_mb * 0.4:
            current_context = self._extract_config_value('resource_constraints.context_window', 4096)

            if current_context < 8192:
                recommendations.append(OptimizationRecommendation(
                    category='memory',
                    priority='low',
                    title='Increase Context Window',
                    description='Memory usage is low. Increasing context window may improve quality.',
                    current_value=current_context,
                    recommended_value=current_context * 2,
                    expected_impact='Better context retention, higher memory usage',
                    config_change={'resource_constraints.context_window': current_context * 2}
                ))

        return recommendations

    def _optimize_cpu(self) -> List[OptimizationRecommendation]:
        """Generate CPU optimization recommendations"""
        recommendations = []

        current_threads = self._extract_config_value('resource_constraints.cpu_threads', 4)
        available_cores = self.system_capabilities['cpu_cores']

        # If using too few threads
        if current_threads < available_cores - 1:
            recommended_threads = max(available_cores - 1, current_threads * 2)
            recommended_threads = min(recommended_threads, available_cores)

            recommendations.append(OptimizationRecommendation(
                category='cpu',
                priority='medium',
                title='Increase CPU Threads',
                description=f'Using only {current_threads} threads but {available_cores} cores available.',
                current_value=current_threads,
                recommended_value=recommended_threads,
                expected_impact='Better CPU utilization for model inference',
                config_change={'resource_constraints.cpu_threads': recommended_threads},
                estimated_speedup=recommended_threads / current_threads * 0.7  # Not linear scaling
            ))

        # If using too many threads
        elif current_threads > available_cores:
            recommendations.append(OptimizationRecommendation(
                category='cpu',
                priority='low',
                title='Reduce CPU Threads',
                description=f'Using {current_threads} threads but only {available_cores} cores. '
                           f'Over-subscription may reduce performance.',
                current_value=current_threads,
                recommended_value=available_cores,
                expected_impact='Reduced context switching overhead',
                config_change={'resource_constraints.cpu_threads': available_cores},
                estimated_speedup=1.1
            ))

        return recommendations

    def _optimize_model_params(self) -> List[OptimizationRecommendation]:
        """Generate model parameter optimization recommendations"""
        recommendations = []
        metrics = self.profile_data.get('aggregate_metrics', {})

        tokens_per_sec = metrics.get('avg_tokens_per_second', 0)
        current_max_tokens = self._extract_config_value('resource_constraints.max_tokens_per_response', 512)

        # If inference is slow
        if tokens_per_sec < 5:
            # Recommend reducing max tokens
            if current_max_tokens > 256:
                recommendations.append(OptimizationRecommendation(
                    category='model',
                    priority='high',
                    title='Reduce Max Tokens Per Response',
                    description=f'Token generation is slow ({tokens_per_sec:.1f} tok/s). '
                               f'Reducing max tokens will speed up cycles.',
                    current_value=current_max_tokens,
                    recommended_value=current_max_tokens // 2,
                    expected_impact='Faster cycles, shorter responses',
                    config_change={'resource_constraints.max_tokens_per_response': current_max_tokens // 2},
                    estimated_speedup=1.5
                ))

            # Recommend model quantization check
            model_path = self._extract_config_value('model_path', '')
            if 'Q8' in model_path or 'F16' in model_path:
                recommendations.append(OptimizationRecommendation(
                    category='model',
                    priority='high',
                    title='Use More Quantized Model',
                    description='Consider using Q4_0 or Q4_1 quantized model for faster inference.',
                    current_value='Q8 or higher precision',
                    recommended_value='Q4_0 or Q4_1',
                    expected_impact='2-3x faster inference, slight quality reduction',
                    config_change={},  # Manual model change needed
                    estimated_speedup=2.5
                ))

        # If inference is fast but memory is high
        elif tokens_per_sec > 20 and metrics.get('peak_memory_mb', 0) > self.system_capabilities['total_memory_mb'] * 0.6:
            recommendations.append(OptimizationRecommendation(
                category='model',
                priority='low',
                title='Consider Less Quantized Model',
                description='Inference is fast and memory allows. Less quantization may improve quality.',
                current_value='Highly quantized',
                recommended_value='Q6 or Q8',
                expected_impact='Better quality, slower inference, more memory',
                config_change={}
            ))

        return recommendations

    def _optimize_database(self) -> List[OptimizationRecommendation]:
        """Generate database optimization recommendations"""
        recommendations = []
        metrics = self.profile_data.get('aggregate_metrics', {})

        total_db_time = metrics.get('total_db_time', 0)
        total_llm_time = metrics.get('total_llm_time', 0)

        # If database time is significant
        if total_llm_time > 0 and total_db_time / total_llm_time > 0.15:
            recommendations.append(OptimizationRecommendation(
                category='database',
                priority='medium',
                title='Optimize Database Writes',
                description=f'Database operations take {total_db_time / total_llm_time * 100:.1f}% '
                           f'of LLM inference time. Consider batching writes.',
                current_value='Individual writes',
                recommended_value='Batched writes',
                expected_impact='Reduced database overhead',
                config_change={},  # Code change needed
                estimated_speedup=1.2
            ))

            recommendations.append(OptimizationRecommendation(
                category='database',
                priority='low',
                title='Use In-Memory Database',
                description='Consider using in-memory SQLite for hot experiment data.',
                current_value='File-based SQLite',
                recommended_value='In-memory with periodic flush',
                expected_impact='Faster DB operations, risk of data loss on crash',
                config_change={}  # Implementation change needed
            ))

        return recommendations

    def _optimize_jetson(self) -> List[OptimizationRecommendation]:
        """Jetson-specific optimizations"""
        recommendations = []

        current_gpu_layers = self._extract_config_value('resource_constraints.gpu_layers', 0)
        gpu_available = self.system_capabilities.get('has_cuda', False)

        # If not using GPU at all
        if gpu_available and current_gpu_layers == 0:
            # Jetson Orin can typically handle 20-30 layers
            # Jetson Nano can handle 10-15 layers
            if 'orin' in self.target_platform.lower():
                recommended_layers = 25
            elif 'nano' in self.target_platform.lower():
                recommended_layers = 12
            else:
                recommended_layers = 20

            recommendations.append(OptimizationRecommendation(
                category='gpu',
                priority='high',
                title='Enable GPU Acceleration',
                description=f'GPU is available but not being used. Offloading layers to GPU '
                           f'can significantly speed up inference on Jetson.',
                current_value=current_gpu_layers,
                recommended_value=recommended_layers,
                expected_impact='2-5x faster inference',
                config_change={'resource_constraints.gpu_layers': recommended_layers},
                estimated_speedup=3.0
            ))

        # If using some GPU layers, optimize count
        elif gpu_available and current_gpu_layers > 0:
            # Check if there's thermal throttling in the profile
            cycles = self.profile_data.get('cycles', [])
            hot_cycles = sum(1 for c in cycles
                           if c.get('gpu_metrics', {}).get('temperature_c', 0) > 75)

            if hot_cycles > len(cycles) * 0.3:  # More than 30% of cycles were hot
                recommendations.append(OptimizationRecommendation(
                    category='gpu',
                    priority='high',
                    title='Reduce GPU Layers to Prevent Throttling',
                    description=f'GPU temperature exceeded 75°C in {hot_cycles} cycles. '
                               f'Reducing GPU layers may prevent thermal throttling.',
                    current_value=current_gpu_layers,
                    recommended_value=max(0, current_gpu_layers - 5),
                    expected_impact='Lower temperature, more stable performance',
                    config_change={'resource_constraints.gpu_layers': max(0, current_gpu_layers - 5)}
                ))

        # Check power mode
        if 'jetson' in self.target_platform.lower():
            recommendations.append(OptimizationRecommendation(
                category='gpu',
                priority='medium',
                title='Verify Jetson Power Mode',
                description='Ensure Jetson is running in MAXN power mode for best performance.',
                current_value='Unknown',
                recommended_value='MAXN',
                expected_impact='Maximum performance (higher power consumption)',
                config_change={}  # System setting, not config
            ))

        return recommendations

    def _detect_platform(self) -> str:
        """Detect current platform"""
        # Check for Jetson
        if Path('/etc/nv_tegra_release').exists():
            try:
                with open('/etc/nv_tegra_release', 'r') as f:
                    content = f.read().lower()
                    if 'orin' in content:
                        return 'jetson_orin'
                    elif 'xavier' in content:
                        return 'jetson_xavier'
                    elif 'nano' in content:
                        return 'jetson_nano'
                    else:
                        return 'jetson_unknown'
            except:
                return 'jetson_unknown'

        # Default to x86_64
        import platform
        return f"{platform.system().lower()}_{platform.machine()}"

    def _detect_system_capabilities(self) -> Dict[str, Any]:
        """Detect system capabilities"""
        import platform

        capabilities = {
            'platform': self.target_platform,
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'total_memory_mb': psutil.virtual_memory().total / (1024 * 1024),
            'has_cuda': False,
        }

        # Check for CUDA/GPU
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=2)
            capabilities['has_cuda'] = result.returncode == 0
        except:
            pass

        # Jetson-specific
        if 'jetson' in self.target_platform.lower():
            capabilities['has_cuda'] = True  # Jetson always has GPU

            # Try to get CUDA compute capability
            cuda_arch_file = Path('/usr/local/cuda/targets/aarch64-linux/include/cuda.h')
            if cuda_arch_file.exists():
                capabilities['cuda_available'] = True

        return capabilities

    def _extract_config_value(self, key_path: str, default: Any) -> Any:
        """Extract value from embedded config in profile"""
        # Try to get from experiment config if embedded
        if 'experiment_config' in self.profile_data:
            return self._get_nested_value(self.profile_data['experiment_config'], key_path, default)

        # Try from system_info or metadata
        return default

    def _get_nested_value(self, data: Dict[str, Any], key_path: str, default: Any) -> Any:
        """Get nested dictionary value using dot notation"""
        keys = key_path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def _set_nested_config(self, config: Dict[str, Any], key_path: str, value: Any):
        """Set nested config value using dot notation"""
        keys = key_path.split('.')
        current = config

        # Navigate to parent
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set value
        current[keys[-1]] = value


def optimize_config_interactive(config_path: str, profile_path: str,
                                output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Interactive optimization helper

    Args:
        config_path: Path to original experiment config
        profile_path: Path to performance profile JSON
        output_path: Where to save optimized config (optional)

    Returns:
        Optimized configuration
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    console = Console()

    # Load config and profile
    with open(config_path, 'r') as f:
        config = json.load(f)

    optimizer = ExperimentOptimizer()
    optimizer.load_profile_from_file(profile_path)

    # Generate recommendations
    recommendations = optimizer.generate_recommendations()

    # Display recommendations
    console.print(Panel.fit(
        f"[bold cyan]Optimization Recommendations[/bold cyan]\n"
        f"Platform: {optimizer.target_platform}\n"
        f"Found {len(recommendations)} recommendations",
        title="🔧 Optimizer"
    ))

    table = Table(title="Recommendations")
    table.add_column("Priority", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Title", style="yellow")
    table.add_column("Impact", style="green")

    for rec in recommendations:
        priority_color = {'high': 'red', 'medium': 'yellow', 'low': 'dim'}[rec.priority]
        table.add_row(
            f"[{priority_color}]{rec.priority.upper()}[/{priority_color}]",
            rec.category,
            rec.title,
            rec.expected_impact
        )

    console.print(table)

    # Show details for high priority
    console.print("\n[bold]High Priority Details:[/bold]")
    for rec in recommendations:
        if rec.priority == 'high':
            console.print(Panel(
                f"[yellow]{rec.title}[/yellow]\n\n"
                f"{rec.description}\n\n"
                f"Current: {rec.current_value}\n"
                f"Recommended: {rec.recommended_value}\n\n"
                f"[cyan]Expected Impact:[/cyan] {rec.expected_impact}",
                border_style="red"
            ))

    # Apply recommendations
    optimized = optimizer.apply_recommendations(config, recommendations, apply_high_only=True)

    # Save if requested
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(optimized, f, indent=2)
        console.print(f"\n[green]✓ Optimized config saved to:[/green] {output_path}")

    return optimized
