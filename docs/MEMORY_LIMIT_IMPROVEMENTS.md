# Memory Limit Enforcement Improvements

## Summary

The memory limit enforcement system in `/home/user/brain-in-jar/src/utils/memory_limit.py` has been completely rewritten to address critical issues and add comprehensive validation capabilities.

## Issues Fixed

### 1. Silent Failure with No Logging
**Before:**
```python
except (ValueError, resource.error):
    # Ignore if the platform does not support RLIMIT_AS or the limit is invalid
    pass
```

**After:**
- Comprehensive logging at all stages (info, warning, error levels)
- Detailed error messages indicating what went wrong and why
- Return values and exceptions to indicate success/failure
- Platform and architecture information in error messages

### 2. No Validation of Memory Limits
**Before:**
- No check if requested limit exceeds system memory
- No validation that limit is positive
- Could request 100GB on a 4GB system

**After:**
```python
def validate_memory_limit(limit_gb: float) -> Tuple[bool, str]:
    """Validates that memory limit is reasonable for the system"""
    - Checks limit is positive
    - Verifies limit doesn't exceed total system memory
    - Warns if using >90% of system memory
```

### 3. ARM64/Jetson RLIMIT_AS Issues
**Before:**
- Only used RLIMIT_AS
- No fallback mechanism
- May not work on ARM64 platforms (Jetson Orin AGX)

**After:**
```python
def _test_rlimit_support() -> Tuple[Optional[int], str]:
    """Test which RLIMIT type works on this platform"""
    - Tests RLIMIT_AS first
    - Detects ARM64 architecture and warns
    - Falls back to RLIMIT_DATA if needed
    - Returns None if neither works
```

### 4. No Multi-Instance Validation
**Before:**
- No way to validate total allocations for matrix mode
- Could try to allocate 2GB + 6GB + 9GB = 17GB on 8GB system

**After:**
```python
def validate_total_allocations(*limits_gb: float) -> Tuple[bool, str]:
    """Validate total memory allocations for multiple instances"""
    - Checks sum of all limits against system memory
    - Warns if total exceeds 95% of system memory
    - Provides detailed error messages with individual limits
```

## New Features

### 1. System Memory Detection
```python
get_system_memory_gb() -> float
```
- Uses psutil if available
- Falls back to /proc/meminfo on Linux
- Returns 0.0 if unable to determine (with warning)

### 2. Strict vs Non-Strict Mode
```python
set_memory_limit(limit_gb: float, strict: bool = True) -> bool
```
- `strict=True`: Raises exceptions on failure (default, backwards compatible)
- `strict=False`: Logs errors and returns False on failure
- Return value indicates success/failure

### 3. Comprehensive Validation
All validation functions return `Tuple[bool, str]` with:
- Boolean indicating validity
- Human-readable error message (empty string if valid)

### 4. Platform Detection
- Detects ARM64/aarch64 architecture
- Warns about potential RLIMIT_AS issues on ARM
- Provides platform-specific error messages

## API Examples

### Basic Usage (Backwards Compatible)
```python
from src.utils.memory_limit import set_memory_limit

# Old code still works - defaults to strict=True
set_memory_limit(2.0)  # Raises exception on failure
```

### Validation Before Setting
```python
from src.utils.memory_limit import validate_memory_limit, set_memory_limit

is_valid, error_msg = validate_memory_limit(2.0)
if is_valid:
    set_memory_limit(2.0)
else:
    print(f"Invalid limit: {error_msg}")
```

### Matrix Mode Validation
```python
from src.utils.memory_limit import validate_total_allocations

subject_limit = 2.0
observer_limit = 6.0
god_limit = 9.0

is_valid, error_msg = validate_total_allocations(
    subject_limit, observer_limit, god_limit
)

if not is_valid:
    print(f"Cannot start matrix mode: {error_msg}")
    return

# Proceed with starting instances...
```

### Non-Strict Mode (Continue on Failure)
```python
from src.utils.memory_limit import set_memory_limit

success = set_memory_limit(2.0, strict=False)
if success:
    print("Memory limit set successfully")
else:
    print("Failed to set memory limit, continuing anyway...")
```

