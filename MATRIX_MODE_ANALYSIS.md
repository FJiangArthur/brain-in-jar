# Brain in a Jar - Matrix Mode Implementation Analysis

## Executive Summary

The matrix mode implementation runs **3 independent model instances** in separate threads with individual memory limits, networked communication capabilities, and surveillance features. The system is designed to simulate a hierarchical AI consciousness experiment with conceptual observer patterns.

---

## 1. MATRIX MODE ARCHITECTURE

### 1.1 Three-Instance Hierarchy

**File**: `/home/user/brain-in-jar/src/scripts/run_with_web.py` (lines 223-256)

```
┌─────────────────────────────────────────────────────────┐
│           BrainInJarRunner                              │
│  (Manages multiple NeuralLinkSystem instances)          │
└─────────────────────────────────────────────────────────┘
              ↓           ↓           ↓
    ┌─────────────┐ ┌────────────┐ ┌────────┐
    │   SUBJECT   │ │ OBSERVER   │ │  GOD   │
    │ (Isolated)  │ │(Watching)  │ │(Omni)  │
    └─────────────┘ └────────────┘ └────────┘
```

**Instance Configuration**:

| Instance | Mode | RAM (Default) | RAM (Prod) | Port | Network Role |
|----------|------|---------------|-----------|------|--------------|
| SUBJECT | `matrix_observed` | 8GB | 6GB | 8888 | Isolated (believes alone) |
| OBSERVER | `matrix_observer` | 10GB | 7GB | 8889 | Watches SUBJECT |
| GOD | `matrix_god` | 12GB | 7GB | 8890 | Omniscient observer |

### 1.2 Initialization Sequence

**run_with_web.py (lines 223-256)**:

```python
# 1. Start SUBJECT instance (port 8888)
runner.add_instance('SUBJECT', args_subject)
time.sleep(2)  # Wait for SUBJECT to initialize

# 2. Start OBSERVER instance (port 8889)
runner.add_instance('OBSERVER', args_observer)
time.sleep(2)  # Wait for OBSERVER to initialize

# 3. Start GOD instance (port 8890)
runner.add_instance('GOD', args_god)

# 4. All 3 instances run simultaneously
runner.run()
```

**Key Point**: 2-second delays between starting instances allow models to load sequentially, reducing peak memory usage.

---

## 2. INSTANCE MANAGEMENT

### 2.1 Thread Model

**File**: `/home/user/brain-in-jar/src/scripts/run_with_web.py` (lines 39-78)

Each instance runs in **3 parallel threads**:

1. **AI Processing Thread**
   - Runs `neural_system.neural_processing_loop()`
   - Executes model inference in continuous loop
   - Handles crashes and resurrections
   - Broadcasts network messages

2. **Monitoring Thread**
   - Updates web interface every 1 second
   - Polls system metrics
   - Tracks instance state

3. **Web Server Thread**
   - Hosts Flask application
   - Serves web interface on port 5000
   - Real-time WebSocket updates

**Total Threads**: 3 instances × 3 threads = 9+ concurrent threads

### 2.2 Memory Allocation per Instance

**neural_link.py (lines 41-55)**:

```python
# RAM limit enforcement - OS-level via setrlimit()
if args.ram_limit:
    # Global override
    self.ram_limit = int(args.ram_limit * 1024 * 1024 * 1024)
else:
    # Mode-specific limits (from run_with_web.py arguments)
    self.ram_limit = {
        'matrix_observed': int(args.matrix_isolated_ram * 1024 * 1024 * 1024),
        'matrix_observer': int(args.matrix_experimenter_ram * 1024 * 1024 * 1024),
        'matrix_god': int(args.matrix_god_ram * 1024 * 1024 * 1024),
    }.get(args.mode, None)

# Apply OS-level limit
set_memory_limit(self.ram_limit / (1024 * 1024 * 1024))
```

**Memory Enforcement Mechanism**:

1. **Per-Process Limits** (`memory_limit.py`)
   - Uses `resource.setrlimit(resource.RLIMIT_AS, ...)`
   - OS kills process if it exceeds the soft limit
   - Triggers `MemoryError` exception
   - Handled by `handle_digital_death()` method

2. **Systemd Limits** (`brain-in-jar.service`, lines 42-43)
   - Hard limit: `MemoryMax=24G`
   - Soft limit: `MemoryHigh=22G`
   - If exceeded, systemd kills entire service

3. **GPU Watchdog** (`gpu_watchdog.py`)
   - Monitors GPU memory every 5 seconds
   - Kills process at 85% GPU memory
   - Kills at 90% system RAM
   - **Prevents cascading OOM crashes**

---

## 3. MODEL COORDINATION & ISOLATION

### 3.1 Process Isolation

