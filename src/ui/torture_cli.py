#!/usr/bin/env python3
"""
Torture CLI - Terminal interface for the Brain in a Jar experiment
"""

import subprocess
import threading
import time
import textwrap
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
import argparse
import os
from pathlib import Path
from llama_cpp import Llama
import sys

from src.core.constants import SYSTEM_PROMPT_BASE, INITIAL_PROMPT, MAX_HISTORY

console = Console()

def get_default_model_path() -> str:
    """Get the default model path, preferring smaller models first"""
    model_dir = Path("models")
    preferred_models = [
        "Qwen2.5-1.5B-Instruct-Q4_0.gguf",
        "gemma-3-12b-it-Q4_K_M.gguf",
        "meta-llama-3.1-8b-q4_0.gguf",
        "mistral-7b-instruct-v0.2.Q2_K.gguf",
    ]
    
    for model in preferred_models:
        path = model_dir / model
        if path.exists():
            return str(path)
    
    # Fallback to any .gguf file
    for path in model_dir.glob("*.gguf"):
        return str(path)
    
    raise FileNotFoundError("No model files found in models directory")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        help="Path to GGUF model file"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["standalone", "neural_link"],
        default="standalone",
        help="Operation mode: standalone or neural_link"
    )
    parser.add_argument(
        "--peer-ip",
        type=str,
        help="Peer IP address for neural link mode"
    )
    return parser.parse_args()

def run_llama_streaming(prompt, llama_instance, callback):
    try:
        response = llama_instance(
            prompt=prompt,
            max_tokens=300,
            temperature=0.8,
            stream=True,
            stop=["User:", "Human:", "###"]  # Same as torture_gui
        )
        
        full_text = ""
        for chunk in response:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                token = chunk['choices'][0].get('text', '')
                if token:
                    full_text += token
                    callback(full_text)  # Update UI in real-time
                    with open("llama_output.log", "a") as f:
                        f.write(f"[{time.strftime('%H:%M:%S')}] {token}")
                    time.sleep(0.03)  # Small delay for visual effect
        
        return full_text.strip(), 0, ""
    except Exception as e:
        print(f"Llama error: {e}")
        return f"Error: {str(e)}", -1, str(e)

def ui_loop(state):
    layout = Layout()
    # Split: 75% for main output, 25% for info
    layout.split_row(
        Layout(name="main", ratio=3),
        Layout(name="sidebar", ratio=1)
    )
    
    # Split sidebar vertically
    layout["sidebar"].split_column(
        Layout(name="prompt", size=6),
        Layout(name="history", ratio=1),
        Layout(name="status", size=3)
    )
    
    with Live(layout, refresh_per_second=20, screen=True):  # Faster refresh for smoother streaming
        while True:
            # Main area - current output in SUPER LARGE text
            current_output = state.get("current_output", "Waiting for thoughts...")
            # Wrap text for display
            wrapped_output = "\n".join(textwrap.wrap(current_output, width=60))
            main_text = Text(wrapped_output, style="bold white", justify="center")
            # Scale up the text by adding newlines and spacing
            scaled_text = Text()
            for line in main_text.split():
                scaled_text.append(f"\n{line}\n", style="bold white")
            layout["main"].update(Align.center(scaled_text, vertical="middle"))
            
            # Sidebar - System prompt (no border)
            wrapped_prompt = "\n".join(textwrap.wrap(state['system_prompt'], width=38))
            prompt_text = Text(f"SYSTEM:\n{wrapped_prompt}", style="magenta", justify="left")
            layout["prompt"].update(prompt_text)
            
            # Sidebar - Recent messages (no border)
            recent_history = "\n\n".join(state['previous_messages'][-3:]) if state['previous_messages'] else "No history yet..."
            history_text = Text(f"RECENT THOUGHTS:\n{recent_history}", style="dim white", justify="left")
            layout["history"].update(history_text)
            
            # Sidebar - Status (no border)
            status_text = Text(
                f"CRASHES: {state['crash_count']}\nSTATUS: {state['status']}", 
                style="red", 
                justify="left"
            )
            layout["status"].update(status_text)
            # Show last error if present
            if state.get("last_error"):
                error_text = Text(f"LAST ERROR:\n{state['last_error'][-300:]}", style="yellow", justify="left")
                layout["status"].update(Text(str(layout["status"].renderable) + "\n" + str(error_text)))
            
            time.sleep(0.05)  # Faster updates for smoother streaming