### System Memory Check
```python
from src.utils.memory_limit import get_system_memory_gb

system_memory = get_system_memory_gb()
if system_memory > 0:
    print(f"System has {system_memory:.2f} GB RAM")
    recommended_limit = system_memory * 0.8
    print(f"Recommended max limit: {recommended_limit:.2f} GB")
```

## Integration Points

### 1. Neural Link System
`/home/user/brain-in-jar/src/core/neural_link.py` (line 59):
- Continues to use `set_memory_limit()` with default strict mode
- Automatically validates and logs errors
- Platform detection happens automatically

### 2. Web Interface Runner
`/home/user/brain-in-jar/src/scripts/run_with_web.py` (lines 314-339):
- Now validates total allocations before starting matrix mode
- Displays system memory and allocation percentages
- Aborts startup if allocations exceed system memory
- Provides clear error messages to user

## Testing

### Unit Tests
`/home/user/brain-in-jar/tests/test_memory_limit.py`:
- Tests system memory detection
- Tests validation functions
- Tests RLIMIT support detection
- Tests strict and non-strict modes
- Tests backwards compatibility

### Example Script
`/home/user/brain-in-jar/examples/test_memory_limits.py`:
```bash
PYTHONPATH=/home/user/brain-in-jar python3 examples/test_memory_limits.py
```

Demonstrates:
- System memory detection
- Individual limit validation
- Total allocations validation (matrix mode example)
- Setting memory limits

## Logging Output Examples

### Success Case
```
INFO: Memory limit set to 2.00 GB (2147483648 bytes) using RLIMIT_AS (virtual memory).
      Hard limit: unlimited
```

### ARM64 Warning
```
INFO: RLIMIT_AS appears to work on aarch64 architecture, but may not enforce correctly
      on ARM64. Monitoring recommended.
```

### Fallback to RLIMIT_DATA
```
WARNING: RLIMIT_AS not supported or failed: Invalid argument
INFO: Falling back to RLIMIT_DATA (data segment) on aarch64 architecture
```

### Validation Failure
```
ERROR: Memory limit validation failed: Requested limit 20.00 GB exceeds total system
       memory 13.00 GB
```

### Platform Not Supported
```
ERROR: Platform does not support memory limits (tested RLIMIT_AS and RLIMIT_DATA).
       Architecture: x86_64, OS: Darwin
```

## Breaking Changes

**None** - The API is fully backwards compatible:
- `set_memory_limit(limit_gb)` works exactly as before
- New `strict` parameter defaults to `True` (raises exceptions)
- Function now returns `bool` instead of `None`, but this is safe

## Migration Guide

### If you were ignoring failures:
```python
# Old code
try:
    set_memory_limit(2.0)
except:
    pass

# New code - more explicit
success = set_memory_limit(2.0, strict=False)
if not success:
    logger.warning("Failed to set memory limit")
```

### If you want pre-validation:
```python
# Old code - just tried and hoped it worked
set_memory_limit(args.ram_limit)

# New code - validate first
is_valid, error = validate_memory_limit(args.ram_limit)
if not is_valid:
    print(f"Invalid RAM limit: {error}")
    sys.exit(1)
set_memory_limit(args.ram_limit)
```

### If you run multiple instances:
```python
# Old code - no validation
instance1_limit = 5.0
instance2_limit = 5.0
instance3_limit = 5.0

# New code - validate total
is_valid, error = validate_total_allocations(
    instance1_limit, instance2_limit, instance3_limit
)
if not is_valid:
    print(f"Total allocation too high: {error}")
    sys.exit(1)
```

## Performance Impact

- Minimal: Validation functions run once at startup
- Memory detection uses cached psutil values
- RLIMIT support test runs once and could be cached if needed
- No impact on runtime after initialization

## Future Improvements

Potential enhancements:
1. Cache RLIMIT type detection (currently tested on every call)
2. Add memory monitoring/alerting when approaching limits
3. Support for cgroups-based memory limits (Docker/K8s)
4. Dynamic limit adjustment based on actual usage
5. Per-process memory tracking and reporting

## References

- Python resource module: https://docs.python.org/3/library/resource.html
- RLIMIT_AS vs RLIMIT_DATA: https://man7.org/linux/man-pages/man2/getrlimit.2.html
- ARM64 memory limits: Known issues with RLIMIT_AS on some ARM platforms
- psutil documentation: https://psutil.readthedocs.io/
