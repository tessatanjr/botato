#!/bin/bash
# ===================================================
# Script to install LLaMA 3 latest via Ollama CLI
# ===================================================

set -e  # Exit on any error

# Optional: Folder to store models (Ollama stores them internally too)
MODEL_DIR="models/llama3"
mkdir -p $MODEL_DIR

echo "Checking Ollama installation..."
if ! command -v ollama &> /dev/null
then
    echo "Ollama CLI not found. Please install Ollama first: https://ollama.com"
    exit 1
fi

echo "Pulling LLaMA 3 latest model..."
ollama pull llama3:latest

echo "LLaMA 3 model installed successfully!"
echo "You can now test it via:"
echo "  ollama run llama3:latest"
echo "Or run Ollama server:"
echo "  ollama serve"
