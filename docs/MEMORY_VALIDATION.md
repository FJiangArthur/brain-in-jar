# Memory Validation System

## Overview

The memory validation system provides comprehensive pre-checks to prevent OOM (Out of Memory) crashes when running Brain in a Jar experiments. It validates memory budgets at multiple stages:

1. **Global validation** - Before starting any instances
2. **Per-instance allocation** - Before creating each instance
3. **Pre-model-load checks** - Before loading the LLM model

## Components

### 1. MemoryBudgetManager (`src/utils/memory_budget.py`)

Tracks and coordinates memory allocations across all AI instances.

**Features:**
- Tracks allocated memory budgets per instance
- Estimates model memory footprint (file size × 1.5 for overhead)
- Enforces safe threshold (85% of total RAM)
- Thread-safe allocation/deallocation
- Detailed allocation reports

**Usage:**
```python
from src.utils.memory_budget import MemoryBudgetManager

# Initialize with 15% safety margin for OS
manager = MemoryBudgetManager(safety_margin_percent=15.0)

# Allocate memory for an instance
can_allocate, msg = manager.allocate("INSTANCE_1", ram_limit_gb=8.0, model_path="model.gguf")

if can_allocate:
    # Create instance
    pass
else:
    print(f"Allocation failed: {msg}")

# Deallocate when instance stops
manager.deallocate("INSTANCE_1")

# Get allocation report
print(manager.get_allocation_report())
```

### 2. validate_memory_budget() Function

Global validation before starting multi-instance experiments.

**Features:**
- Validates total memory requirements for all instances
- Accounts for model footprint and RAM limits
- Checks against safe threshold (85% of total RAM)
- Provides detailed validation report with recommendations

**Usage:**
```python
from src.utils.memory_budget import validate_memory_budget

ram_limits = {
    'subject': 8.0,   # GB
    'observer': 10.0,
    'god': 12.0
}

is_valid, report = validate_memory_budget(
    mode='matrix',
    ram_limits=ram_limits,
    model_path='models/your-model.gguf'
)

if not is_valid:
    print("Memory validation failed!")
    print(report)
    sys.exit(1)
```

### 3. check_available_memory_before_load() Function

Pre-flight check immediately before loading a model into memory.

**Features:**
- Checks current available system memory
- Estimates required memory (model footprint + headroom)
- Warns if system memory already high (>75%)
- Provides clear pass/fail with detailed message

**Usage:**
```python
from src.utils.memory_budget import check_available_memory_before_load

can_load, msg = check_available_memory_before_load(
    model_path='models/your-model.gguf',
    ram_limit_gb=8.0
)

if not can_load:
    raise MemoryError(f"Cannot load model: {msg}")

# Proceed with model loading
```

## Integration Points

### In `src/scripts/run_with_web.py`

**1. Main Entry Point - Global Validation**
```python
def main():
    # Validate BEFORE creating any instances
    is_valid, report = validate_memory_budget(mode, ram_limits, model_path)
    if not is_valid:
        print("FATAL: Memory validation failed")
        sys.exit(1)

    # Create runner with MemoryBudgetManager
    runner = BrainInJarRunner()
```

**2. Instance Creation - Per-Instance Allocation**
```python
def add_instance(self, instance_id, args):
    # Allocate memory budget
    can_allocate, msg = self.memory_budget.allocate(
        instance_id, ram_limit, model_path
    )

    if not can_allocate:
        print(f"Allocation failed: {msg}")
        return None

    try:
        # Create instance
        neural_system = NeuralLinkSystem(args)
    except Exception as e:
        # Deallocate on failure
        self.memory_budget.deallocate(instance_id)
        raise
```

**3. Shutdown - Cleanup**
```python
def shutdown(self):
    # Print final allocation report
    print(self.memory_budget.get_allocation_report())

    # Deallocate each instance
    for instance_id in self.instances:
        self.memory_budget.deallocate(instance_id)
```

### In `src/core/neural_link.py`

**Model Loading - Pre-Flight Check**
```python
def load_model(self):
    # Pre-flight memory check
    ram_limit_gb = self.ram_limit / (1024**3)
    can_load, msg = check_available_memory_before_load(
        self.args.model, ram_limit_gb
    )

    if not can_load:
        raise MemoryError(f"Pre-flight check failed: {msg}")

    # Load model
    self.llama = Llama(model_path=self.args.model, ...)
```

## Memory Estimation

### Model Footprint Calculation

```
estimated_footprint_gb = model_file_size_gb × 1.5
```

The 1.5× multiplier accounts for:
- Model weights in memory
- Context buffers
- Inference state
- Internal llama.cpp allocations

### Required Memory

```
required_memory = max(ram_limit_gb, estimated_footprint_gb)
```

