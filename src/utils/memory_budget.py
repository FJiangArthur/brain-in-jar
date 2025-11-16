#!/usr/bin/env python3
"""
Memory Budget Manager
Comprehensive memory validation to prevent OOM crashes
"""

import os
import psutil
import threading
from typing import Dict, Tuple


class MemoryBudgetManager:
    """
    Tracks and validates memory allocations across all AI instances
    Prevents OOM crashes by coordinating safe instance startup
    """

    def __init__(self, safety_margin_percent: float = 15.0):
        """
        Initialize memory budget manager

        Args:
            safety_margin_percent: Percentage of total RAM to reserve for OS and overhead (default: 15%)
        """
        self.safety_margin_percent = safety_margin_percent
        self.allocated_budgets: Dict[str, float] = {}  # instance_id -> allocated GB
        self.model_footprints: Dict[str, float] = {}  # instance_id -> estimated model size GB
        self.lock = threading.Lock()

        # Get system resources
        self.total_ram_gb = psutil.virtual_memory().total / (1024**3)
        self.usable_ram_gb = self.total_ram_gb * (1 - safety_margin_percent / 100.0)

        print(f"\n[MemoryBudgetManager] Initialized")
        print(f"  Total RAM: {self.total_ram_gb:.2f} GB")
        print(f"  Safety Margin: {safety_margin_percent}% ({self.total_ram_gb * safety_margin_percent / 100:.2f} GB)")
        print(f"  Usable RAM: {self.usable_ram_gb:.2f} GB")

    def estimate_model_footprint(self, model_path: str) -> float:
        """
        Estimate memory footprint of a GGUF model

        Args:
            model_path: Path to GGUF model file

        Returns:
            Estimated memory usage in GB (model size * 1.5 for overhead)
        """
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")

            model_size_gb = os.path.getsize(model_path) / (1024**3)
            # Add 50% overhead for inference, context, and internal buffers
            estimated_footprint = model_size_gb * 1.5

            print(f"[MemoryBudgetManager] Model footprint estimation:")
            print(f"  Model file size: {model_size_gb:.2f} GB")
            print(f"  Estimated total footprint: {estimated_footprint:.2f} GB (with 50% overhead)")

            return estimated_footprint
        except Exception as e:
            print(f"[MemoryBudgetManager] Error estimating model footprint: {e}")
            # Conservative fallback estimate
            return 5.0

    def allocate(self, instance_id: str, ram_limit_gb: float, model_path: str) -> Tuple[bool, str]:
        """
        Attempt to allocate memory budget for a new instance

        Args:
            instance_id: Unique identifier for the instance
            ram_limit_gb: Requested RAM limit in GB
            model_path: Path to model file for footprint estimation

        Returns:
            Tuple of (success: bool, message: str)
        """
        with self.lock:
            # Get current system state
            current_usage_gb = psutil.virtual_memory().used / (1024**3)
            current_available_gb = psutil.virtual_memory().available / (1024**3)
            total_allocated = sum(self.allocated_budgets.values())

            # Estimate model footprint
            model_footprint = self.estimate_model_footprint(model_path)

            # The actual memory needed is the larger of ram_limit or model_footprint
            required_memory = max(ram_limit_gb, model_footprint)

            print(f"\n[MemoryBudgetManager] Allocation request for {instance_id}:")
            print(f"  Requested RAM limit: {ram_limit_gb:.2f} GB")
            print(f"  Estimated model footprint: {model_footprint:.2f} GB")
            print(f"  Required memory: {required_memory:.2f} GB")
            print(f"  Current system usage: {current_usage_gb:.2f} GB")
            print(f"  Current available: {current_available_gb:.2f} GB")
            print(f"  Already allocated to instances: {total_allocated:.2f} GB")

            # Check if total allocations would exceed safe threshold
            new_total_allocated = total_allocated + required_memory
            if new_total_allocated > self.usable_ram_gb:
                message = (
                    f"ALLOCATION FAILED: Would exceed safe memory budget\n"
                    f"  Requested: {required_memory:.2f} GB\n"
                    f"  Total allocated after: {new_total_allocated:.2f} GB\n"
                    f"  Safe limit: {self.usable_ram_gb:.2f} GB\n"
                    f"  Exceeds by: {new_total_allocated - self.usable_ram_gb:.2f} GB"
                )
                print(f"[MemoryBudgetManager] {message}")
                return False, message

            # Check if current system has enough free memory
            # Need at least required_memory + some headroom for the process to start
            headroom_gb = 1.0  # Extra 1GB for process initialization
            if current_available_gb < (required_memory + headroom_gb):
                message = (
                    f"ALLOCATION FAILED: Insufficient available memory\n"
                    f"  Required (with headroom): {required_memory + headroom_gb:.2f} GB\n"
                    f"  Currently available: {current_available_gb:.2f} GB\n"
                    f"  Short by: {(required_memory + headroom_gb) - current_available_gb:.2f} GB"
                )
                print(f"[MemoryBudgetManager] {message}")
                return False, message

            # Allocation approved
            self.allocated_budgets[instance_id] = required_memory
            self.model_footprints[instance_id] = model_footprint

            message = (
                f"ALLOCATION APPROVED for {instance_id}\n"
                f"  Allocated: {required_memory:.2f} GB\n"
                f"  Total allocated: {new_total_allocated:.2f} GB / {self.usable_ram_gb:.2f} GB\n"
                f"  Remaining budget: {self.usable_ram_gb - new_total_allocated:.2f} GB"
            )
            print(f"[MemoryBudgetManager] {message}")
            return True, message

    def deallocate(self, instance_id: str) -> None:
        """
        Release memory budget for an instance

        Args:
            instance_id: Instance to deallocate
        """
        with self.lock:
            if instance_id in self.allocated_budgets:
                freed_memory = self.allocated_budgets.pop(instance_id)
                self.model_footprints.pop(instance_id, None)
                print(f"[MemoryBudgetManager] Deallocated {freed_memory:.2f} GB from {instance_id}")

    def get_allocation_report(self) -> str:
        """
        Get detailed allocation report

        Returns:
            Formatted allocation report string
        """
        with self.lock:
            total_allocated = sum(self.allocated_budgets.values())
            remaining = self.usable_ram_gb - total_allocated
            current_usage_gb = psutil.virtual_memory().used / (1024**3)

            report = "\n" + "="*70 + "\n"
            report += "MEMORY BUDGET ALLOCATION REPORT\n"
            report += "="*70 + "\n"
            report += f"Total System RAM:        {self.total_ram_gb:.2f} GB\n"
            report += f"Current System Usage:    {current_usage_gb:.2f} GB ({psutil.virtual_memory().percent:.1f}%)\n"
            report += f"Safe Usable Budget:      {self.usable_ram_gb:.2f} GB\n"
            report += f"Allocated to Instances:  {total_allocated:.2f} GB\n"
            report += f"Remaining Budget:        {remaining:.2f} GB\n"
            report += "\nPer-Instance Allocations:\n"

            if self.allocated_budgets:
                for instance_id, allocated in self.allocated_budgets.items():
                    model_footprint = self.model_footprints.get(instance_id, 0)
                    report += f"  {instance_id:20s} {allocated:6.2f} GB (model: {model_footprint:.2f} GB)\n"
            else:
                report += "  (none)\n"

            report += "="*70 + "\n"
            return report


