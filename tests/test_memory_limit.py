import resource

from src.utils.memory_limit import set_memory_limit


def test_set_memory_limit():
    # Store original limits to restore later
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    try:
        set_memory_limit(0.2)  # around 200MB
        new_soft, _ = resource.getrlimit(resource.RLIMIT_AS)
        assert 199 * 1024 * 1024 <= new_soft <= 205 * 1024 * 1024
    finally:
        resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
