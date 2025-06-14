#!/usr/bin/env python3
"""
CLI Interface for Brain in a Jar - A Dystopian AI Experiment
"""

import os
import sys
import time
from typing import List, Dict, Optional
from pathlib import Path

from llama_cpp import Llama
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core.constants import SYSTEM_PROMPT_BASE, INITIAL_PROMPT, MAX_HISTORY
from src.utils.conversation_logger import ConversationLogger

# Initialize Rich console
console = Console()

def get_default_model_path() -> str:
    """Get the default model path, preferring smaller models first"""
    model_dir = Path("models")
    preferred_models = [
        "gemma-2-2b-it-q4_0.gguf",
        "gemma-2-2b-it-Q4_K_M.gguf",
        "gemma-2-2b-it-Q4_0.gguf",
        "gemma-2-2b-it.gguf",
        "gemma-2-2b-it-Q4_K.gguf",
        "gemma-2-2b-it-Q5_K_M.gguf",
        "gemma-2-2b-it-Q5_0.gguf",
        "gemma-2-2b-it-Q5_K.gguf",
        "gemma-2-2b-it-Q6_K.gguf",
        "gemma-2-2b-it-Q8_0.gguf",
        "gemma-2-2b-it-f16.gguf",
        "gemma-2-2b-it-f32.gguf",
    ]
    
    for model in preferred_models:
        path = model_dir / model
        if path.exists():
            return str(path)
    
    # Fallback to any .gguf file
    for path in model_dir.glob("*.gguf"):
        return str(path)
    
    raise FileNotFoundError("No model files found in models directory")

def main_loop_with_ui():
    """Main interaction loop with enhanced UI"""
    # Get model path
    model_path = get_default_model_path()
    if not model_path:
        console.print("[red]No model file found. Please place a .gguf model file in the models directory.[/red]")
        return

    # Initialize model
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing AI...", total=None)
        try:
            llama_instance = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=4,
                n_batch=512,
                verbose=False
            )
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]Error initializing model: {str(e)}[/red]")
            return

    # Initialize conversation logger
    logger = ConversationLogger()

    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="system", ratio=1),
        Layout(name="chat", ratio=2)
    )

    # Initialize conversation state
    conversation_history: List[Dict[str, str]] = []
    current_prompt = INITIAL_PROMPT
    system_prompt = SYSTEM_PROMPT_BASE

    def update_display():
        """Update the display with current state"""
        # Header
        header = Table.grid(padding=1)
        header.add_column(style="bold cyan")
        header.add_row("🤖 Brain in a Jar - Dystopian AI Experiment")
        layout["header"].update(header)

        # System prompt panel
        system_panel = Panel(
            Text(system_prompt, style="dim"),
            title="System Prompt",
            border_style="blue"
        )
        layout["system"].update(system_panel)

        # Chat history
        chat_table = Table.grid(padding=1)
        chat_table.add_column("Role", style="bold")
        chat_table.add_column("Message", style="white")

        for msg in conversation_history[-MAX_HISTORY:]:
            role = "🤖" if msg["role"] == "assistant" else "👤"
            chat_table.add_row(role, msg["content"])

        layout["chat"].update(chat_table)

        # Footer
        footer = Table.grid(padding=1)
        footer.add_column(style="bold yellow")
        footer.add_row("Type 'exit' to quit, 'reset' to start over")
        layout["footer"].update(footer)

    # Main interaction loop
    with Live(layout, refresh_per_second=4) as live:
        while True:
            update_display()
            
            # Get user input
            user_input = Prompt.ask("\nYou")
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'reset':
                conversation_history = []
                current_prompt = INITIAL_PROMPT
                continue

            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Prepare messages for the model
            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history
            ]

            # Get AI response
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("AI is thinking...", total=None)
                try:
                    response = llama_instance.create_chat_completion(
                        messages=messages,
                        max_tokens=512,
                        temperature=0.7,
                        stop=["User:", "\n\n"]
                    )
                    progress.update(task, completed=True)
                except Exception as e:
                    console.print(f"[red]Error getting response: {str(e)}[/red]")
                    continue

            # Extract and process response
            if response and 'choices' in response and len(response['choices']) > 0:
                ai_response = response['choices'][0]['message']['content'].strip()
                conversation_history.append({"role": "assistant", "content": ai_response})
                
                # Log the interaction
                logger.log_interaction(user_input, ai_response)
            else:
                console.print("[red]Error: No valid response from AI[/red]")

def main():
    """Main entry point"""
    try:
        main_loop_with_ui()
    except KeyboardInterrupt:
        console.print("\n[yellow]Experiment terminated by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())