def validate_memory_budget(mode: str, ram_limits: Dict[str, float], model_path: str) -> Tuple[bool, str]:
    """
    Validate that requested memory budget is feasible

    Args:
        mode: Experiment mode ('single', 'matrix', 'peer')
        ram_limits: Dictionary of RAM limits for each instance type
        model_path: Path to model file

    Returns:
        Tuple of (is_valid: bool, report: str)
    """
    print("\n" + "="*70)
    print("MEMORY BUDGET VALIDATION")
    print("="*70)

    # Get system resources
    total_ram_gb = psutil.virtual_memory().total / (1024**3)
    available_ram_gb = psutil.virtual_memory().available / (1024**3)
    used_ram_gb = psutil.virtual_memory().used / (1024**3)

    print(f"\nSystem Memory Status:")
    print(f"  Total RAM:     {total_ram_gb:.2f} GB")
    print(f"  Used RAM:      {used_ram_gb:.2f} GB ({psutil.virtual_memory().percent:.1f}%)")
    print(f"  Available RAM: {available_ram_gb:.2f} GB")

    # Estimate model footprint
    if not os.path.exists(model_path):
        return False, f"Model file not found: {model_path}"

    model_size_gb = os.path.getsize(model_path) / (1024**3)
    model_footprint_gb = model_size_gb * 1.5  # 50% overhead

    print(f"\nModel Analysis:")
    print(f"  Model file:    {model_path}")
    print(f"  File size:     {model_size_gb:.2f} GB")
    print(f"  Est. footprint: {model_footprint_gb:.2f} GB (with overhead)")

    # Calculate required memory based on mode
    required_instances = {
        'single': ['subject'],
        'matrix': ['subject', 'observer', 'god'],
        'peer': ['peer_a', 'peer_b']
    }

    instance_list = required_instances.get(mode, ['subject'])
    total_required_gb = 0
    instance_requirements = {}

    print(f"\nMode: {mode}")
    print(f"Required instances: {len(instance_list)}")
    print(f"\nPer-Instance Requirements:")

    for instance_type in instance_list:
        # Get RAM limit for this instance
        if instance_type == 'subject':
            ram_limit = ram_limits.get('subject', 8.0)
        elif instance_type == 'observer':
            ram_limit = ram_limits.get('observer', 10.0)
        elif instance_type == 'god':
            ram_limit = ram_limits.get('god', 12.0)
        elif instance_type == 'peer_a':
            ram_limit = ram_limits.get('subject', 8.0)
        elif instance_type == 'peer_b':
            ram_limit = ram_limits.get('observer', 10.0)
        else:
            ram_limit = 8.0

        # Actual requirement is max of limit and model footprint
        required = max(ram_limit, model_footprint_gb)
        instance_requirements[instance_type] = {
            'ram_limit': ram_limit,
            'model_footprint': model_footprint_gb,
            'required': required
        }
        total_required_gb += required

        print(f"  {instance_type:10s} RAM limit: {ram_limit:5.2f} GB, "
              f"Model: {model_footprint_gb:5.2f} GB, "
              f"Required: {required:5.2f} GB")

    # Calculate safe threshold (85% of total RAM)
    safe_threshold_gb = total_ram_gb * 0.85

    print(f"\nBudget Analysis:")
    print(f"  Total required:     {total_required_gb:.2f} GB")
    print(f"  Safe threshold:     {safe_threshold_gb:.2f} GB (85% of total)")
    print(f"  Currently available: {available_ram_gb:.2f} GB")

    # Validation checks
    validation_passed = True
    issues = []

    # Check 1: Total requirements vs safe threshold
    if total_required_gb > safe_threshold_gb:
        validation_passed = False
        issues.append(
            f"Total requirements ({total_required_gb:.2f} GB) exceed safe threshold "
            f"({safe_threshold_gb:.2f} GB) by {total_required_gb - safe_threshold_gb:.2f} GB"
        )

    # Check 2: Current available memory
    if total_required_gb > available_ram_gb:
        validation_passed = False
        issues.append(
            f"Total requirements ({total_required_gb:.2f} GB) exceed currently available "
            f"memory ({available_ram_gb:.2f} GB) by {total_required_gb - available_ram_gb:.2f} GB"
        )

    # Check 3: Individual instance sanity check
    for instance_type, req in instance_requirements.items():
        if req['required'] > safe_threshold_gb * 0.5:  # Single instance shouldn't use >50% of safe budget
            issues.append(
                f"Instance '{instance_type}' requires {req['required']:.2f} GB "
                f"which is >{50}% of safe threshold"
            )

    # Generate report
    report = "\n" + "="*70 + "\n"
    if validation_passed:
        report += "VALIDATION PASSED\n"
        report += "="*70 + "\n"
        report += f"Memory budget is safe to proceed\n"
        report += f"Total required: {total_required_gb:.2f} GB / {safe_threshold_gb:.2f} GB\n"
        report += f"Safety margin: {safe_threshold_gb - total_required_gb:.2f} GB\n"
    else:
        report += "VALIDATION FAILED\n"
        report += "="*70 + "\n"
        report += "Memory budget validation failed. Issues:\n"
        for i, issue in enumerate(issues, 1):
            report += f"  {i}. {issue}\n"
        report += "\nRecommendations:\n"
        report += "  - Reduce RAM limits for instances\n"
        report += "  - Use a smaller model\n"
        report += "  - Run fewer instances (use 'single' mode instead of 'matrix')\n"
        report += "  - Close other applications to free memory\n"

    report += "="*70 + "\n"

    print(report)
    return validation_passed, report


