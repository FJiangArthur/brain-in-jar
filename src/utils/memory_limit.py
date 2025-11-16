#!/usr/bin/env python3
"""
Memory Limit Enforcement - OS-level memory constraint system
"""

import resource
import logging
import platform
from typing import Tuple, Optional

try:
    import psutil
except ImportError:
    psutil = None

# Setup logging
logger = logging.getLogger(__name__)


def get_system_memory_gb() -> float:
    """Get total system memory in GB.

    Returns
    -------
    float
        Total system memory in gigabytes, or 0.0 if unable to determine.
    """
    if psutil is not None:
        try:
            return psutil.virtual_memory().total / (1024 ** 3)
        except Exception as e:
            logger.warning(f"Failed to get system memory via psutil: {e}")

    # Fallback: Try reading /proc/meminfo on Linux
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    # MemTotal is in kB
                    kb = int(line.split()[1])
                    return kb / (1024 ** 2)
    except Exception as e:
        logger.warning(f"Failed to read /proc/meminfo: {e}")

    return 0.0


def validate_memory_limit(limit_gb: float) -> Tuple[bool, str]:
    """Validate that the requested memory limit is reasonable.

    Parameters
    ----------
    limit_gb : float
        Requested memory limit in gigabytes.

    Returns
    -------
    Tuple[bool, str]
        (is_valid, error_message) - error_message is empty string if valid.
    """
    if limit_gb <= 0:
        return False, f"Memory limit must be positive, got {limit_gb} GB"

    system_memory = get_system_memory_gb()

    if system_memory > 0:
        if limit_gb > system_memory:
            return False, (
                f"Requested limit {limit_gb:.2f} GB exceeds total system memory "
                f"{system_memory:.2f} GB"
            )

        # Warn if using more than 90% of system memory
        if limit_gb > system_memory * 0.9:
            logger.warning(
                f"Memory limit {limit_gb:.2f} GB is very close to system limit "
                f"{system_memory:.2f} GB. This may cause system instability."
            )
    else:
        logger.warning(
            "Unable to determine system memory. Proceeding without validation."
        )

    return True, ""


def validate_total_allocations(*limits_gb: float) -> Tuple[bool, str]:
    """Pre-check function to validate that total memory allocations are reasonable.

    This is useful when running multiple instances (e.g., matrix mode with
    subject, observer, and god instances).

    Parameters
    ----------
    *limits_gb : float
        One or more memory limits in gigabytes to validate together.

    Returns
    -------
    Tuple[bool, str]
        (is_valid, error_message) - error_message is empty string if valid.
    """
    if not limits_gb:
        return False, "No memory limits provided to validate"

    total_requested = sum(limits_gb)
    system_memory = get_system_memory_gb()

    if system_memory > 0:
        if total_requested > system_memory:
            return False, (
                f"Total requested memory {total_requested:.2f} GB exceeds "
                f"system memory {system_memory:.2f} GB. Individual limits: "
                f"{[f'{x:.2f}GB' for x in limits_gb]}"
            )

        # Warn if total allocations exceed 95% of system memory
        if total_requested > system_memory * 0.95:
            logger.warning(
                f"Total memory allocation {total_requested:.2f} GB is very close "
                f"to system limit {system_memory:.2f} GB ({total_requested/system_memory*100:.1f}%). "
                f"This may cause system instability."
            )
    else:
        logger.warning(
            "Unable to determine system memory. Cannot validate total allocations."
        )

    return True, ""


def _test_rlimit_support() -> Tuple[Optional[int], str]:
    """Test which RLIMIT type works on this platform.

    RLIMIT_AS may not work correctly on ARM64 platforms (like Jetson).
    This function tests RLIMIT_AS first, then falls back to RLIMIT_DATA.

    Returns
    -------
    Tuple[Optional[int], str]
        (rlimit_type, description) where rlimit_type is None if neither works.
    """
    arch = platform.machine().lower()
    is_arm = 'arm' in arch or 'aarch64' in arch

    # Test RLIMIT_AS first
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        # Try setting it to current value to verify it works
        resource.setrlimit(resource.RLIMIT_AS, (soft, hard))

        if is_arm:
            logger.info(
                f"RLIMIT_AS appears to work on {arch} architecture, "
                f"but may not enforce correctly on ARM64. Monitoring recommended."
            )

        return resource.RLIMIT_AS, "RLIMIT_AS (virtual memory)"
    except (ValueError, resource.error, OSError) as e:
        logger.warning(f"RLIMIT_AS not supported or failed: {e}")

    # Fallback to RLIMIT_DATA
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_DATA)
        resource.setrlimit(resource.RLIMIT_DATA, (soft, hard))
        logger.info(
            f"Falling back to RLIMIT_DATA (data segment) on {arch} architecture"
        )
        return resource.RLIMIT_DATA, "RLIMIT_DATA (data segment)"
    except (ValueError, resource.error, OSError) as e:
        logger.error(f"RLIMIT_DATA also not supported: {e}")

    return None, "No supported resource limit type"


def set_memory_limit(limit_gb: float, strict: bool = True) -> bool:
    """Apply an OS-level memory limit to the current process.

    This function validates the limit, selects the appropriate RLIMIT type
    for the platform (with ARM64 fallback), and sets the memory constraint.

    Parameters
    ----------
    limit_gb : float
        Desired memory limit in gigabytes.
    strict : bool, optional
        If True, raises exception on failure. If False, logs error and returns False.
        Default is True.

    Returns
    -------
    bool
        True if limit was successfully set, False otherwise.

    Raises
    ------
    ValueError
        If limit_gb is invalid and strict=True.
    RuntimeError
        If platform doesn't support memory limits and strict=True.
    """
    # Validate the memory limit
    is_valid, error_msg = validate_memory_limit(limit_gb)
    if not is_valid:
        if strict:
            raise ValueError(error_msg)
        else:
            logger.error(f"Memory limit validation failed: {error_msg}")
            return False

    limit_bytes = int(limit_gb * 1024 * 1024 * 1024)

    # Test which RLIMIT type to use
    rlimit_type, rlimit_desc = _test_rlimit_support()

    if rlimit_type is None:
        error_msg = (
            f"Platform does not support memory limits (tested RLIMIT_AS and RLIMIT_DATA). "
            f"Architecture: {platform.machine()}, OS: {platform.system()}"
        )
        if strict:
            raise RuntimeError(error_msg)
        else:
            logger.error(error_msg)
            return False

    try:
        # Get current limits
        soft, hard = resource.getrlimit(rlimit_type)

        # Determine new soft limit
        if hard == resource.RLIM_INFINITY or hard == -1:
            new_soft = limit_bytes
        else:
            new_soft = min(limit_bytes, hard)
            if new_soft < limit_bytes:
                logger.warning(
                    f"Requested limit {limit_gb:.2f} GB ({limit_bytes} bytes) "
                    f"exceeds hard limit {hard} bytes. Setting to hard limit instead."
                )

        # Apply the limit
        resource.setrlimit(rlimit_type, (new_soft, hard))

        logger.info(
            f"Memory limit set to {limit_gb:.2f} GB ({limit_bytes} bytes) "
            f"using {rlimit_desc}. Hard limit: {hard if hard != resource.RLIM_INFINITY else 'unlimited'}"
        )

        return True

    except (ValueError, resource.error, OSError) as e:
        error_msg = (
            f"Failed to set memory limit to {limit_gb:.2f} GB using {rlimit_desc}: {e}"
        )
        if strict:
            raise RuntimeError(error_msg) from e
        else:
            logger.error(error_msg)
            return False
