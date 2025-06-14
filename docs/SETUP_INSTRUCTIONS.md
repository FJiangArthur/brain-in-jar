# 🧠 Enhanced Brain-in-Jar Setup Instructions

## Overview

This enhanced setup solves the common **Llama CPP Python shared library issues** and adds:
- ✅ **ASCII Facial Expressions** - Emotional responses through art
- ✅ **Computer Vision** - Image analysis, camera capture, person segmentation
- ✅ **Platform Optimization** - ARM/x86 specific build flags
- ✅ **Shared Library Fix** - Proper linking for llama-cpp-python

## Quick Start

### 1. Run the Setup Script
```bash
./setup_brain_jar.sh
```

### 2. Activate Environment
```bash
source venv/bin/activate
```

### 3. Download a Model (Optional)
```bash
# For Raspberry Pi (small model)
wget https://huggingface.co/microsoft/DialoGPT-small/resolve/main/pytorch_model.bin

# For more powerful systems
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
```

### 4. Run the Interface
```bash
# With AI model
python3 enhanced_neural_interface.py --model path/to/model.gguf

# Vision-only mode (no model needed)
python3 enhanced_neural_interface.py --no-vision
```

## Platform-Specific Optimizations

### 🍓 Raspberry Pi
- **ARM64/ARM32 optimizations**
- **OpenBLAS acceleration** 
- **Camera support** via picamera2
- **Memory-efficient** settings
- **Build flags**: `-march=armv8-a+crc+simd -mtune=cortex-a72`

### 🚀 NVIDIA Jetson
- **CUDA acceleration** enabled
- **Tegra architecture** optimizations
- **Hardware video** processing
- **Build flags**: `LLAMA_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=53;62;72;87`

### 💻 x86_64 Linux
- **AVX2 and FMA** optimizations
- **Maximum performance** flags
- **Full feature** support
- **Build flags**: `LLAMA_AVX2=ON -DLLAMA_FMA=ON`

## Features in Detail

### 😊 Emotional ASCII Faces

The system expresses emotions through ASCII art:

```
Happy:           Thinking:         Angry:
    ◕   ◕           ◐   ◑          ▸       ◂
  ◕  ◡  ◕        ◐  ·  ◑       ▸  ●   ●  ◂
      ◡              ·                ▲
   \  ___  /      ╰  ...  ╯       ╰ ███ ╯
     \___/          hmm...         GRRRR!
```

**Available emotions:**
- HAPPY, SAD, ANGRY, SURPRISED
- CONFUSED, THINKING, EXCITED, TIRED  
- NEUTRAL, LOVE, WORRIED, FOCUSED

### 👁 Computer Vision System

**Image Processing:**
- **Face detection** with confidence scores
- **Color analysis** and dominant color extraction
- **Edge/texture analysis** for complexity assessment
- **Motion detection** through background subtraction

**Person Segmentation:**
- **Background subtraction** (MOG2 algorithm)
- **Color-based segmentation** (skin tone detection)
- **Edge-based segmentation** for object boundaries
- **Morphological filtering** for clean results

**ASCII Art Generation:**
- **Standard ASCII**: ` .:-=+*#%@`
- **Detailed ASCII**: Full character set for high detail
- **Aspect ratio correction** for proper display

### 💬 Interactive Commands

```bash
# Vision Commands
/image <path>      # Analyze image file
/camera           # Capture from camera  
/segment <path>   # Segment people in image

# Emotion Commands
/emotion <name>   # Show specific emotion
/demo            # Demo all emotions

# System Commands
/status          # Show system status
/help            # Show help
/quit            # Exit
```

## Troubleshooting

### ❌ Shared Library Issues

**Problem**: `ImportError: libllama.so: cannot open shared object file`

**Solution**:
```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
sudo ldconfig

# Make permanent
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
```

### ❌ Camera Not Working

**Raspberry Pi**:
```bash
sudo raspi-config  # Enable camera
sudo usermod -a -G video $USER
```

**General Linux**:
```bash
sudo usermod -a -G video $USER
# Check camera permissions
ls -l /dev/video*
```

### ❌ Out of Memory (Raspberry Pi)

**Use smaller models**:
- TinyLlama-1.1B (Q4_0) - ~600MB
- Phi-2-2.7B (Q4_K_M) - ~1.5GB

**Reduce context size**:
```python
# Edit enhanced_neural_interface.py
n_ctx = 1024  # Instead of 2048
```

### ❌ CUDA Issues (Jetson)

```bash
export CUDA_PATH=/usr/local/cuda
export PATH=$CUDA_PATH/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH

# Verify CUDA
nvcc --version
nvidia-smi
```

### ❌ Build Failures

**Missing dependencies**:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential cmake git python3-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
```

**CMake version too old**:
```bash
# Install newer CMake
wget https://github.com/Kitware/CMake/releases/download/v3.25.0/cmake-3.25.0-linux-x86_64.sh
sudo sh cmake-3.25.0-linux-x86_64.sh --prefix=/usr/local --skip-license
```

## Model Recommendations

### Raspberry Pi 4 (4GB+)
- **TinyLlama-1.1B-Chat** (Q4_K_M) - ~800MB  
- **Phi-2-2.7B** (Q4_0) - ~1.5GB
- **DistilBERT** for embeddings

### Jetson Nano/Xavier  
- **Llama-2-7B-Chat** (Q4_K_M) - ~4GB
- **Code Llama-7B** (Q4_0) - ~3.5GB
- **Mistral-7B** (Q4_K_M) - ~4GB

### x86_64 (8GB+ RAM)
- **Llama-2-13B-Chat** (Q4_K_M) - ~7GB  
- **Mixtral-8x7B** (Q4_K_M) - ~26GB
- **Code Llama-34B** (Q4_K_M) - ~20GB

## Performance Tips

1. **Use quantized models** (Q4_K_M recommended)
2. **Monitor temperature** on embedded devices
3. **Use SSD storage** for faster model loading
4. **Adjust batch size** based on available RAM
5. **Enable hardware acceleration** when available

## File Structure

```
brain-in-jar/
├── setup_brain_jar.sh           # Main setup script
├── enhanced_neural_interface.py # Main application
├── emotion_engine.py           # ASCII emotion system  
├── vision_system.py            # Computer vision
├── venv/                       # Python environment
├── lib/llama-cpp/             # Compiled Llama CPP
└── models/                    # Your GGUF models
```

## Usage Examples

### Basic Chat
```bash
python3 enhanced_neural_interface.py --model model.gguf
> Hello! How are you?
🧠 AI: I'm doing great! Ready to help you today.
```

### Image Analysis
```bash
> /image photo.jpg
📊 Analysis:
Image: 640x480 pixels
Lighting: bright (avg: 180.5/255)
People: 2 face(s) detected
  - Face 0: confidence 0.85
Colors:
  - Color 1: RGB(120, 150, 200) (35.2%)
```

### Camera Capture
```bash
> /camera
📸 Activating camera...
[Camera preview opens - press SPACE to capture]
🧠 AI: I can see a well-lit room with...
```

### Emotion Display  
```bash
> /emotion EXCITED
😊 Displaying: excited
    ★   ★    
  ★  !  ★  
      !      
   \  !!!  / 
    WOW!!!   
```

Happy brain-in-jarring! 🧠✨

## Support

For issues:
1. Check this troubleshooting guide
2. Verify dependencies are installed
3. Test components individually
4. Check system logs for errors

The setup script provides comprehensive platform detection and optimization for the best performance on your specific hardware.