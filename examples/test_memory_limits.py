#!/usr/bin/env python3
"""
Example script demonstrating the enhanced memory limit validation.

This shows how to use the new validation functions before starting
multi-instance experiments (e.g., matrix mode).
"""

from src.utils.memory_limit import (
    get_system_memory_gb,
    validate_memory_limit,
    validate_total_allocations,
    set_memory_limit,
    _test_rlimit_support,
)


def main():
    print("=" * 70)
    print("Memory Limit Validation Example")
    print("=" * 70)

    # 1. Check system memory
    print("\n1. System Memory Detection")
    print("-" * 70)
    system_memory = get_system_memory_gb()
    if system_memory > 0:
        print(f"✓ Detected system memory: {system_memory:.2f} GB")
    else:
        print("⚠ Unable to detect system memory")

    # 2. Check RLIMIT support
    print("\n2. Resource Limit Support")
    print("-" * 70)
    rlimit_type, description = _test_rlimit_support()
    if rlimit_type is not None:
        print(f"✓ Using {description}")
    else:
        print("✗ No RLIMIT support detected on this platform")

    # 3. Validate individual limits
    print("\n3. Individual Limit Validation")
    print("-" * 70)
    test_limits = [2.0, 5.0, 10.0, system_memory + 10 if system_memory > 0 else 1000]

    for limit in test_limits:
        is_valid, msg = validate_memory_limit(limit)
        status = "✓" if is_valid else "✗"
        print(f"{status} {limit:.2f} GB: {msg if msg else 'Valid'}")

    # 4. Validate total allocations (matrix mode example)
    print("\n4. Total Allocations Validation (Matrix Mode Example)")
    print("-" * 70)

    # Example: Matrix mode with Subject (2GB), Observer (6GB), GOD (9GB)
    subject_limit = 2.0
    observer_limit = 6.0
    god_limit = 9.0

    is_valid, msg = validate_total_allocations(subject_limit, observer_limit, god_limit)
    total = subject_limit + observer_limit + god_limit

    if is_valid:
        print(f"✓ Matrix mode allocation is valid:")
        print(f"  - Subject:  {subject_limit:.2f} GB")
        print(f"  - Observer: {observer_limit:.2f} GB")
        print(f"  - GOD:      {god_limit:.2f} GB")
        print(f"  - Total:    {total:.2f} GB")
        if system_memory > 0:
            print(f"  - Available: {system_memory:.2f} GB ({total/system_memory*100:.1f}% utilization)")
    else:
        print(f"✗ Matrix mode allocation failed validation:")
        print(f"  {msg}")

    # 5. Actually set a memory limit (small value for safety)
    print("\n5. Setting Memory Limit (Example)")
    print("-" * 70)
    try:
        test_limit = 0.5  # 500 MB
        result = set_memory_limit(test_limit, strict=False)
        if result:
            print(f"✓ Successfully set memory limit to {test_limit} GB")
        else:
            print(f"⚠ Failed to set memory limit (non-strict mode)")
    except Exception as e:
        print(f"✗ Error setting memory limit: {e}")

    print("\n" + "=" * 70)
    print("Validation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