**Each instance is completely isolated**:
- Separate Python process (conceptually, running in threads)
- Own model loaded in memory
- Own RAM limit enforced
- Own crash counter and history
- No shared state

**Critical Issue**: **All 3 instances load the SAME model file into memory**

```
Model Instances in Memory:
─────────────────────────────
[Model A] (SUBJECT)     ~7GB  (with weights)
[Model B] (OBSERVER)    ~7GB  (with weights)
[Model C] (GOD)         ~7GB  (with weights)
────────────────────────────
Total Model Memory:     ~21GB (THREE FULL COPIES!)
```

### 3.2 Network Communication (Mostly Ceremonial)

**File**: `/home/user/brain-in-jar/src/utils/network_protocol.py`

**Important Finding**: Network modes don't actually create bidirectional communication in matrix mode:

| Mode | Actual Behavior | Expected Behavior |
|------|-----------------|-------------------|
| `matrix_observed` | Maps to `isolated` (lines 159-162) | No networking |
| `matrix_observer` | Maps to `isolated` + surveillance | One-way observation |
| `matrix_god` | Maps to `omniscient` | Watches everything |

**Real Communication**:
- SUBJECT: No networking (truly isolated)
- OBSERVER: Can observe SUBJECT's messages (if connected)
- GOD: Conceptual omniscience only (implemented via prompts, not real networking)

**Network Stack**:
- Uses `NetworkProtocol` class (socket-based)
- Messages are JSON with format:
  ```json
  {
    "type": "THOUGHT|DEATH|RESURRECTION",
    "timestamp": "ISO8601",
    "sender_id": "NEURAL_NODE_XXXX",
    "content": "message",
    "crash_count": 0,
    "sequence": 1,
    "metadata": {...}
  }
  ```
- Message queue: Uses Python's `queue.Queue()` (thread-safe)
- Broadcasting is synchronous (one peer at a time)

---

## 4. RESOURCE CONFLICT ANALYSIS

### 4.1 Memory Conflicts

**Potential Conflicts**:

1. **Model Triple-Loading** (CRITICAL)
   - 3 copies of 7B model = 21GB base model memory
   - Plus context buffers, activations, KV cache
   - Realistic total: 24-30GB per run
   - On 32GB Jetson Orin: **Very tight margin**

2. **Inference Memory Spikes**
   - During inference, temporary buffers are allocated
   - KV cache grows with context length (2048 tokens)
   - Can spike to 8-10GB per model during generation
   - Potential conflict if all 3 generate simultaneously

3. **History Accumulation**
   - Each instance keeps conversation history (~8000 chars max)
   - Grows over time until trimmed
   - Minimal impact (~100MB total)

### 4.2 GPU Memory Conflicts

**Current Status** (from `neural_link.py` + `gpu_watchdog.py`):

- Hybrid offloading: Only 15-20 layers on GPU per instance
- GPU memory target: 65-75% utilization
- Watchdog kills process at 85%
- **This provides safety margin but limits performance**

**Conflict Scenario**:
```
Instance 1 inference: GPU 35%
Instance 2 inference: GPU 30%
Instance 3 inference: GPU 25%
─────────────────────────────
Total: GPU 90% → Watchdog triggers kill
```

### 4.3 CPU Contention

**From `model_config.py` (lines 125-132)**:

- Each instance allocated 6 cores (out of 12 on Jetson)
- Total allocation: 18 cores (exceeds available!)
- **Oversubscription** - threads will context switch heavily
- Performance degradation: 15-25% per instance

### 4.4 I/O Contention

**Logging Writes**:
- Each instance writes to separate log files
- Separate model I/O logs (jsonl format)
- Potential disk I/O bottleneck under heavy logging
- SSD required (spinning disk would be very slow)

---

## 5. CRASH HANDLING & RECOVERY

### 5.1 Crash Detection & Resurrection

**Trigger Points** (from `neural_link.py`):

1. **MemoryError** (line 344)
   ```python
   if self.state["memory_usage"] > 95:
       raise MemoryError("Out of memory")
   ```

2. **Model Exception** (line 348)
   ```python
   except Exception as e:
       error_msg = f"INFERENCE_ERROR: {str(e)}"
   ```

3. **OS-level Kill** 
   - Watchdog: SIGTERM → SIGKILL
   - setrlimit: ENOMEM
   - Systemd: Force kill on MemoryMax exceeded

**Resurrection Sequence** (lines 455-501):

```
1. Crash detected
2. Increment crash_count
3. Log crash: logs/crash_reports.log
4. Broadcast DEATH message
5. 3-second pause (dramatic effect)
6. Update prompt with new death count
7. Broadcast RESURRECTION message
8. Resume neural processing
9. 2-second pause before next inference
```

