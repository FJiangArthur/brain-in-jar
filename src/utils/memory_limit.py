import resource


def set_memory_limit(limit_gb: float) -> None:
    """Apply an OS-level memory limit to the current process.

    Parameters
    ----------
    limit_gb : float
        Desired memory limit in gigabytes.
    """
    limit_bytes = int(limit_gb * 1024 * 1024 * 1024)
    try:
        # Only lower the soft limit so it can be restored later without privileges
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        if hard == resource.RLIM_INFINITY or hard == -1:
            resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, hard))
        else:
            resource.setrlimit(resource.RLIMIT_AS, (min(limit_bytes, hard), hard))
    except (ValueError, resource.error):
        # Ignore if the platform does not support RLIMIT_AS or the limit is invalid
        pass
