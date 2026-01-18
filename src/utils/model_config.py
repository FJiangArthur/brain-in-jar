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
            # Check if on Jetson (unified memory architecture)
            if os.path.exists('/etc/nv_tegra_release'):
                # Jetson devices use unified memory - estimate available GPU memory
                # Use 80% of system RAM as available for GPU operations
                system_ram_gb = self.system_memory_gb
                estimated_gpu_mb = int(system_ram_gb * 1024 * 0.8)
                print(f"  [Jetson Unified Memory] Estimating {estimated_gpu_mb} MB available for GPU")
                return estimated_gpu_mb

            # Standard NVIDIA GPU with dedicated memory
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                memory_str = result.stdout.strip()
                if memory_str != '[N/A]':
                    return int(float(memory_str))
            return 0
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, Exception):
            return 0

    def _get_system_memory(self):
        """Get total system memory in GB"""
        try:
            return psutil.virtual_memory().total / (1024**3)
        except Exception:
            return 8.0  # Default fallback

    def get_optimal_config(self, model_size_gb=None, conservative=True, concurrent_models=1, matrix_role=None):
        """
        Get optimal model configuration

        Args:
            model_size_gb: Approximate model size in GB (auto-detect if None)
            conservative: Use conservative settings to prevent OOM (default True)
            concurrent_models: Number of models running simultaneously (1-3)
            matrix_role: For matrix mode, instance role ('subject', 'observer', 'god')

        Returns:
            dict: Configuration parameters for llama-cpp-python
        """
        # Use Jetson-specific preset if detected
        if os.path.exists('/etc/nv_tegra_release'):
            return self.get_jetson_orin_config(concurrent_models=concurrent_models, matrix_role=matrix_role)

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

    def get_jetson_orin_config(self, concurrent_models=1, matrix_role=None):
        """
        Get optimized config for Jetson Orin AGX

        Args:
            concurrent_models: Number of models running simultaneously (1-3)
                1 = single/isolated mode
                2 = peer mode
                3 = matrix mode (Subject/Observer/GOD)
            matrix_role: For matrix mode, specify role ('subject', 'observer', 'god')
                to allocate GPU layers hierarchically
        """
        print(f"\n[ModelConfig] Using Jetson Orin AGX preset (concurrent_models={concurrent_models})")

        # Adjust GPU layers based on how many models will be loaded
        if concurrent_models >= 3:
            # Matrix mode: 3 models - use CPU-only to avoid OOM on Jetson
            # The Jetson Orin has 12 CPU cores and plenty of RAM for 3 models
            gpu_layers = 0  # CPU-only for all instances in matrix mode
            print(f"  [Matrix Mode] Using {gpu_layers} GPU layers (CPU-only for stability with 3 models)")
            print(f"  [Matrix Mode] Role: {matrix_role.upper() if matrix_role else 'UNKNOWN'}")
        elif concurrent_models == 2:
            # Peer mode: 2 models - moderate GPU usage
            gpu_layers = 12  # ~12 layers per model = ~24 total
            print(f"  [Peer Mode] Using {gpu_layers} GPU layers to support 2 concurrent models")
        else:
            # Single model: can use more GPU layers
            gpu_layers = 25  # Maximum for single model
            print(f"  [Single Mode] Using {gpu_layers} GPU layers for single model")

        return {
            'n_ctx': 2048,         # Conservative context
            'n_batch': 256,        # Moderate batch size
            'n_threads': 6,        # 6 of 12 cores
            'n_gpu_layers': gpu_layers,
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