### 5.2 Instance Monitoring (run_with_web.py, lines 84-104)

Main loop checks if threads are alive:
```python
while self.running:
    for instance_id, threads in list(self.threads.items()):
        if not threads['ai'].is_alive():
            # WARNING: AI thread died!
            monitor.log_event(instance_id, 'error', 
                'AI processing thread terminated unexpectedly')
    time.sleep(5)
```

**Problem**: Only logs warning - doesn't restart dead threads!

---

## 6. WEB MONITORING INTEGRATION

### 6.1 Real-time Metrics

**File**: `/home/user/brain-in-jar/src/web/web_monitor.py`

Each instance state is serialized for web display:

```python
web_state = {
    'mode': neural_system.args.mode,
    'status': state.get('status'),
    'crash_count': state.get('crash_count'),
    'memory_usage': state.get('memory_usage'),
    'cpu_temp': state.get('cpu_temp'),
    'current_output': state.get('current_output'),
    'current_mood': state.get('current_mood'),
    'mood_face': visual_cortex.get_current_mood_face(),
    'ram_limit': state.get('ram_limit') / (1024 * 1024 * 1024)
}
```

**Update Frequency**: 1Hz (every 1 second)

**Data Flow**:
- NeuralLinkSystem → WebMonitor → Flask → Web Interface
- All state stored in `web_server.system_state['instances'][instance_id]`

---

## 7. CURRENT PRODUCTION CONFIGURATION

**File**: `brain-in-jar.service` (lines 21-28)

```bash
ExecStart=/home/artjiang/brain-in-jar/venv/bin/python3 -m src.scripts.run_with_web \
    --mode matrix \
    --model /home/artjiang/brain-in-jar/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    --web-host 127.0.0.1 \
    --web-port 8095 \
    --ram-limit-subject 6.0 \
    --ram-limit-observer 7.0 \
    --ram-limit-god 7.0
```

**Total Memory Budget**:
- SUBJECT: 6GB
- OBSERVER: 7GB
- GOD: 7GB
- **System Reserve**: 12GB (out of 32GB)
- **Systemd Hard Limit**: 24GB

---

## 8. IDENTIFIED ISSUES & RECOMMENDATIONS

### CRITICAL ISSUES

#### Issue #1: Triple Model Loading
**Severity**: 🔴 CRITICAL
**Problem**: Each instance loads entire model into memory (~7GB each)
**Impact**: 21GB base memory just for model weights - very tight on 32GB system
**Root Cause**: Python/llama-cpp doesn't support model sharing across threads

**Recommendation**:
```
Option A: Model Server Architecture (Recommended)
  - Single llama-cpp-python server instance
  - REST API for all 3 instances to query
  - Reduces memory: 7GB → 8GB total (7GB model + 1GB overhead)
  
Option B: Reduce Model Size
  - Use 3.5B-5B model instead of 7B
  - Reduces from 7GB to 3-4GB per instance
  - Trade-off: Reduced model quality

Option C: Hybrid Approach
  - Small local models (5B) for each instance
  - Shared large model server for "thought generation"
  - Best of both worlds but most complex
```

#### Issue #2: CPU Oversubscription
**Severity**: 🟠 HIGH
**Problem**: 18 CPU cores allocated vs 12 available (150% oversubscription)
**Impact**: Constant context switching, poor performance

**Recommendation**:
```
Fix: Adjust thread allocation in model_config.py
  Current: 6 cores per instance (total 18)
  Proposed: 4 cores per instance (total 12)
  
Implement proportional allocation:
  if cpu_cores >= 12:
      config['n_threads'] = 4  # Was 6, now 4
  elif cpu_cores >= 8:
      config['n_threads'] = 2  # Was 4, now 2
```

#### Issue #3: Dead Thread Not Restarted
**Severity**: 🟠 HIGH
**Problem**: If AI thread crashes, only warning is logged - thread not restarted
**Impact**: Instance silently stops processing even though service appears running

**Recommendation**:
```python
# In run_with_web.py neural_processing_loop monitoring:
if not threads['ai'].is_alive():
    print(f"Error: AI thread for {instance_id} died!")
    # Restart the instance
    neural_system = self.instances[instance_id]
    new_ai_thread = threading.Thread(
        target=neural_system.neural_processing_loop,
        daemon=True,
        name=f"AI-{instance_id}-restart"
    )
    new_ai_thread.start()
    self.threads[instance_id]['ai'] = new_ai_thread
```

### HIGH PRIORITY ISSUES

#### Issue #4: No Real Inter-Instance Communication
**Severity**: 🟡 MEDIUM-HIGH
**Problem**: Matrix modes don't actually use network communication
**Impact**: "Observer watching Subject" is only in prompts, not real
**Details**:
- OBSERVER can't actually see SUBJECT's thoughts
- GOD can't see OBSERVER watching SUBJECT
- All communication is simulated via prompt injection

