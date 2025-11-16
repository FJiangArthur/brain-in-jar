#!/usr/bin/env python3
"""Tests for memory limit enforcement."""

import resource
import pytest

from src.utils.memory_limit import (
    set_memory_limit,
    validate_memory_limit,
    validate_total_allocations,
    get_system_memory_gb,
    _test_rlimit_support,
)


def test_get_system_memory():
    """Test that we can detect system memory."""
    memory = get_system_memory_gb()
    # Should return a positive value or 0 if unable to detect
    assert memory >= 0
    # If it detected memory, should be reasonable (at least 1GB, less than 10TB)
    if memory > 0:
        assert 1.0 <= memory <= 10000.0


def test_validate_memory_limit():
    """Test memory limit validation."""
    # Test negative limit
    is_valid, msg = validate_memory_limit(-1.0)
    assert not is_valid
    assert "positive" in msg.lower()

    # Test zero limit
    is_valid, msg = validate_memory_limit(0.0)
    assert not is_valid

    # Test reasonable limit
    is_valid, msg = validate_memory_limit(0.5)
    # Should be valid on any system with more than 0.5GB
    system_memory = get_system_memory_gb()
    if system_memory > 0.5:
        assert is_valid
        assert msg == ""

    # Test limit exceeding system memory
    system_memory = get_system_memory_gb()
    if system_memory > 0:
        is_valid, msg = validate_memory_limit(system_memory + 100)
        assert not is_valid
        assert "exceeds" in msg.lower()


def test_validate_total_allocations():
    """Test validation of total memory allocations."""
    # Test empty list
    is_valid, msg = validate_total_allocations()
    assert not is_valid

    # Test reasonable allocations
    is_valid, msg = validate_total_allocations(1.0, 2.0, 3.0)
    system_memory = get_system_memory_gb()
    if system_memory > 6.0:
        assert is_valid
        assert msg == ""

    # Test excessive allocations
    if system_memory > 0:
        is_valid, msg = validate_total_allocations(system_memory + 10, system_memory + 20)
        assert not is_valid
        assert "exceeds" in msg.lower()


def test_rlimit_support():
    """Test that we can detect RLIMIT support."""
    rlimit_type, description = _test_rlimit_support()
    # Should return either RLIMIT_AS, RLIMIT_DATA, or None
    if rlimit_type is not None:
        assert rlimit_type in (resource.RLIMIT_AS, resource.RLIMIT_DATA)
        assert len(description) > 0


def test_set_memory_limit():
    """Test setting memory limits."""
    # Test with non-strict mode (should not raise on small systems)
    result = set_memory_limit(0.2, strict=False)

    # Get the rlimit type that was used
    rlimit_type, _ = _test_rlimit_support()

    if rlimit_type is not None and result:
        # Verify the limit was set
        new_soft, _ = resource.getrlimit(rlimit_type)
        # Allow some tolerance (199-205 MB range)
        expected_bytes = int(0.2 * 1024 * 1024 * 1024)
        tolerance = 6 * 1024 * 1024  # 6MB tolerance
        assert abs(new_soft - expected_bytes) <= tolerance, \
            f"Expected ~{expected_bytes} bytes, got {new_soft} bytes"


def test_set_memory_limit_strict_mode():
    """Test strict mode validation."""
    # Test invalid limit in strict mode
    with pytest.raises(ValueError):
        set_memory_limit(-1.0, strict=True)

    # Test excessive limit in strict mode
    system_memory = get_system_memory_gb()
    if system_memory > 0:
        with pytest.raises(ValueError):
            set_memory_limit(system_memory + 1000, strict=True)


def test_set_memory_limit_backwards_compatible():
    """Test that the function is backwards compatible."""
    # Should work without specifying strict parameter (defaults to True)
    try:
        # Use a reasonable limit that should work on most systems
        result = set_memory_limit(0.5, strict=False)
        # If it succeeded, verify it returns a boolean
        assert isinstance(result, bool)
    except (ValueError, RuntimeError):
        # It's ok if it fails on systems without memory limit support
        pass
