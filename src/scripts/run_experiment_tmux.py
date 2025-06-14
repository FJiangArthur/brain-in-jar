#!/usr/bin/env python3
"""
Run a complete Brain in a Jar experiment in a tmux session with three panes
"""

import subprocess
import sys
from pathlib import Path
import time

def run_tmux_session():
    # Get model paths
    models_dir = Path("models")
    subject_model = models_dir / "Qwen2.5-1.5B-Instruct-Q4_0.gguf"
    observer_model = models_dir / "Qwen2.5-1.5B-Instruct-Q4_0.gguf"
    god_model = models_dir / "meta-llama-3.1-8b-q4_0.gguf"

    if not all(model.exists() for model in [subject_model, observer_model, god_model]):
        print("[red]Error: One or more model files not found[/red]")
        return 1

    # Create tmux session
    session_name = "brain_in_jar"
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name])

    # Split window into three panes
    subprocess.run(["tmux", "split-window", "-v", "-t", session_name])
    subprocess.run(["tmux", "split-window", "-h", "-t", session_name + ":0.1"])

    # Use venv's Python directly
    venv_python = Path("venv/bin/python").absolute()

    # Define commands for each instance
    subject_cmd = f"echo 'Starting Subject...' && {venv_python} -m src.core.neural_link --model {subject_model} --mode isolated --ram-limit 2 --peer-ip 127.0.0.1 --peer-port 8888"
    observer_cmd = f"echo 'Starting Observer...' && {venv_python} -m src.core.neural_link --model {observer_model} --mode isolated --ram-limit 7 --target-ip 127.0.0.1 --target-port 8888"
    god_cmd = f"echo 'Starting GOD...' && {venv_python} -m src.core.neural_link --model {god_model} --mode isolated --ram-limit 9 --target-ip 127.0.0.1 --target-port 8888"

    # Send commands to each pane
    subprocess.run(["tmux", "send-keys", "-t", session_name + ":0.0", god_cmd, "C-m"])
    subprocess.run(["tmux", "send-keys", "-t", session_name + ":0.1", subject_cmd, "C-m"])
    subprocess.run(["tmux", "send-keys", "-t", session_name + ":0.2", observer_cmd, "C-m"])

    # Attach to the session
    subprocess.run(["tmux", "attach-session", "-t", session_name])

    return 0

if __name__ == "__main__":
    sys.exit(run_tmux_session()) 