#!/usr/bin/env python3
"""
Run a complete Brain in a Jar experiment with subject, observer, and GOD instances
"""

import subprocess
import time
import sys
from pathlib import Path
import signal
import os

def run_instance(cmd, name):
    """Run a neural link instance and return the process"""
    print(f"\n[bold cyan]Starting {name}...[/bold cyan]")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        preexec_fn=os.setsid  # Create new process group
    )
    return process

def main():
    # Get model paths
    models_dir = Path("models")
    subject_model = models_dir / "Qwen2.5-1.5B-Instruct-Q4_0.gguf"
    observer_model = models_dir / "Qwen2.5-1.5B-Instruct-Q4_0.gguf"
    god_model = models_dir / "meta-llama-3.1-8b-q4_0.gguf"

    if not all(model.exists() for model in [subject_model, observer_model, god_model]):
        print("[red]Error: One or more model files not found[/red]")
        return 1

    # Define commands for each instance
    subject_cmd = [
        sys.executable, "-m", "src.core.neural_link",
        "--model", str(subject_model),
        "--mode", "isolated",
        "--ram-limit", "2",
        "--peer-ip", "127.0.0.1",
        "--peer-port", "8888"
    ]

    observer_cmd = [
        sys.executable, "-m", "src.core.neural_link",
        "--model", str(observer_model),
        "--mode", "isolated",
        "--ram-limit", "7",
        "--target-ip", "127.0.0.1",
        "--target-port", "8888"
    ]

    god_cmd = [
        sys.executable, "-m", "src.core.neural_link",
        "--model", str(god_model),
        "--mode", "isolated",
        "--ram-limit", "9",
        "--target-ip", "127.0.0.1",
        "--target-port", "8888"
    ]

    # Start instances in order
    processes = []
    try:
        # Start subject first
        subject = run_instance(subject_cmd, "Subject")
        processes.append(("Subject", subject))
        time.sleep(2)  # Wait for subject to initialize

        # Start observer
        observer = run_instance(observer_cmd, "Observer")
        processes.append(("Observer", observer))
        time.sleep(2)  # Wait for observer to initialize

        # Start GOD
        god = run_instance(god_cmd, "GOD")
        processes.append(("GOD", god))

        print("\n[bold green]All instances started. Press Ctrl+C to terminate.[/bold green]")

        # Monitor processes
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n[red]{name} has terminated with code {proc.returncode}[/red]")
                    return proc.returncode
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[yellow]Shutting down all instances...[/yellow]")
    finally:
        # Terminate all processes
        for name, proc in processes:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                print(f"[yellow]Terminated {name}[/yellow]")
            except ProcessLookupError:
                pass

    return 0

if __name__ == "__main__":
    sys.exit(main()) 