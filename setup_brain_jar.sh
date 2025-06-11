#!/bin/bash

# Enhanced Brain-in-Jar Setup Script
# Fixes Llama CPP shared library issues and adds advanced features
# Supports Raspberry Pi, Jetson, and x86 Linux systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}" >&2; }
warning() { echo -e "${YELLOW}[WARNING] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }

# Global variables
PLATFORM=""
CMAKE_ARGS=""

# Detect platform and set optimization flags
detect_platform() {
    local arch=$(uname -m)
    local os=$(uname -s)
    
    log "Detecting platform..."
    echo "Architecture: $arch, OS: $os"
    
    if [[ "$arch" == "aarch64" || "$arch" == "arm64" ]]; then
        if grep -q "jetson\|tegra" /proc/cpuinfo 2>/dev/null; then
            PLATFORM="jetson"
            info "Detected NVIDIA Jetson"
        elif grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
            PLATFORM="raspberry_pi"
            info "Detected Raspberry Pi (64-bit)"
        else
            PLATFORM="arm64_linux"
            info "Detected ARM64 Linux"
        fi
    elif [[ "$arch" == "armv7l" ]]; then
        PLATFORM="raspberry_pi_32"
        info "Detected Raspberry Pi (32-bit)"
    elif [[ "$arch" == "x86_64" ]]; then
        PLATFORM="x86_64_linux"
        info "Detected x86_64 Linux"
    else
        error "Unsupported architecture: $arch"
        exit 1
    fi
}

# Install build dependencies
install_dependencies() {
    log "Installing build dependencies..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            build-essential cmake git python3 python3-pip python3-dev python3-venv \
            pkg-config libopenblas-dev ninja-build ccache wget curl \
            python3-opencv libopencv-dev libcamera-dev
            
        case $PLATFORM in
            "jetson")
                sudo apt-get install -y cuda-toolkit libcudnn8-dev
                ;;
            "raspberry_pi"|"raspberry_pi_32")
                sudo apt-get install -y libraspberrypi-dev python3-picamera2
                ;;
        esac
        
    elif command -v yum &> /dev/null; then
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y cmake git python3 python3-pip python3-devel \
                           openblas-devel ninja-build ccache opencv-devel
                           
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --needed --noconfirm base-devel cmake git python \
                                          python-pip openblas ninja ccache opencv
    fi
}

# Configure platform-specific build flags
configure_build_flags() {
    log "Configuring platform-specific build flags..."
    
    case $PLATFORM in
        "jetson")
            export CUDA_PATH="/usr/local/cuda"
            export PATH="$CUDA_PATH/bin:$PATH"
            export LD_LIBRARY_PATH="$CUDA_PATH/lib64:$LD_LIBRARY_PATH"
            CMAKE_ARGS="-DLLAMA_CUBLAS=ON -DLLAMA_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=53;62;72;87"
            ;;
        "raspberry_pi")
            CMAKE_ARGS="-DLLAMA_NATIVE=OFF -DLLAMA_OPENBLAS=ON"
            CMAKE_ARGS="$CMAKE_ARGS -DCMAKE_C_FLAGS='-march=armv8-a+crc+simd -mtune=cortex-a72'"
            CMAKE_ARGS="$CMAKE_ARGS -DCMAKE_CXX_FLAGS='-march=armv8-a+crc+simd -mtune=cortex-a72'"
            ;;
        "raspberry_pi_32")
            CMAKE_ARGS="-DLLAMA_NATIVE=OFF -DLLAMA_OPENBLAS=ON"
            CMAKE_ARGS="$CMAKE_ARGS -DCMAKE_C_FLAGS='-march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard'"
            CMAKE_ARGS="$CMAKE_ARGS -DCMAKE_CXX_FLAGS='-march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard'"
            ;;
        "arm64_linux")
            CMAKE_ARGS="-DLLAMA_NATIVE=ON -DLLAMA_OPENBLAS=ON"
            ;;
        "x86_64_linux")
            CMAKE_ARGS="-DLLAMA_NATIVE=ON -DLLAMA_OPENBLAS=ON -DLLAMA_AVX2=ON -DLLAMA_FMA=ON"
            ;;
    esac
    
    CMAKE_ARGS="$CMAKE_ARGS -DBUILD_SHARED_LIBS=ON -DCMAKE_POSITION_INDEPENDENT_CODE=ON"
    info "Build flags configured for $PLATFORM"
}

# Build Llama CPP with shared library support
build_llama_cpp() {
    log "Building Llama CPP..."
    
    cd lib/llama-cpp
    rm -rf build && mkdir -p build && cd build
    
    cmake .. $CMAKE_ARGS -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local
    
    local jobs=$(nproc)
    [[ $PLATFORM == "raspberry_pi"* ]] && jobs=$(( jobs < 2 ? 1 : 2 ))
    
    make -j$jobs
    sudo make install
    sudo ldconfig
    
    # Verify shared library
    if ldconfig -p | grep -q "libllama"; then
        log "✓ Llama shared library installed successfully"
    else
        error "Shared library installation failed"
        exit 1
    fi
    
    cd ../../..
}

# Setup Python environment
setup_python_env() {
    log "Setting up Python environment..."
    
    [[ ! -d "venv" ]] && python3 -m venv venv
    source venv/bin/activate
    
    pip install --upgrade pip wheel setuptools
    
    # Set environment for llama-cpp-python
    export LLAMA_CPP_LIB=/usr/local/lib/libllama.so
    export CMAKE_ARGS="$CMAKE_ARGS"
    export FORCE_CMAKE=1
    
    pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose
    pip install opencv-python pillow numpy scipy matplotlib
    
    [[ $PLATFORM == "raspberry_pi"* ]] && pip install picamera2 || true
}

# Test installation
test_installation() {
    log "Testing installation..."
    source venv/bin/activate
    
    python3 -c "
import llama_cpp
print('✓ llama-cpp-python imported successfully')
print(f'Version: {llama_cpp.__version__}')
import cv2, numpy as np
print('✓ Computer vision modules working')
"
}

# Main execution
main() {
    log "🚀 Starting Enhanced Brain-in-Jar Setup"
    
    detect_platform
    install_dependencies
    configure_build_flags
    build_llama_cpp
    setup_python_env
    test_installation
    
    log "🎉 Setup completed! Now creating enhanced modules..."
}

main "$@"