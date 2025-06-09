#!/bin/bash

# Download the model
huggingface-cli download google/gemma-3-1b-it-qat-q4_0-gguf --local-dir models

echo "Model downloaded to models/gemma-3-1b-it-q4_0.gguf"
