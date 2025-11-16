#!/usr/bin/env python3
"""
Test script for memory budget validation
Demonstrates the memory pre-check system
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.memory_budget import (
    MemoryBudgetManager,
    validate_memory_budget,
    check_available_memory_before_load
)
import psutil


def print_system_info():
    """Print current system memory information"""
    mem = psutil.virtual_memory()
    print("\n" + "="*70)
    print("SYSTEM MEMORY INFORMATION")
    print("="*70)
    print(f"Total RAM:     {mem.total / (1024**3):.2f} GB")
    print(f"Available RAM: {mem.available / (1024**3):.2f} GB")
    print(f"Used RAM:      {mem.used / (1024**3):.2f} GB")
    print(f"Usage:         {mem.percent:.1f}%")
    print("="*70 + "\n")


def test_memory_budget_manager():
    """Test the MemoryBudgetManager class"""
    print("\n" + "="*70)
    print("TEST 1: MemoryBudgetManager")
    print("="*70)

    # Initialize manager
    manager = MemoryBudgetManager(safety_margin_percent=15.0)

    # Try to find a model file for testing
    model_path = "models/Qwen2.5-1.5B-Instruct-Q4_0.gguf"
    if not Path(model_path).exists():
        # Try alternative paths
        possible_paths = [
            "models/gemma-3-12b-it-Q4_K_M.gguf",
            "models/meta-llama-3.1-8b-q4_0.gguf",
            "models/mistral-7b-instruct-v0.2.Q2_K.gguf"
        ]
        for path in possible_paths:
            if Path(path).exists():
                model_path = path
                break

    if not Path(model_path).exists():
        print(f"\nWARNING: No model file found for testing.")
        print("Creating a dummy model for demonstration purposes...")
        # Create a small dummy file for testing
        Path("models").mkdir(exist_ok=True)
        model_path = "models/test_model.gguf"
        with open(model_path, "wb") as f:
            # Write 2GB dummy file
            f.write(b'\0' * (2 * 1024 * 1024 * 1024))

    print(f"\nUsing model: {model_path}")

    # Test allocation for a single instance
    print("\nTest: Allocating 8GB for instance 'TEST_1'")
    success, msg = manager.allocate("TEST_1", 8.0, model_path)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Message:\n{msg}")

    # Test allocation for another instance
    print("\nTest: Allocating 10GB for instance 'TEST_2'")
    success, msg = manager.allocate("TEST_2", 10.0, model_path)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Message:\n{msg}")

    # Print allocation report
    print(manager.get_allocation_report())

    # Deallocate instances
    print("\nDeallocating TEST_1...")
    manager.deallocate("TEST_1")

    print("\nDeallocating TEST_2...")
    manager.deallocate("TEST_2")

    print("\nFinal allocation report:")
    print(manager.get_allocation_report())


def test_validate_memory_budget():
    """Test the validate_memory_budget function"""
    print("\n" + "="*70)
    print("TEST 2: validate_memory_budget()")
    print("="*70)

    # Find a model
    model_path = "models/Qwen2.5-1.5B-Instruct-Q4_0.gguf"
    if not Path(model_path).exists():
        possible_paths = [
            "models/gemma-3-12b-it-Q4_K_M.gguf",
            "models/meta-llama-3.1-8b-q4_0.gguf",
            "models/mistral-7b-instruct-v0.2.Q2_K.gguf",
            "models/test_model.gguf"
        ]
        for path in possible_paths:
            if Path(path).exists():
                model_path = path
                break

    if not Path(model_path).exists():
        print(f"\nERROR: No model file found. Skipping test.")
        return

    # Test single mode
    print("\nTest: Single instance mode with 8GB limit")
    ram_limits = {'subject': 8.0, 'observer': 10.0, 'god': 12.0}
    is_valid, report = validate_memory_budget('single', ram_limits, model_path)
    print(f"\nValidation result: {'PASSED' if is_valid else 'FAILED'}")

    # Test matrix mode
    print("\n" + "-"*70)
    print("\nTest: Matrix mode (3 instances)")
    ram_limits = {'subject': 8.0, 'observer': 10.0, 'god': 12.0}
    is_valid, report = validate_memory_budget('matrix', ram_limits, model_path)
    print(f"\nValidation result: {'PASSED' if is_valid else 'FAILED'}")

    # Test with excessive limits (should fail)
    print("\n" + "-"*70)
    print("\nTest: Excessive limits (should fail)")
    total_ram = psutil.virtual_memory().total / (1024**3)
    excessive_limit = total_ram * 0.4  # Each instance wants 40% of total RAM
    ram_limits = {
        'subject': excessive_limit,
        'observer': excessive_limit,
        'god': excessive_limit
    }
    is_valid, report = validate_memory_budget('matrix', ram_limits, model_path)
    print(f"\nValidation result: {'PASSED' if is_valid else 'FAILED'}")


def test_pre_flight_check():
    """Test the pre-flight memory check"""
    print("\n" + "="*70)
    print("TEST 3: check_available_memory_before_load()")
    print("="*70)

    # Find a model
    model_path = "models/Qwen2.5-1.5B-Instruct-Q4_0.gguf"
    if not Path(model_path).exists():
        possible_paths = [
            "models/gemma-3-12b-it-Q4_K_M.gguf",
            "models/meta-llama-3.1-8b-q4_0.gguf",
            "models/mistral-7b-instruct-v0.2.Q2_K.gguf",
            "models/test_model.gguf"
        ]
        for path in possible_paths:
            if Path(path).exists():
                model_path = path
                break

    if not Path(model_path).exists():
        print(f"\nERROR: No model file found. Skipping test.")
        return

    # Test with reasonable limit
    print(f"\nTest: Pre-flight check for {model_path} with 8GB limit")
    can_load, msg = check_available_memory_before_load(model_path, 8.0)
    print(f"Result: {'CAN LOAD' if can_load else 'CANNOT LOAD'}")
    print(f"Message: {msg}")

    # Test with excessive limit
    print("\n" + "-"*70)
    total_ram = psutil.virtual_memory().total / (1024**3)
    excessive_limit = total_ram * 2  # Want 2x total RAM (should fail)
    print(f"\nTest: Pre-flight check with excessive limit ({excessive_limit:.2f}GB)")
    can_load, msg = check_available_memory_before_load(model_path, excessive_limit)
    print(f"Result: {'CAN LOAD' if can_load else 'CANNOT LOAD'}")
    print(f"Message: {msg}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MEMORY VALIDATION SYSTEM TEST SUITE")
    print("="*70)

    print_system_info()

    try:
        test_memory_budget_manager()
    except Exception as e:
        print(f"\nERROR in test_memory_budget_manager: {e}")

    try:
        test_validate_memory_budget()
    except Exception as e:
        print(f"\nERROR in test_validate_memory_budget: {e}")

    try:
        test_pre_flight_check()
    except Exception as e:
        print(f"\nERROR in test_pre_flight_check: {e}")

    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