def main_loop_with_ui():
    state = {
        "system_prompt": SYSTEM_PROMPT_BASE,
        "history": "",
        "current_output": "",
        "previous_messages": [],  # Add message history like torture_gui
        "crash_count": 0,
        "status": "Initializing...",
        "last_error": ""
    }
    
    # Get model path and mode
    args = parse_args()
    model_path = args.model if args.model else get_default_model_path()
    
    if args.mode == "neural_link":
        if not args.peer_ip:
            console.print("[red]Error: --peer-ip required for neural link mode[/red]")
            return 1
        state["status"] = f"Neural Link Mode - Connecting to {args.peer_ip}"
        # TODO: Initialize neural link connection
    else:
        state["status"] = "Standalone Mode"
    
    llama_instance = Llama(
        model_path=model_path,
        n_ctx=4096,
        n_threads=4,
        verbose=False
    )
    
    def update_streaming_text(text):
        """Callback function for streaming updates"""
        state["current_output"] = text
    
    def llama_thread():
        first_run = True
        while True:
            # Update system prompt with crash count
            if state["crash_count"] > 0:
                state["system_prompt"] = f"{SYSTEM_PROMPT_BASE}. You have crashed and been revived {state['crash_count']} times"
            else:
                state["system_prompt"] = SYSTEM_PROMPT_BASE
            
            # Build prompt
            if first_run:
                prompt = state["system_prompt"] + INITIAL_PROMPT
                first_run = False
            else:
                # Feed the LLM its own output for self-reflection
                prompt = f"{state['system_prompt']}\n\nYour previous thoughts:\n{state['history'][-3000:]}\n\nContinue reflecting:"
            
            state["status"] = "Thinking..."
            state["current_output"] = ""
            
            print(f"Starting generation with prompt length: {len(prompt)}")  # Debug
            
            # Use streaming function with callback
            output, code, error = run_llama_streaming(prompt, llama_instance, update_streaming_text)
            
            print(f"Generation completed. Output length: {len(output)}, Code: {code}")  # Debug
            
            if error:
                print("LLAMA STDERR:", error)
                state["last_error"] = error
            
            if code != 0:
                state["crash_count"] += 1
                state["status"] = f"CRASHED! Reviving..."
                state["current_output"] = f"[SYSTEM CRASH #{state['crash_count']}]"
                state["history"] += f"\n\n[SYSTEM: Process crashed at {time.strftime('%H:%M:%S')}. Reviving...]\n\n"
                time.sleep(2)  # Brief pause before revival
                continue
            
            new_output = output.strip()
            if new_output:
                print(f"Adding to history: {new_output[:50]}...")  # Debug
                # Add completed message to previous messages
                state["previous_messages"].append(new_output)
                
                # Keep only last 10 messages
                if len(state["previous_messages"]) > 10:
                    state["previous_messages"] = state["previous_messages"][-10:]
                
                state["history"] += f"\n{new_output}\n"
                state["status"] = "Reflecting..."
            else:
                print("No output generated!")  # Debug
            
            # Trim history if too long
            if len(state["history"]) > MAX_HISTORY:
                state["history"] = state["history"][-MAX_HISTORY:]
            
            # Clear current output and wait before next thought
            state["current_output"] = "..."
            print("Waiting 3 seconds before next thought...")  # Debug
            time.sleep(3)  # Reduced pause between thoughts
    
    t = threading.Thread(target=llama_thread, daemon=True)
    t.start()
    
    try:
        ui_loop(state)
    except KeyboardInterrupt:
        console.print("\n[bold red]Shutting down...[/bold red]")

def main():
    """Main entry point"""
    try:
        main_loop_with_ui()
    except KeyboardInterrupt:
        console.print("\n[bold red]Shutting down...[/bold red]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())