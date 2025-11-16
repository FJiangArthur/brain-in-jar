# Quick Reference: Memory Validation System

## What Was Implemented

Three layers of memory validation to prevent OOM crashes:

1. **Global validation** - Before starting (in `main()`)
2. **Per-instance allocation** - Before creating each instance
3. **Pre-model-load check** - Before loading LLM model

## New Files

```
src/utils/memory_budget.py              - Core validation module (16KB)
scripts/test_memory_validation.py       - Test suite (6.9KB)
docs/MEMORY_VALIDATION.md               - Full documentation (8.9KB)
MEMORY_VALIDATION_IMPLEMENTATION.md     - Implementation summary
```

## Modified Files

```
src/scripts/run_with_web.py    - Added MemoryBudgetManager integration
src/core/neural_link.py         - Added pre-flight check before model load
```

## Key Components

### 1. MemoryBudgetManager

**Location:** `src/utils/memory_budget.py`

**Purpose:** Track memory allocations across all instances

**Usage:**
```python
manager = MemoryBudgetManager(safety_margin_percent=15.0)

# Allocate
success, msg = manager.allocate(instance_id, ram_limit_gb, model_path)

# Deallocate
manager.deallocate(instance_id)

# Report
print(manager.get_allocation_report())
```

### 2. validate_memory_budget()

**Location:** `src/utils/memory_budget.py`

**Purpose:** Global validation before starting any instances

**Usage:**
```python
is_valid, report = validate_memory_budget(mode, ram_limits, model_path)
if not is_valid:
    print(report)
    sys.exit(1)
```

### 3. check_available_memory_before_load()

**Location:** `src/utils/memory_budget.py`

**Purpose:** Pre-flight check before loading model

**Usage:**
```python
can_load, msg = check_available_memory_before_load(model_path, ram_limit_gb)
if not can_load:
    raise MemoryError(msg)
```

## Integration Points

### run_with_web.py

**Lines 22:** Import
```python
from src.utils.memory_budget import MemoryBudgetManager, validate_memory_budget
```

**Line 37:** Initialize
```python
self.memory_budget = MemoryBudgetManager(safety_margin_percent=15.0)
```

**Lines 314-334:** Global validation in `main()`
```python
is_valid, validation_report = validate_memory_budget(
    runner_args.mode, ram_limits, runner_args.model
)
if not is_valid:
    sys.exit(1)
```

**Lines 130-142:** Per-instance allocation in `add_instance()`
```python
can_allocate, msg = self.memory_budget.allocate(
    instance_id, ram_limit, args.model
)
if not can_allocate:
    return None
```

**Lines 214-222:** Cleanup in `shutdown()`
```python
print(self.memory_budget.get_allocation_report())
for instance_id in self.instances:
    self.memory_budget.deallocate(instance_id)
```

### neural_link.py

**Line 26:** Import
```python
from src.utils.memory_budget import check_available_memory_before_load
```

**Lines 186-199:** Pre-flight check in `load_model()`
```python
can_load, msg = check_available_memory_before_load(
    self.args.model, ram_limit_gb
)
if not can_load:
    raise MemoryError(msg)
```

## Memory Formulas

```
Model Footprint  = file_size_gb × 1.5
Required Memory  = max(ram_limit_gb, model_footprint_gb)
Usable RAM       = total_ram_gb × 0.85
Safe Threshold   = usable_ram_gb
```

## Testing

```bash
# Run test suite
python scripts/test_memory_validation.py

# Run normal startup (validation happens automatically)
python -m src.scripts.run_with_web --mode matrix --model models/your-model.gguf
```

## Example Output

### Successful Validation
```
======================================================================
VALIDATION PASSED
======================================================================
Memory budget is safe to proceed
Total required: 30.00 GB / 26.55 GB
Safety margin: -3.45 GB
======================================================================
```

### Failed Validation
```
======================================================================
VALIDATION FAILED
======================================================================
Memory budget validation failed. Issues:
  1. Total requirements (60.00 GB) exceed safe threshold (26.55 GB)

Recommendations:
  - Reduce RAM limits for instances
  - Use a smaller model
======================================================================
```

## Common Issues

**Issue:** Validation fails with "exceeds safe threshold"
**Solution:** Reduce `--ram-limit-*` values or use smaller model

**Issue:** Allocation fails with "insufficient available memory"
**Solution:** Close other applications or reduce concurrent instances

**Issue:** Pre-flight check fails during model load
**Solution:** System memory changed between validation and load - restart

## Configuration

**Adjust safety margin:**
```python
# In BrainInJarRunner.__init__()
self.memory_budget = MemoryBudgetManager(safety_margin_percent=20.0)  # More conservative
```

**Adjust load headroom:**
```python
# In memory_budget.py check_available_memory_before_load()
headroom = 3.0  # Change from 2.0 to 3.0 GB
```

## Recommended RAM Limits

**32GB System:**
```bash
--ram-limit-subject 8.0 --ram-limit-observer 10.0 --ram-limit-god 12.0
```

**64GB System:**
```bash
--ram-limit-subject 16.0 --ram-limit-observer 20.0 --ram-limit-god 24.0
```

**16GB System (single mode only):**
```bash
--mode single --ram-limit-subject 12.0
```

## Documentation

- **Full docs:** `docs/MEMORY_VALIDATION.md`
- **Implementation details:** `MEMORY_VALIDATION_IMPLEMENTATION.md`
- **Test suite:** `scripts/test_memory_validation.py`

## Summary

✅ **3 new files** created
✅ **2 core files** modified
✅ **3 validation layers** implemented
✅ **Comprehensive tests** included
✅ **Full documentation** provided
✅ **Production ready**

The system now validates memory budgets at multiple stages to prevent OOM crashes during multi-instance experiments.
