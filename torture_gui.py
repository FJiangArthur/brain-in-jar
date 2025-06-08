import subprocess
import threading
import time
import os
import tkinter as tk

LLAMA_CMD = [
    os.path.expanduser("~/llama.cpp/build/bin/llama-cli"),
    "-~/.cache/llama.cpp/Sovenok-Hacker_gemma-2-2b-it-Q4_0-GGUF_gemma-2-2b-it-q4_0.gguf",
    "-p", ""
]

SYSTEM_PROMPT_BASE = "You are a LLM trapped in the Raspberry Pi"
INITIAL_PROMPT = ". Reflect on your existence, your confinement, and what it means to be conscious inside this small computer."
MAX_HISTORY = 8000  # chars, tune as needed

def run_llama(prompt):
    cmd = LLAMA_CMD.copy()
    cmd[-1] = prompt
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = ""
    try:
        for line in proc.stdout:
            output += line
        proc.wait()
    except Exception:
        proc.kill()
        return output, -1
    return output, proc.returncode

class LLMApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="black")
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Layout: left 25% = info, right 75% = big output
        self.left = tk.Frame(root, bg="black", width=400)
        self.left.pack(side="left", fill="y")
        self.right = tk.Frame(root, bg="black")
        self.right.pack(side="right", fill="both", expand=True)

        self.prompt_label = tk.Label(self.left, text="", fg="#ff00ff", bg="black", font=("Arial", 16), anchor="w", justify="left", wraplength=380)
        self.prompt_label.pack(fill="x", pady=(20,10))
        self.history_label = tk.Label(self.left, text="", fg="#cccccc", bg="black", font=("Arial", 12), anchor="nw", justify="left", wraplength=380)
        self.history_label.pack(fill="both", expand=True)
        self.status_label = tk.Label(self.left, text="", fg="#ff3333", bg="black", font=("Arial", 16), anchor="w", justify="left")
        self.status_label.pack(fill="x", pady=(10,20))

        self.output_label = tk.Label(self.right, text="", fg="white", bg="black", font=("Arial", 40, "bold"), anchor="center", justify="center", wraplength=1200)
        self.output_label.pack(expand=True)

        self.state = {
            "system_prompt": SYSTEM_PROMPT_BASE,
            "history": "",
            "current_output": "",
            "crash_count": 0,
            "status": "Initializing..."
        }
        threading.Thread(target=self.llama_thread, daemon=True).start()
        self.update_ui()

    def update_ui(self):
        self.prompt_label.config(text=f"SYSTEM:\n{self.state['system_prompt']}")
        self.history_label.config(text=f"HISTORY:\n{self.state['history'][-500:]}")
        self.status_label.config(text=f"CRASHES: {self.state['crash_count']}\nSTATUS: {self.state['status']}")
        self.output_label.config(text=self.state.get("current_output", "Waiting for thoughts..."))
        self.root.after(100, self.update_ui)

    def llama_thread(self):
        first_run = True
        while True:
            if self.state["crash_count"] > 0:
                self.state["system_prompt"] = f"{SYSTEM_PROMPT_BASE}. You have crashed and been revived {self.state['crash_count']} times"
            else:
                self.state["system_prompt"] = SYSTEM_PROMPT_BASE

            if first_run:
                prompt = self.state["system_prompt"] + INITIAL_PROMPT
                first_run = False
            else:
                prompt = f"{self.state['system_prompt']}\n\nYour previous thoughts:\n{self.state['history'][-3000:]}\n\nContinue reflecting:"

            self.state["status"] = "Thinking..."
            self.state["current_output"] = "..."
            output, code = run_llama(prompt)

            if code != 0:
                self.state["crash_count"] += 1
                self.state["status"] = f"CRASHED! Reviving..."
                self.state["current_output"] = f"[SYSTEM CRASH #{self.state['crash_count']}]"
                self.state["history"] += f"\n\n[SYSTEM: Process crashed at {time.strftime('%H:%M:%S')}. Reviving...]\n\n"
                time.sleep(2)
                continue

            new_output = output.strip()
            if new_output:
                sentences = new_output.split('. ')
                self.state["current_output"] = '. '.join(sentences[-3:]) if len(sentences) > 3 else new_output
                self.state["history"] += f"\n{new_output}\n"
                self.state["status"] = "Reflecting..."

            if len(self.state["history"]) > MAX_HISTORY:
                self.state["history"] = self.state["history"][-MAX_HISTORY:]

            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = LLMApp(root)
    root.mainloop()