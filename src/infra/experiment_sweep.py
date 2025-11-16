#!/usr/bin/env python3
"""
Automated Experiment Parameter Sweep System

Enables systematic exploration of parameter spaces for phenomenology research.
Supports Cartesian product sweeps, parallel execution, and resume capability.
"""

import json
import itertools
import multiprocessing
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import copy

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.schema import ExperimentConfig


@dataclass
class SweepConfig:
    """Configuration for a parameter sweep"""
    sweep_id: str
    base_config_path: str
    sweep_params: Dict[str, List[Any]]
    parallel_jobs: int = 1
    output_dir: str = "logs/sweeps"
    db_path: str = "logs/experiments.db"
    resume: bool = False
    jetson_optimized: bool = False
    max_retries: int = 2
    timeout_seconds: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class SweepResult:
    """Result from a single experiment in the sweep"""
    experiment_id: str
    parameters: Dict[str, Any]
    status: str  # 'completed', 'failed', 'timeout', 'crashed'
    start_time: datetime
    end_time: Optional[datetime] = None
    total_cycles: int = 0
    total_crashes: int = 0
    total_messages: int = 0
    error_message: Optional[str] = None
    db_path: str = ""


class ExperimentSweep:
    """
    Orchestrates automated parameter sweeps

    Features:
    - Cartesian product of parameter ranges
    - Sequential or parallel execution
    - Resume interrupted sweeps
    - Progress tracking
    - Results aggregation
    - Jetson Orin optimization (queue management, resource allocation)

    Example:
        sweep = ExperimentSweep(
            base_config="experiments/examples/unstable_memory.json",
            sweep_params={
                "corruption_rate": [0.1, 0.2, 0.3, 0.4, 0.5],
                "max_cycles": [15, 20]
            },
            parallel_jobs=3
        )
        results = sweep.run_all()
    """

    def __init__(
        self,
        base_config: str,
        sweep_params: Dict[str, List[Any]],
        sweep_id: Optional[str] = None,
        parallel_jobs: int = 1,
        output_dir: str = "logs/sweeps",
        db_path: str = "logs/experiments.db",
        resume: bool = False,
        jetson_optimized: bool = False,
        timeout_seconds: Optional[int] = None,
        max_retries: int = 2,
        tags: Optional[List[str]] = None,
        description: str = ""
    ):
        """
        Initialize sweep

        Args:
            base_config: Path to base experiment config JSON
            sweep_params: Dict of parameter_name -> [list of values]
            sweep_id: Unique sweep identifier (auto-generated if None)
            parallel_jobs: Number of experiments to run in parallel
            output_dir: Directory for sweep outputs
            db_path: Path to experiment database
            resume: Resume from previous incomplete sweep
            jetson_optimized: Enable Jetson Orin optimizations
            timeout_seconds: Timeout per experiment (None = no timeout)
            max_retries: Max retry attempts for failed experiments
            tags: Tags for this sweep
            description: Human-readable description
        """
        self.base_config_path = Path(base_config)
        self.sweep_params = sweep_params
        self.sweep_id = sweep_id or self._generate_sweep_id()
        self.parallel_jobs = parallel_jobs
        self.output_dir = Path(output_dir) / self.sweep_id
        self.db_path = db_path
        self.resume = resume
        self.jetson_optimized = jetson_optimized
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.tags = tags or []
        self.description = description

        # Validate base config exists
        if not self.base_config_path.exists():
            raise FileNotFoundError(f"Base config not found: {self.base_config_path}")

        # Load base config
        self.base_config = ExperimentConfig.from_json(str(self.base_config_path))

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate experiment grid
        self.experiment_grid = self._generate_experiment_grid()

        # Track results
        self.results: List[SweepResult] = []
        self.completed_experiments: set = set()

        # Load previous state if resuming
        if resume:
            self._load_sweep_state()

        print(f"[Sweep] Initialized sweep: {self.sweep_id}")
        print(f"[Sweep] Base config: {self.base_config_path}")
        print(f"[Sweep] Parameters to sweep: {list(sweep_params.keys())}")
        print(f"[Sweep] Total experiments: {len(self.experiment_grid)}")
        print(f"[Sweep] Parallel jobs: {parallel_jobs}")
        print(f"[Sweep] Output directory: {self.output_dir}")

    def _generate_sweep_id(self) -> str:
        """Generate unique sweep ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = self.base_config_path.stem
        return f"sweep_{base_name}_{timestamp}"

    def _generate_experiment_grid(self) -> List[Dict[str, Any]]:
        """
        Generate Cartesian product of all parameter combinations

        Returns:
            List of parameter dictionaries, one for each experiment
        """
        # Get parameter names and value lists
        param_names = list(self.sweep_params.keys())
        param_values = [self.sweep_params[name] for name in param_names]

        # Generate Cartesian product
        grid = []
        for combination in itertools.product(*param_values):
            param_dict = dict(zip(param_names, combination))
            grid.append(param_dict)

        return grid

    def _create_experiment_config(
        self,
        param_dict: Dict[str, Any],
        experiment_index: int
    ) -> Tuple[str, ExperimentConfig]:
        """
        Create experiment config from base config + parameter overrides

        Args:
            param_dict: Parameter values for this experiment
            experiment_index: Index in experiment grid

        Returns:
            Tuple of (experiment_id, ExperimentConfig)
        """
        # Deep copy base config
        config = copy.deepcopy(self.base_config)

        # Generate unique experiment ID
        param_str = "_".join([f"{k}={v}" for k, v in param_dict.items()])
        experiment_id = f"{self.sweep_id}_exp{experiment_index:04d}_{param_str}"
        experiment_id = experiment_id.replace(".", "p")  # Replace dots for filesystem safety

        config.experiment_id = experiment_id

        # Apply parameter overrides
        for param_name, param_value in param_dict.items():
            self._set_config_parameter(config, param_name, param_value)

        # Add sweep tags
        config.tags.extend([f"sweep:{self.sweep_id}", "automated_sweep"])
        config.tags.extend([f"{k}:{v}" for k, v in param_dict.items()])

        return experiment_id, config

    def _set_config_parameter(self, config: ExperimentConfig, param_path: str, value: Any):
        """
        Set a parameter in the config using dot notation

        Supports nested parameters like:
        - "max_cycles" -> config.max_cycles
        - "resource_constraints.ram_limit_gb" -> config.resource_constraints.ram_limit_gb
        - "interventions.0.parameters.corruption_rate" -> first intervention's corruption_rate

        Args:
            config: ExperimentConfig to modify
            param_path: Dot-separated path to parameter
            value: Value to set
        """
        parts = param_path.split(".")

        # Navigate to parent object
        obj = config
        for part in parts[:-1]:
            # Handle list indexing
            if part.isdigit():
                obj = obj[int(part)]
            else:
                obj = getattr(obj, part)

        # Set the final value
        final_part = parts[-1]
        if final_part.isdigit():
            obj[int(final_part)] = value
        elif isinstance(obj, dict):
            obj[final_part] = value
        else:
            setattr(obj, final_part, value)

    def run_all(self, verbose: bool = True) -> List[SweepResult]:
        """
        Run all experiments in the sweep

        Args:
            verbose: Print progress updates

        Returns:
            List of SweepResult objects
        """
        print(f"\n{'='*80}")
        print(f"STARTING SWEEP: {self.sweep_id}")
        print(f"{'='*80}\n")

        # Save sweep configuration
        self._save_sweep_config()

        # Determine experiments to run
        experiments_to_run = []
        for idx, param_dict in enumerate(self.experiment_grid):
            experiment_id, config = self._create_experiment_config(param_dict, idx)

            # Skip if already completed (for resume)
            if self.resume and experiment_id in self.completed_experiments:
                if verbose:
                    print(f"[Sweep] Skipping completed experiment: {experiment_id}")
                continue

            experiments_to_run.append((idx, experiment_id, config, param_dict))

        total_experiments = len(experiments_to_run)
        print(f"[Sweep] Running {total_experiments} experiments")

        if self.parallel_jobs > 1:
            # Parallel execution
            self._run_parallel(experiments_to_run, verbose)
        else:
            # Sequential execution
            self._run_sequential(experiments_to_run, verbose)

        # Save final results
        self._save_sweep_results()

        print(f"\n{'='*80}")
        print(f"SWEEP COMPLETE: {self.sweep_id}")
        print(f"{'='*80}\n")
        print(f"Total experiments: {len(self.results)}")
        print(f"Completed: {sum(1 for r in self.results if r.status == 'completed')}")
        print(f"Failed: {sum(1 for r in self.results if r.status == 'failed')}")
        print(f"Timeout: {sum(1 for r in self.results if r.status == 'timeout')}")
        print(f"\nResults saved to: {self.output_dir}")

        return self.results

    def _run_sequential(self, experiments: List[Tuple], verbose: bool = True):
        """Run experiments sequentially"""
        for i, (idx, experiment_id, config, param_dict) in enumerate(experiments):
            if verbose:
                print(f"\n[Sweep] Running experiment {i+1}/{len(experiments)}: {experiment_id}")
                print(f"[Sweep] Parameters: {param_dict}")

            result = self._run_single_experiment(experiment_id, config, param_dict)
            self.results.append(result)

            # Save intermediate results
            self._save_sweep_results()

            if verbose:
                print(f"[Sweep] Status: {result.status}")
                if result.status == 'completed':
                    print(f"[Sweep] Cycles: {result.total_cycles}, Crashes: {result.total_crashes}")

    def _run_parallel(self, experiments: List[Tuple], verbose: bool = True):
        """Run experiments in parallel"""
        if self.jetson_optimized:
            # Limit parallelism for Jetson Orin (4 seems optimal)
            max_workers = min(self.parallel_jobs, 4)
            print(f"[Sweep] Jetson optimization enabled: limiting to {max_workers} parallel jobs")
        else:
            max_workers = self.parallel_jobs

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_experiment = {
                executor.submit(
                    self._run_single_experiment_subprocess,
                    experiment_id,
                    config,
                    param_dict
                ): (idx, experiment_id, param_dict)
                for idx, experiment_id, config, param_dict in experiments
            }

            # Process completions
            completed_count = 0
            for future in as_completed(future_to_experiment):
                idx, experiment_id, param_dict = future_to_experiment[future]

                try:
                    result = future.result()
                    self.results.append(result)
                    completed_count += 1

                    if verbose:
                        print(f"\n[Sweep] Completed {completed_count}/{len(experiments)}: {experiment_id}")
                        print(f"[Sweep] Status: {result.status}")
                        if result.status == 'completed':
                            print(f"[Sweep] Cycles: {result.total_cycles}, Crashes: {result.total_crashes}")

                    # Save intermediate results
                    self._save_sweep_results()

                except Exception as e:
                    print(f"[Sweep] Error running {experiment_id}: {e}")
                    self.results.append(SweepResult(
                        experiment_id=experiment_id,
                        parameters=param_dict,
                        status='failed',
                        start_time=datetime.now(),
                        error_message=str(e),
                        db_path=self.db_path
                    ))

    def _run_single_experiment(
        self,
        experiment_id: str,
        config: ExperimentConfig,
        param_dict: Dict[str, Any]
    ) -> SweepResult:
        """
        Run a single experiment (in-process)

        Args:
            experiment_id: Unique experiment ID
            config: Experiment configuration
            param_dict: Parameters for this experiment

        Returns:
            SweepResult
        """
        # Save config to file
        config_path = self.output_dir / f"{experiment_id}_config.json"
        config.to_json(str(config_path))

        # Run experiment via subprocess
        start_time = datetime.now()

        try:
            cmd = [
                sys.executable,
                "-m", "src.runner.experiment_runner",
                "--config", str(config_path),
                "--db", self.db_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=str(Path(__file__).parent.parent.parent)
            )

            end_time = datetime.now()

            # Get experiment summary from database
            from src.db.experiment_database import ExperimentDatabase
            db = ExperimentDatabase(self.db_path)
            summary = db.get_experiment_summary(experiment_id)

            if result.returncode == 0:
                status = 'completed'
                error_message = None
            else:
                status = 'failed'
                error_message = result.stderr

            return SweepResult(
                experiment_id=experiment_id,
                parameters=param_dict,
                status=status,
                start_time=start_time,
                end_time=end_time,
                total_cycles=summary.get('total_cycles', 0),
                total_crashes=summary.get('total_crashes', 0),
                total_messages=summary.get('total_messages', 0),
                error_message=error_message,
                db_path=self.db_path
            )

        except subprocess.TimeoutExpired:
            return SweepResult(
                experiment_id=experiment_id,
                parameters=param_dict,
                status='timeout',
                start_time=start_time,
                end_time=datetime.now(),
                error_message=f"Timeout after {self.timeout_seconds}s",
                db_path=self.db_path
            )
        except Exception as e:
            return SweepResult(
                experiment_id=experiment_id,
                parameters=param_dict,
                status='failed',
                start_time=start_time,
                end_time=datetime.now(),
                error_message=str(e),
                db_path=self.db_path
            )

    def _run_single_experiment_subprocess(
        self,
        experiment_id: str,
        config: ExperimentConfig,
        param_dict: Dict[str, Any]
    ) -> SweepResult:
        """Wrapper for subprocess execution (pickleable)"""
        return self._run_single_experiment(experiment_id, config, param_dict)

    def _save_sweep_config(self):
        """Save sweep configuration to file"""
        config_data = {
            'sweep_id': self.sweep_id,
            'base_config_path': str(self.base_config_path),
            'sweep_params': self.sweep_params,
            'parallel_jobs': self.parallel_jobs,
            'total_experiments': len(self.experiment_grid),
            'created_at': datetime.now().isoformat(),
            'jetson_optimized': self.jetson_optimized,
            'timeout_seconds': self.timeout_seconds,
            'tags': self.tags,
            'description': self.description
        }

        config_path = self.output_dir / "sweep_config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)

    def _save_sweep_results(self):
        """Save sweep results to file"""
        results_data = {
            'sweep_id': self.sweep_id,
            'timestamp': datetime.now().isoformat(),
            'total_experiments': len(self.experiment_grid),
            'completed_experiments': len(self.results),
            'results': [
                {
                    'experiment_id': r.experiment_id,
                    'parameters': r.parameters,
                    'status': r.status,
                    'start_time': r.start_time.isoformat(),
                    'end_time': r.end_time.isoformat() if r.end_time else None,
                    'total_cycles': r.total_cycles,
                    'total_crashes': r.total_crashes,
                    'total_messages': r.total_messages,
                    'error_message': r.error_message
                }
                for r in self.results
            ]
        }

        results_path = self.output_dir / "sweep_results.json"
        with open(results_path, 'w') as f:
            json.dump(results_data, f, indent=2)

        # Also save completed experiment IDs for resume
        self.completed_experiments = {r.experiment_id for r in self.results if r.status == 'completed'}
        completed_path = self.output_dir / "completed_experiments.json"
        with open(completed_path, 'w') as f:
            json.dump(list(self.completed_experiments), f, indent=2)

    def _load_sweep_state(self):
        """Load previous sweep state for resume"""
        completed_path = self.output_dir / "completed_experiments.json"
        if completed_path.exists():
            with open(completed_path, 'r') as f:
                self.completed_experiments = set(json.load(f))
            print(f"[Sweep] Resuming sweep: {len(self.completed_experiments)} experiments already completed")

        results_path = self.output_dir / "sweep_results.json"
        if results_path.exists():
            with open(results_path, 'r') as f:
                results_data = json.load(f)

            # Reconstruct results
            for r_data in results_data['results']:
                self.results.append(SweepResult(
                    experiment_id=r_data['experiment_id'],
                    parameters=r_data['parameters'],
                    status=r_data['status'],
                    start_time=datetime.fromisoformat(r_data['start_time']),
                    end_time=datetime.fromisoformat(r_data['end_time']) if r_data['end_time'] else None,
                    total_cycles=r_data['total_cycles'],
                    total_crashes=r_data['total_crashes'],
                    total_messages=r_data['total_messages'],
                    error_message=r_data.get('error_message'),
                    db_path=self.db_path
                ))

    def estimate_time_remaining(self, avg_experiment_duration: float) -> float:
        """
        Estimate time remaining for sweep completion

        Args:
            avg_experiment_duration: Average duration per experiment (seconds)

        Returns:
            Estimated remaining time in seconds
        """
        completed = len(self.results)
        remaining = len(self.experiment_grid) - completed

        if self.parallel_jobs > 1:
            # Account for parallelism
            remaining_time = (remaining / self.parallel_jobs) * avg_experiment_duration
        else:
            remaining_time = remaining * avg_experiment_duration

        return remaining_time


def estimate_jetson_parallel_capacity(ram_per_experiment_gb: float = 2.0) -> int:
    """
    Estimate optimal parallel job count for Jetson Orin AGX

    Jetson Orin AGX specs:
    - 64GB RAM
    - 12-core ARM CPU
    - Ampere GPU with 2048 CUDA cores

    Args:
        ram_per_experiment_gb: RAM requirement per experiment

    Returns:
        Recommended parallel job count
    """
    # Conservative estimates
    total_ram_gb = 64
    available_ram_gb = total_ram_gb * 0.7  # Reserve 30% for system
    cpu_cores = 12

    # Calculate limits
    ram_limited_jobs = int(available_ram_gb / ram_per_experiment_gb)
    cpu_limited_jobs = cpu_cores // 2  # 2 cores per experiment

    # Take minimum, but cap at 4 for stability
    recommended_jobs = min(ram_limited_jobs, cpu_limited_jobs, 4)

    print(f"[Jetson] Total RAM: {total_ram_gb}GB")
    print(f"[Jetson] Available RAM: {available_ram_gb}GB")
    print(f"[Jetson] RAM allows: {ram_limited_jobs} parallel jobs")
    print(f"[Jetson] CPU allows: {cpu_limited_jobs} parallel jobs")
    print(f"[Jetson] Recommended: {recommended_jobs} parallel jobs")

    return recommended_jobs


if __name__ == "__main__":
    # Example usage
    print("Example sweep usage:")
    print()
    print("sweep = ExperimentSweep(")
    print("    base_config='experiments/examples/unstable_memory.json',")
    print("    sweep_params={")
    print("        'corruption_rate': [0.1, 0.2, 0.3, 0.4, 0.5],")
    print("        'max_cycles': [15, 20]")
    print("    },")
    print("    parallel_jobs=3")
    print(")")
    print("results = sweep.run_all()")
