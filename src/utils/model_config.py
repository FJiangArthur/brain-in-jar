#!/usr/bin/env python3
"""
Smart Model Configuration
Automatically determines optimal model settings based on available resources
"""

import subprocess
import psutil
import os


class ModelConfig:
    """Generate optimal model configuration for available hardware"""

    def __init__(self):
        self.gpu_available = self._check_gpu()
        self.gpu_memory_mb = self._get_gpu_memory() if self.gpu_available else 0
        self.system_memory_gb = self._get_system_memory()
        self.cpu_cores = os.cpu_count() or 4

    def _check_gpu(self):
        """Check if CUDA GPU is available"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and result.stdout.strip() != '[N/A]'
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return False

    def _get_gpu_memory(self):
        """Get total GPU memory in MB"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return int(float(result.stdout.strip()))
            return 0
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, Exception):
            return 0

    def _get_system_memory(self):
        """Get total system memory in GB"""
        try:
            return psutil.virtual_memory().total / (1024**3)
        except Exception:
            return 8.0  # Default fallback

    def get_optimal_config(self, model_size_gb=None, conservative=True):
        """
        Get optimal model configuration

        Args:
            model_size_gb: Approximate model size in GB (auto-detect if None)
            conservative: Use conservative settings to prevent OOM (default True)

        Returns:
            dict: Configuration parameters for llama-cpp-python
        """
        config = {
            'n_ctx': 2048,        # Context window
            'n_batch': 256,       # Batch size
            'n_threads': 4,       # CPU threads
            'n_gpu_layers': 0,    # GPU layers (0 = CPU only)
            'verbose': True,      # Show initialization info
            'use_mmap': True,     # Use memory mapping
            'use_mlock': False,   # Don't lock memory (causes issues on Jetson)
        }

        print(f"\n[ModelConfig] System Resources:")
        print(f"  GPU: {'Available' if self.gpu_available else 'Not available'}")
        if self.gpu_available:
            print(f"  GPU Memory: {self.gpu_memory_mb} MB ({self.gpu_memory_mb/1024:.1f} GB)")
        print(f"  System RAM: {self.system_memory_gb:.1f} GB")
        print(f"  CPU Cores: {self.cpu_cores}")

        # Determine GPU layers based on available GPU memory
        if self.gpu_available and self.gpu_memory_mb > 0:
            if conservative:
                # Conservative: Use only 60% of GPU memory
                if self.gpu_memory_mb >= 16000:  # 16GB+ GPU
                    config['n_gpu_layers'] = 25  # Partial offload
                    config['n_ctx'] = 4096
                    config['n_batch'] = 512
                elif self.gpu_memory_mb >= 8000:  # 8GB+ GPU
                    config['n_gpu_layers'] = 15  # Partial offload
                    config['n_ctx'] = 2048
                    config['n_batch'] = 256
                elif self.gpu_memory_mb >= 4000:  # 4GB+ GPU
                    config['n_gpu_layers'] = 8   # Minimal offload
                    config['n_ctx'] = 2048
                    config['n_batch'] = 128
                else:
                    # Less than 4GB - CPU only
                    config['n_gpu_layers'] = 0
                    config['n_ctx'] = 1024
                    config['n_batch'] = 128
            else:
                # Aggressive: Use more GPU memory
                if self.gpu_memory_mb >= 16000:
                    config['n_gpu_layers'] = 35
                    config['n_ctx'] = 8192
                    config['n_batch'] = 512
                elif self.gpu_memory_mb >= 8000:
                    config['n_gpu_layers'] = 25
                    config['n_ctx'] = 4096
                    config['n_batch'] = 512
                elif self.gpu_memory_mb >= 4000:
                    config['n_gpu_layers'] = 15
                    config['n_ctx'] = 2048
                    config['n_batch'] = 256
                else:
                    config['n_gpu_layers'] = 8
                    config['n_ctx'] = 2048
                    config['n_batch'] = 128

        # Optimize CPU threads based on available cores
        if self.cpu_cores >= 12:
            config['n_threads'] = 6  # Use half the cores
        elif self.cpu_cores >= 8:
            config['n_threads'] = 4
        elif self.cpu_cores >= 4:
            config['n_threads'] = 2
        else:
            config['n_threads'] = 1

        # Adjust based on system RAM
        if self.system_memory_gb < 8:
            # Low RAM - be very conservative
            config['n_ctx'] = min(config['n_ctx'], 1024)
            config['n_batch'] = min(config['n_batch'], 128)
        elif self.system_memory_gb >= 32:
            # High RAM - can be more generous
            config['n_ctx'] = max(config['n_ctx'], 2048)

        print(f"\n[ModelConfig] Recommended Configuration:")
        print(f"  Context Window: {config['n_ctx']}")
        print(f"  Batch Size: {config['n_batch']}")
        print(f"  CPU Threads: {config['n_threads']}")
        if self.gpu_available:
            print(f"  GPU Layers: {config['n_gpu_layers']}")
            if config['n_gpu_layers'] > 0:
                print(f"  Mode: Hybrid CPU+GPU (Conservative)")
            else:
                print(f"  Mode: CPU Only")
        else:
            print(f"  Mode: CPU Only (No GPU detected)")

        return config

    def get_jetson_orin_config(self):
        """Get optimized config for Jetson Orin AGX"""
        print("\n[ModelConfig] Using Jetson Orin AGX preset")

        return {
            'n_ctx': 2048,         # Conservative context
            'n_batch': 256,        # Moderate batch size
            'n_threads': 6,        # 6 of 12 cores
            'n_gpu_layers': 20,    # Hybrid: ~20 layers on GPU, rest on CPU
            'verbose': True,
            'use_mmap': True,
            'use_mlock': False,    # Don't lock memory
        }

    def print_recommendation(self):
        """Print configuration recommendation"""
        config = self.get_optimal_config(conservative=True)
        print("\n" + "="*60)
        print("RECOMMENDED MODEL CONFIGURATION")
        print("="*60)
        for key, value in config.items():
            print(f"  {key:20s} = {value}")
        print("="*60)


def main():
    """Test model configuration detection"""
    config = ModelConfig()
    config.print_recommendation()

    print("\n\nJetson Orin AGX Preset:")
    jetson_config = config.get_jetson_orin_config()
    for key, value in jetson_config.items():
        print(f"  {key:20s} = {value}")


if __name__ == '__main__':
    main()
