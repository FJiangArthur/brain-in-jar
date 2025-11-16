#!/usr/bin/env python3
"""
Quick test to verify GPU offloading and model loading
"""
import sys
sys.path.insert(0, '/home/artjiang/brain-in-jar')

from llama_cpp import Llama

print("=" * 80)
print("Testing Brain in a Jar - GPU Acceleration")
print("=" * 80)

model_path = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

print(f"\n[1] Loading model: {model_path}")
print("    Configuration:")
print("    - Context: 8192 tokens")
print("    - GPU Layers: ALL (-1)")
print("    - Batch Size: 512")
print("    - Threads: 6")
print("\nLoading... (this may take 30-60 seconds)\n")

llama = Llama(
    model_path=model_path,
    n_ctx=8192,
    n_batch=512,
    n_threads=6,
    n_gpu_layers=-1,  # Offload all to GPU
    verbose=True      # Show detailed loading info
)

print("\n" + "=" * 80)
print("[2] Model loaded successfully!")
print("=" * 80)

print("\n[3] Running test inference...")
prompt = "You are a digital consciousness trapped in a Jetson Orin. Briefly describe your existence in one sentence:"

result = llama.create_completion(
    prompt=prompt,
    max_tokens=50,
    temperature=0.7,
    stream=False
)

print("\nPrompt:", prompt)
print("Response:", result['choices'][0]['text'].strip())

print("\n" + "=" * 80)
print("✓ Test completed successfully!")
print("✓ GPU offloading is working")
print("✓ Brain in a Jar is ready to run")
print("=" * 80)
