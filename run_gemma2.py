import os
import shutil
import argparse
import sys
from llama_cpp import Llama

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str, default="./some_local_gemma2.bin",
                        help="Path to the local/hypothetical gemma2 model to copy.")
    parser.add_argument("--dst", type=str, default="./models/gemma2.bin",
                        help="Where to place the model.")
    parser.add_argument("--prompt", type=str, default="Hello, how are you?",
                        help="Prompt to query the model.")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.dst), exist_ok=True)

    if not os.path.exists(args.src):
        sys.exit(f"[Simulated Download Error] Model source not found: {args.src}")

    shutil.copyfile(args.src, args.dst)
    print("Copied the gemma2 model to", args.dst)

    try:
        llama = Llama(model_path=args.dst)
        output = llama(args.prompt)
        text = output.get("choices", [])[0].get("text", "")
        print("Prompt:", args.prompt)
        print("LLM Output:", text)
    except Exception as e:
        print("[Error]", e)

if __name__ == "__main__":
    main()

