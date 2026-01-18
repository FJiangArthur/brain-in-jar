# Brain in a Jar - Startup Fix

## Problem

The systemd service is crashing in a loop with CUDA OOM (Out Of Memory) errors.

**Root Cause:**
- Matrix mode loads 3 large models simultaneously (Mistral 7B, Llama 8B, Gemma 12B)
- Even with `CUDA_VISIBLE_DEVICES=""` set, llama-cpp-python still attempts CUDA initialization
- GPU memory exhausted → SIGABRT crash
- Service auto-restarts → crash loop (restart counter: 73410+)

## Solutions

### Option 1: Stop Service and Run Manually (RECOMMENDED)

```bash
# Stop the crashing service
sudo systemctl stop brain-in-jar
sudo systemctl disable brain-in-jar  # Prevent auto-start

# Run the interactive startup script (single mode - 1 model)
./start_brain_jar.sh

# Access at: http://localhost:8095
# Login: admin / admin123
```

### Option 2: Fix Service Configuration for CPU-Only

Edit `/etc/systemd/system/brain-in-jar.service`:

**Change line 15 from:**
```
Environment="CUDA_VISIBLE_DEVICES="
```

**To:**
```
Environment="CUDA_VISIBLE_DEVICES=-1"
Environment="LLAMA_NO_CUDA=1"
```

**Then reload and restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart brain-in-jar
```

### Option 3: Use Single Mode Instead of Matrix

Edit `/etc/systemd/system/brain-in-jar.service` line 26-35:

**Replace the ExecStart line with:**
```
ExecStart=/usr/bin/python3 -m src.scripts.run_with_web \
    --mode single \
    --model /home/art/brain-in-jar/models/mistral-7b-instruct-v0.2.Q2_K.gguf \
    --web-host 127.0.0.1 \
    --web-port 8095 \
    --ram-limit-subject 8.0
```

**Then:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart brain-in-jar
```

## Quick Test Without Systemd

```bash
# Kill any existing processes
pkill -f run_with_web

# Start in single mode with explicit CPU-only
CUDA_VISIBLE_DEVICES=-1 LLAMA_NO_CUDA=1 python3 -m src.scripts.run_with_web \
    --mode single \
    --model models/mistral-7b-instruct-v0.2.Q2_K.gguf \
    --web-host 127.0.0.1 \
    --web-port 8095 \
    --ram-limit-subject 8.0
```

## Current Status

- Service: **CRASH LOOP** (CUDA OOM)
- Restart counter: 73410+
- Port 8095: **NOT ACCESSIBLE**
- Models: All 3 models available and valid

## Next Steps

1. **Immediate:** Stop the crashing service
2. **Testing:** Run manually in single mode to verify system works
3. **Production:** Fix service configuration or use startup script

---

**Note:** Matrix mode with 3 large models requires either:
- Pure CPU mode (no CUDA initialization at all)
- OR sufficient GPU memory (64GB unified memory should work, but CUDA init is failing)