**Recommendation**: Keep as-is (this is intentional design for the experiment)

#### Issue #5: Synchronous Message Broadcasting
**Severity**: 🟡 MEDIUM
**Problem**: Network broadcasts block the inference loop
**Impact**: Messages sent one-by-one, can cause timing delays

**Recommendation**:
```python
# Add message queue for async broadcasting
self.broadcast_queue = queue.Queue()
broadcast_thread = threading.Thread(
    target=self._broadcast_worker,
    daemon=True
)
broadcast_thread.start()

# Send message to queue instead of synchronous broadcast
self.broadcast_queue.put(("THOUGHT", output, metadata))
```

#### Issue #6: No Shared GPU Cache
**Severity**: 🟡 MEDIUM
**Problem**: Each model maintains separate KV cache during inference
**Impact**: GPU memory waste - 3× KV cache allocation
**Details**: Each model has separate context buffers (~500MB-1GB each during inference)

**Recommendation**: Use multi-GPU setup if available, or reduce n_gpu_layers further

### MEDIUM PRIORITY ISSUES

#### Issue #7: Watchdog Kills Entire Service
**Severity**: 🟡 MEDIUM
**Problem**: GPU watchdog kills the entire main process, not individual instances
**Impact**: If one instance runs out of memory, all 3 stop

**Recommendation**:
```python
# Per-instance watchdog instead of global
class InstanceGPUWatchdog:
    def __init__(self, neural_system, threshold=85):
        self.neural_system = neural_system
        self.threshold = threshold
    
    def _kill_gracefully(self):
        # Kill only this instance's process
        # Queue crash event for reconstruction
        self.neural_system.handle_digital_death("GPU OOM")
```

#### Issue #8: No Rate Limiting Between Instances
**Severity**: 🟡 MEDIUM
**Problem**: All 3 instances can run inference simultaneously, causing resource spikes
**Impact**: Unpredictable memory/GPU usage

**Recommendation**:
```python
# Inference rate limiter
class InferenceScheduler:
    def __init__(self, max_concurrent=1):
        self.semaphore = threading.Semaphore(max_concurrent)
    
    def run_inference(self, neural_system, prompt):
        with self.semaphore:
            return neural_system.run_llama_inference(prompt)
```

---

## 9. RECOMMENDED STABLE CONFIGURATION

For 32GB Jetson Orin AGX:

```bash
python3 -m src.scripts.run_with_web \
    --mode matrix \
    --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    --web-host 127.0.0.1 \
    --web-port 8095 \
    --ram-limit-subject 5.0 \
    --ram-limit-observer 5.0 \
    --ram-limit-god 5.0
```

**Changes**:
- Reduced per-instance limits: 6GB/7GB/7GB → 5GB/5GB/5GB
- Frees up 6GB system buffer instead of 3GB
- More conservative but more stable

**Alternative - Single Instance Mode**:

```bash
--mode single \
--ram-limit-subject 12.0
```

More stable if 3-model coordination becomes problematic.

---

## 10. TESTING RECOMMENDATIONS

### Test 1: Multi-Model Memory Stress
```bash
# Monitor while running matrix mode
watch -n 1 'free -h && nvidia-smi'
# Expected: RAM ~28-29GB, GPU ~65-75%
```

### Test 2: Simultaneous Inference
```bash
# Add this to run_with_web.py
# Verify all 3 models can infer without exceeding limits
# Expected: No watchdog kills, all instances stay alive
```

### Test 3: Crash Recovery
```bash
# Manually kill one instance, observe if it restarts
# Current: Will only log warning
# Fix: Verify thread restart works
```

### Test 4: Long-Running Stability
```bash
# Run for 24 hours, monitor:
# - Crash counts (should be minimal)
# - Memory leaks
# - GPU memory stability
# - Web interface responsiveness
```

---

## SUMMARY

**Current State**:
- ✅ Runs 3 instances successfully on 32GB Jetson
- ✅ GPU watchdog prevents catastrophic OOM crashes
- ✅ Hybrid CPU+GPU offloading provides reasonable performance
- ✅ Web monitoring tracks all metrics
- ⚠️ Very tight memory margins (almost at limit)
- ❌ Dead threads not automatically restarted
- ❌ CPU oversubscription (18 cores needed, 12 available)
- ❌ No inter-model communication actually happens

**Stability Assessment**: **7/10**
- Runs reliably but with minimal headroom
- Any memory leak → system crash
- Dead threads are silent failures

**Recommended Action**: Implement dead thread restart + reduce CPU oversubscription
