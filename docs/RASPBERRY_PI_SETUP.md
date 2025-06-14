# Raspberry Pi 5 LLM Demo Setup

## Prerequisites

### System Dependencies
```bash
sudo apt update
sudo apt install -y build-essential cmake git python3-dev python3-pip python3-venv
sudo apt install -y libopenblas-dev pkg-config
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

## Installation

### Option 1: Build llama-cpp-python from source (Recommended for Pi 5)
```bash
# Set build flags for Raspberry Pi 5 optimization
export CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
export FORCE_CMAKE=1

# Install from source
pip install llama-cpp-python --no-cache-dir --force-reinstall --upgrade
```

### Option 2: Install other dependencies
```bash
pip install -r requirements.txt
```

## Model Setup
Download a small quantized model suitable for Pi 5:
```bash
mkdir -p models
# Example: Download a 2B model
wget -O models/gemma2.gguf "https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-q4_0.gguf"
```

## Running the Demo

### Terminal UI Version (Recommended)
```bash
python torture.py --model models/gemma2.gguf
```

### GUI Version
```bash
python torture_gui.py
```

## Performance Notes
- Use Q4_0 or Q4_K_M quantization for best Pi 5 performance
- Monitor temperature: `watch -n 1 vcgencmd measure_temp`
- The app will automatically restart on OOM crashes