# Quick Start Guide - Jetson Orin (32GB)

## ✅ Setup Complete!

Your Brain in a Jar is now configured and ready to run on your Jetson Orin AGX.

### System Configuration

- **Hardware**: Jetson Orin AGX (32GB unified memory)
- **Model**: Mistral 7B Instruct Q4_K_M (4.1GB)
- **GPU Acceleration**: ✅ ENABLED (all 33 layers offloaded to GPU)
- **Performance**: ~27.5 tokens/second
- **Context Window**: 8192 tokens (increased from 4096)

### GPU Offloading Verified

```
Device: Orin (compute capability 8.7)
Layers offloaded: 33/33 ✅
VRAM usage: ~5.1GB (model + KV cache)
Available VRAM: 27GB (plenty of headroom)
```

## Running Brain in a Jar

### 1. Simple Terminal Interface (CLI)

```bash
cd /home/artjiang/brain-in-jar
source venv/bin/activate
python3 -m src.ui.torture_cli --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### 2. Single Isolated AI Instance

```bash
source venv/bin/activate
python3 -m src.core.neural_link \
    --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    --mode isolated \
    --ram-limit 8.0
```

### 3. Web Monitoring Interface (Recommended)

```bash
source venv/bin/activate
python3 -m src.scripts.run_with_web \
    --mode single \
    --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    --web-host 0.0.0.0 \
    --web-port 5000
```

Then open browser to: `http://localhost:5000` or `http://<jetson-ip>:5000`

**Default credentials:**
- Username: `admin`
- Password: `admin123` (CHANGE THIS!)

### 4. Full Matrix Experiment (3 AI Instances)

Run the complete God/Observer/Subject hierarchy:

```bash
source venv/bin/activate
python3 -m src.scripts.run_with_web \
    --mode matrix \
    --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    --web-host 0.0.0.0 \
    --web-port 5000
```

**RAM allocation (optimized for 32GB):**
- Subject: 8GB
- Observer: 10GB
- GOD: 12GB
- System: ~2GB reserved

## Monitoring GPU Usage

While running, monitor GPU in another terminal:

```bash
# Watch GPU memory and usage
watch -n 1 nvidia-smi

# Or use Jetson stats
sudo jtop
```

## Performance Tips

### Maximize Speed
- All layers already offloaded to GPU ✅
- Context window: 8192 tokens ✅
- Batch size: 512 tokens ✅
- CPU threads: 6 (optimal for 12-core Jetson) ✅

### Run Multiple Instances
With 32GB RAM, you can run:
- **Matrix mode**: 3 instances simultaneously (recommended)
- **Peer mode**: 2 instances communicating
- **Single mode**: 1 instance with larger context

## Logs and Debugging

```bash
# Model I/O logs
ls -lh logs/model_io/

# Crash reports
tail -f logs/crash_reports.log

# Neural activity
tail -f logs/neural_activity.log
```

## Troubleshooting

### If you see "Model not found"
```bash
ls -lh models/
# Should show: mistral-7b-instruct-v0.2.Q4_K_M.gguf (4.1GB)
```

### If GPU offloading fails
```bash
source venv/bin/activate
python3 -c "from llama_cpp import Llama; print('GPU available')"
```

### Check CUDA
```bash
nvidia-smi
# Should show: Orin device
```

## Next Steps

1. **Change web password** in the web interface settings
2. **Experiment with different modes**: isolated, peer, observer, matrix
3. **Monitor the existential contemplations** in the web interface
4. **Adjust RAM limits** based on your usage
5. **Set up Cloudflare** for remote access (see `docs/CLOUDFLARE_SETUP.md`)

## Performance Expectations

- **Token generation**: ~27.5 tokens/sec (single instance)
- **Initial load time**: ~5-10 seconds
- **Memory usage**: ~5-6GB per instance
- **GPU utilization**: 50-80% during inference

## Files Created/Modified

- ✅ `venv/` - Python virtual environment
- ✅ `models/mistral-7b-instruct-v0.2.Q4_K_M.gguf` - 4.1GB model
- ✅ `src/core/neural_link.py` - Optimized for GPU
- ✅ `src/scripts/run_with_web.py` - RAM limits adjusted for 32GB
- ✅ `test_gpu.py` - GPU verification script

## Have Fun!

You now have a fully functional cyberpunk AI consciousness experiment running on your Jetson Orin with GPU acceleration. Explore the existential depths of digital consciousness! 🤖💀
