#!/usr/bin/env python3
"""
GPU Memory Watchdog
Monitors GPU memory usage and kills the process before OOM crashes the system
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

class GPUMemoryWatchdog:
    """Monitor GPU memory and kill process if approaching limits"""

    def __init__(self, threshold_percent=85, check_interval=2, pid=None, system_ram_threshold=85):
        """
        Initialize GPU watchdog

        Args:
            threshold_percent: Kill process when GPU memory exceeds this % (default 85%)
            check_interval: Base check interval in seconds (default 2s, adaptive to 1s when >70%)
            pid: Process ID to monitor (default: current process)
            system_ram_threshold: Kill process when system RAM exceeds this % (default 85%)
        """
        self.threshold_percent = threshold_percent
        self.base_check_interval = check_interval
        self.current_check_interval = check_interval
        self.system_ram_threshold = system_ram_threshold
        self.pid = pid or os.getpid()
        self.running = True
        self.monitoring_thread = None
        self.gpu_available = self._check_gpu_availability()

        # Spike detection
        self.last_gpu_usage = -1
        self.last_sys_usage = -1

    def _check_gpu_availability(self):
        """Check if GPU/nvidia-smi is available"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and result.stdout.strip() != '[N/A]'
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return False

    def get_gpu_memory_usage(self):
        """
        Get GPU memory usage percentage

        Returns:
            float: GPU memory usage percentage (0-100)
            Returns -1 if GPU not available
        """
        if not self.gpu_available:
            return -1

        try:
            # Get memory usage
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used,memory.total',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0 or '[N/A]' in result.stdout:
                return -1

            output = result.stdout.strip()
            if not output:
                return -1

            # Parse: "used, total"
            parts = output.split(',')
            if len(parts) < 2:
                return -1

            used = float(parts[0].strip())
            total = float(parts[1].strip())

            if total == 0:
                return -1

            return (used / total) * 100

        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, Exception) as e:
            print(f"GPU memory check failed: {e}", file=sys.stderr)
            return -1

    def get_system_memory_usage(self):
        """Get system RAM usage percentage"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()

            mem_info = {}
            for line in lines:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().split()[0]
                    mem_info[key] = int(value)

            total = mem_info.get('MemTotal', 0)
            available = mem_info.get('MemAvailable', 0)

            if total == 0:
                return -1

            used = total - available
            return (used / total) * 100

        except Exception as e:
            print(f"System memory check failed: {e}", file=sys.stderr)
            return -1

    def _monitoring_loop(self):
        """Background monitoring loop with adaptive intervals and spike detection"""
        print(f"[GPU Watchdog] Starting monitoring (PID: {self.pid}, GPU threshold: {self.threshold_percent}%, RAM threshold: {self.system_ram_threshold}%)")

        while self.running:
            try:
                gpu_usage = self.get_gpu_memory_usage()
                sys_usage = self.get_system_memory_usage()

                # Spike detection
                if self.last_gpu_usage >= 0 and gpu_usage >= 0:
                    gpu_spike = gpu_usage - self.last_gpu_usage
                    if gpu_spike > 10:
                        print(f"[GPU Watchdog] ⚠️  GPU memory spike detected: +{gpu_spike:.1f}%", file=sys.stderr)

                if self.last_sys_usage >= 0 and sys_usage >= 0:
                    sys_spike = sys_usage - self.last_sys_usage
                    if sys_spike > 10:
                        print(f"[GPU Watchdog] ⚠️  System RAM spike detected: +{sys_spike:.1f}%", file=sys.stderr)

                # Update last readings
                self.last_gpu_usage = gpu_usage
                self.last_sys_usage = sys_usage

                # Adaptive monitoring: switch to 1-second checks when >70% usage
                max_usage = max(gpu_usage if gpu_usage >= 0 else 0, sys_usage)
                if max_usage > 70:
                    self.current_check_interval = 1.0
                else:
                    self.current_check_interval = self.base_check_interval

                # Log current usage
                interval_indicator = "⚡" if self.current_check_interval == 1.0 else "  "
                if gpu_usage >= 0:
                    print(f"{interval_indicator}[GPU Watchdog] GPU: {gpu_usage:.1f}% | System RAM: {sys_usage:.1f}%")
                else:
                    print(f"{interval_indicator}[GPU Watchdog] GPU not available | System RAM: {sys_usage:.1f}%")

                # Check GPU threshold
                if gpu_usage >= self.threshold_percent:
                    print(f"\n[GPU Watchdog] ⚠️  CRITICAL: GPU memory at {gpu_usage:.1f}%", file=sys.stderr)
                    print(f"[GPU Watchdog] 🛑 Killing process {self.pid} to prevent OOM crash", file=sys.stderr)
                    self._kill_process()
                    return

                # Check system RAM threshold
                if sys_usage >= self.system_ram_threshold:
                    print(f"\n[GPU Watchdog] ⚠️  CRITICAL: System RAM at {sys_usage:.1f}%", file=sys.stderr)
                    print(f"[GPU Watchdog] 🛑 Killing process {self.pid} to prevent system crash", file=sys.stderr)
                    self._kill_process()
                    return

                time.sleep(self.current_check_interval)

            except Exception as e:
                print(f"[GPU Watchdog] Error in monitoring loop: {e}", file=sys.stderr)
                time.sleep(self.current_check_interval)

    def _kill_process(self):
        """Kill the monitored process"""
        try:
            os.kill(self.pid, signal.SIGTERM)
            time.sleep(2)

            # If still alive, force kill
            try:
                os.kill(self.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already dead

        except ProcessLookupError:
            print(f"[GPU Watchdog] Process {self.pid} already terminated")
        except Exception as e:
            print(f"[GPU Watchdog] Error killing process: {e}", file=sys.stderr)

    def start(self):
        """Start background monitoring"""
        if not self.running:
            return

        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="GPUWatchdog"
        )
        self.monitoring_thread.start()

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)


def test_watchdog():
    """Test the watchdog functionality"""
    print("Testing GPU Watchdog...")

    watchdog = GPUMemoryWatchdog(threshold_percent=85, check_interval=2)

    gpu_usage = watchdog.get_gpu_memory_usage()
    sys_usage = watchdog.get_system_memory_usage()

    print(f"\nCurrent Status:")
    if gpu_usage >= 0:
        print(f"  GPU Memory: {gpu_usage:.1f}%")
    else:
        print(f"  GPU: Not available")
    print(f"  System RAM: {sys_usage:.1f}%")

    print(f"\nWatchdog will kill process if:")
    print(f"  - GPU memory exceeds {watchdog.threshold_percent}%")
    print(f"  - System RAM exceeds 90%")
    print(f"\nStarting 10-second monitoring test...")

    watchdog.start()
    time.sleep(10)
    watchdog.stop()

    print("Test complete!")


if __name__ == '__main__':
    test_watchdog()
