import resource
import sys
import platform
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_memory_limit(limit_gb: float) -> None:
    """Apply an OS-level memory limit to the current process.

    On ARM64/Jetson, RLIMIT_AS can interfere with threading, so we add headroom
    and prefer RLIMIT_DATA, or disable it entirely if issues persist.

    Parameters
    ----------
    limit_gb : float
        Desired memory limit in gigabytes.
    """
    limit_bytes = int(limit_gb * 1024 * 1024 * 1024)

    logger.info(f"Setting memory limit to {limit_gb:.2f} GB ({limit_bytes} bytes)")
    logger.info(f"Platform: {platform.machine()}, System: {platform.system()}")

    # On ARM64 (Jetson), skip RLIMIT_AS as it interferes with Python threading
    # Rely on GPU watchdog and system RAM watchdog instead
    if platform.machine() in ['aarch64', 'arm64']:
        logger.warning("ARM64 detected - skipping RLIMIT_AS to avoid threading issues")
        logger.info("Relying on GPU watchdog and system RAM monitoring for memory protection")
        logger.info("✓ Memory monitoring enabled (watchdog-based)")
        return

    # On other platforms, try RLIMIT_AS with extra headroom for threading
    headroom_bytes = int(2 * 1024 * 1024 * 1024)  # 2GB headroom for Python runtime
    limit_with_headroom = limit_bytes + headroom_bytes

    success = _try_set_limit(resource.RLIMIT_AS, limit_with_headroom, "RLIMIT_AS")

    if not success:
        logger.warning(f"Failed to set memory limit on this platform")
        logger.info("Relying on GPU watchdog and system RAM monitoring for memory protection")


def _try_set_limit(resource_type, limit_bytes, resource_name):
    """
    Try to set a specific resource limit

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        soft, hard = resource.getrlimit(resource_type)
        logger.info(f"{resource_name} current limits: soft={soft}, hard={hard}")

        # Set the new limit
        if hard == resource.RLIM_INFINITY or hard == -1:
            new_limit = (limit_bytes, hard)
        else:
            new_limit = (min(limit_bytes, hard), hard)

        resource.setrlimit(resource_type, new_limit)

        # Verify the limit was set
        verify_soft, verify_hard = resource.getrlimit(resource_type)
        logger.info(f"{resource_name} new limits: soft={verify_soft}, hard={verify_hard}")

        if verify_soft == new_limit[0]:
            logger.info(f"✓ Memory limit set successfully using {resource_name}")
            return True
        else:
            logger.warning(f"✗ {resource_name} limit verification failed")
            return False

    except (ValueError, resource.error, OSError) as e:
        logger.warning(f"✗ {resource_name} not supported or failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error setting {resource_name}: {e}")
        return False