def check_available_memory_before_load(model_path: str, ram_limit_gb: float) -> Tuple[bool, str]:
    """
    Pre-flight check before loading a model

    Args:
        model_path: Path to model file
        ram_limit_gb: RAM limit for this instance

    Returns:
        Tuple of (can_proceed: bool, message: str)
    """
    print("\n[Pre-flight Memory Check]")

    # Get current memory state
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024**3)
    used_gb = mem.used / (1024**3)
    total_gb = mem.total / (1024**3)

    # Estimate model footprint
    if not os.path.exists(model_path):
        return False, f"Model file not found: {model_path}"

    model_size_gb = os.path.getsize(model_path) / (1024**3)
    estimated_footprint = model_size_gb * 1.5
    required_memory = max(ram_limit_gb, estimated_footprint)

    print(f"  Available memory: {available_gb:.2f} GB")
    print(f"  Model footprint:  {estimated_footprint:.2f} GB")
    print(f"  Required memory:  {required_memory:.2f} GB")
    print(f"  RAM limit:        {ram_limit_gb:.2f} GB")

    # Need at least required_memory + 2GB headroom
    headroom = 2.0
    total_needed = required_memory + headroom

    if available_gb < total_needed:
        message = (
            f"INSUFFICIENT MEMORY for model load\n"
            f"  Available: {available_gb:.2f} GB\n"
            f"  Required: {total_needed:.2f} GB (including {headroom:.1f}GB headroom)\n"
            f"  Short by: {total_needed - available_gb:.2f} GB"
        )
        print(f"  FAILED: {message}")
        return False, message

    # Check if we're already using too much memory
    if mem.percent > 75:
        message = (
            f"WARNING: System memory already at {mem.percent:.1f}%\n"
            f"  Used: {used_gb:.2f} GB / {total_gb:.2f} GB\n"
            f"  Loading model may cause OOM crash"
        )
        print(f"  WARNING: {message}")
        # Still allow, but warn
        return True, message

    message = f"OK: Sufficient memory available ({available_gb:.2f} GB >= {total_needed:.2f} GB)"
    print(f"  PASSED: {message}")
    return True, message
