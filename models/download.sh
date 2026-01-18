#!/bin/bash

# Download the model
#huggingface-cli download google/gemma-3-1b-it-qat-q4_0-gguf --local-dir models
wget https://huggingface.co/tensorblock/gemma-3-12b-it-GGUF/resolve/main/gemma-3-12b-it-Q4_K_M.gguf
echo "Model downloaded to models/gemma-3-1b-it-q4_0.gguf"

wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q2_K.gguf
echo "Mistral model downloaded to models/mistral-7b-instruct-v0.2.Q2_K.gguf"

wget https://huggingface.co/kaetemi/Meta-Llama-3.1-8B-Q4_0-GGUF/resolve/main/meta-llama-3.1-8b-q4_0.gguf
echo "Llama model downloaded to models/meta-llama-3.1-8b-q4_0.gguf" 
