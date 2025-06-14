#!/usr/bin/env python3
"""
Simple Llama GUI - Basic interface for Llama model interaction
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from llama_cpp import Llama
import argparse
import os

from ..utils.conversation_logger import ConversationLogger

DEFAULT_MODEL = os.environ.get('DEFAULT_LLAMA_MODEL', './models/gemma2.bin')

class LlamaGUI:
    def __init__(self, root, model_path):
        self.root = root
        self.root.title('Llama-Cpp GUI')
        self.model = None
        if model_path:
            self.model = Llama(model_path=model_path)
        else:
            if os.path.exists(DEFAULT_MODEL):
                self.model = Llama(model_path=DEFAULT_MODEL)

        self.prompt_label = None
        self.prompt_entry = None
        self.submit_button = None
        self.output_text = None
        self.setup_ui()

    def setup_ui(self):
        self.prompt_label = tk.Label(self.root, text='Enter prompt:')
        self.prompt_label.pack()
        self.prompt_entry = tk.Entry(self.root, width=80)
        self.prompt_entry.pack()

        self.submit_button = tk.Button(self.root, text='Submit', command=self.run_model)
        self.submit_button.pack()

        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack()

    def run_model(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            return
        self.output_text.insert(tk.END, f"\nUser: {prompt}\n")
        self.output_text.see(tk.END)
        self.root.update()

        if not self.model:
            self.output_text.insert(tk.END, '[Error] Model not loaded. Provide a valid --model path.\n')
            self.output_text.see(tk.END)
            return

        output = self.model(
            prompt=prompt,
            max_tokens=100,
            stop=['\n'],
            stream=False
        )
        content = ''
        if 'choices' in output and len(output['choices']) > 0:
            content = output['choices'][0].get('text', '')

        self.output_text.insert(tk.END, f"LLM: {content}\n")
        self.output_text.see(tk.END)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str,
                        help='Path to llama model (e.g. ./models/gemma2.bin)')
    args = parser.parse_args()

    root = tk.Tk()
    gui = LlamaGUI(root, args.model)
    root.mainloop()

if __name__ == '__main__':
    main()