The instance needs at least enough memory to hold the model, even if the RAM limit is lower.

### Safety Thresholds

- **Usable RAM**: Total RAM × 85% (leaves 15% for OS)
- **Per-instance max**: 50% of safe threshold
- **Load headroom**: Required + 2GB extra for initialization

## Validation Flow

### Multi-Instance Startup (Matrix Mode)

```
1. User starts: python -m src.scripts.run_with_web --mode matrix

2. Global Validation
   ├─ Check total system RAM
   ├─ Estimate model footprint
   ├─ Calculate total requirements for all instances
   ├─ Validate against safe threshold (85%)
   └─ PASS or FAIL with report

3. Create MemoryBudgetManager

4. For each instance:
   ├─ Per-Instance Allocation
   │  ├─ Check current available memory
   │  ├─ Check total allocated budget
   │  └─ APPROVE or DENY allocation
   │
   ├─ Create NeuralLinkSystem
   │  └─ load_model()
   │     ├─ Pre-Flight Memory Check
   │     │  ├─ Check current available memory
   │     │  ├─ Verify headroom (required + 2GB)
   │     │  └─ PASS or FAIL
   │     └─ Load Llama model
   │
   └─ Wait for stabilization (45 seconds)

5. All instances running

6. Shutdown
   ├─ Print allocation report
   └─ Deallocate all instances
```

## Error Messages

### Validation Failed - Exceeds Safe Threshold
```
VALIDATION FAILED
Memory budget validation failed. Issues:
  1. Total requirements (30.00 GB) exceed safe threshold (27.20 GB) by 2.80 GB

Recommendations:
  - Reduce RAM limits for instances
  - Use a smaller model
  - Run fewer instances (use 'single' mode instead of 'matrix')
  - Close other applications to free memory
```

### Allocation Failed - Insufficient Memory
```
ALLOCATION FAILED: Insufficient available memory
  Required (with headroom): 13.00 GB
  Currently available: 10.50 GB
  Short by: 2.50 GB
```

### Pre-Flight Failed - Cannot Load Model
```
INSUFFICIENT MEMORY for model load
  Available: 8.50 GB
  Required: 10.50 GB (including 2.0GB headroom)
  Short by: 2.00 GB
```

## Testing

Run the test suite to verify memory validation:

```bash
python scripts/test_memory_validation.py
```

This will test:
1. MemoryBudgetManager allocation/deallocation
2. validate_memory_budget() with various configurations
3. check_available_memory_before_load() pre-flight checks

## Configuration

### Adjusting Safety Margins

**MemoryBudgetManager:**
```python
# More conservative (20% reserved for OS)
manager = MemoryBudgetManager(safety_margin_percent=20.0)

# Less conservative (10% reserved)
manager = MemoryBudgetManager(safety_margin_percent=10.0)
```

**Load Headroom:**

Edit `src/utils/memory_budget.py`:
```python
def check_available_memory_before_load(...):
    # Adjust headroom (default: 2GB)
    headroom = 3.0  # 3GB headroom
```

### Recommended RAM Limits by Hardware

**32GB System (e.g., Jetson Orin AGX):**
```bash
--ram-limit-subject 8.0   # 8GB for Subject
--ram-limit-observer 10.0 # 10GB for Observer
--ram-limit-god 12.0      # 12GB for GOD
# Total: 30GB (~94% of 32GB)
```

**64GB System:**
```bash
--ram-limit-subject 16.0   # 16GB
--ram-limit-observer 20.0  # 20GB
--ram-limit-god 24.0       # 24GB
# Total: 60GB (~94% of 64GB)
```

**16GB System (not recommended for matrix mode):**
```bash
# Use single mode only
--mode single --ram-limit-subject 12.0
```

## Benefits

1. **Prevents OOM Crashes**: Validates before allocating, not after crash
2. **Clear Error Messages**: Tells user exactly what's wrong and how to fix
3. **Safe Multi-Instance**: Coordinates allocations across instances
4. **Detailed Reports**: Shows exactly what's allocated and where
5. **Fail Fast**: Catches issues at startup, not during experiment

## Limitations

1. **Estimates Only**: Model footprint is estimated, actual usage may vary
2. **No Runtime Monitoring**: Only checks at allocation time, not during execution
   - Use GPU Watchdog for runtime protection
3. **Cannot Prevent All OOMs**: Other processes or memory leaks can still cause issues
4. **Conservative by Design**: May reject valid configurations to err on safe side

## See Also

- `src/utils/gpu_watchdog.py` - Runtime GPU/RAM monitoring
- `src/utils/model_config.py` - Model configuration optimization
- `src/utils/memory_limit.py` - OS-level memory limits
- `docs/JETSON_ORIN_SETUP.md` - Hardware-specific setup
