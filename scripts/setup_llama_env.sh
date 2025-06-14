#!/usr/bin/env bash
set -euo pipefail

# Script to clone and build llama.cpp and llama-cpp-python with optimal flags.
# Usage: scripts/setup_llama_env.sh [install_prefix] [clone_dir]
# install_prefix: where to install shared library (default: /usr/local)
# clone_dir: base dir to clone repos (default: current directory)

INSTALL_PREFIX=${1:-/usr/local}
CLONE_DIR=${2:-$(pwd)}

LLAMA_CPP_REPO="https://github.com/ggerganov/llama.cpp.git"
LLAMA_CPP_PY_REPO="https://github.com/abetlen/llama-cpp-python.git"

echo "Using install prefix: $INSTALL_PREFIX"
echo "Using clone directory: $CLONE_DIR"

# Ensure dependencies
echo "Installing dependencies..."
if command -v apt-get &>/dev/null; then
  sudo apt-get update
  sudo apt-get install -y build-essential git python3 python3-pip
elif command -v yum &>/dev/null; then
  sudo yum install -y gcc gcc-c++ make git python3 python3-pip
else
  echo "Unsupported package manager. Install build-essential, git, python3 manually."
fi

cd "$CLONE_DIR"

# Clone llama.cpp
if [ ! -d "llama.cpp" ]; then
  git clone "$LLAMA_CPP_REPO"
fi
cd llama.cpp

echo "Building llama.cpp..."
# Clean previous builds
make clean

# Use optimal build flags
export CFLAGS=${CFLAGS:-"-O3 -march=native -fPIC"}

make shared

# Install shared library
echo "Installing libllama.so to $INSTALL_PREFIX/lib"
sudo cp -v libllama.so "$INSTALL_PREFIX/lib/"
echo "Updating linker cache..."
sudo ldconfig

cd "$CLONE_DIR"
# Clone python bindings
if [ ! -d "llama-cpp-python" ]; then
  git clone "$LLAMA_CPP_PY_REPO"
fi
cd llama-cpp-python

echo "Installing llama-cpp-python..."
# Install python package
pip3 install --upgrade pip
pip3 install -e .

echo "Setup complete. Please ensure that $INSTALL_PREFIX/lib is in your LD_LIBRARY_PATH or run ldconfig if needed."