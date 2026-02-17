#!/bin/bash
# download_llama2_models.sh
# Requires: Python + huggingface_hub installed
# Must have HUGGINGFACE_TOKEN exported

set -e

echo "Starting LLaMA 2 models download..."

# Create model directories
mkdir -p models/llama2/7B
mkdir -p models/llama2/13B

# Function to download a model
download_model() {
    MODEL_NAME=$1
    TARGET_DIR=$2
    echo "Downloading $MODEL_NAME to $TARGET_DIR ..."
    python - <<END
from huggingface_hub import snapshot_download
import os

os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_TOKEN"] = os.environ.get("HUGGINGFACE_TOKEN")

snapshot_download(
    repo_id="$MODEL_NAME",
    cache_dir="$TARGET_DIR",
    revision="main",
    local_files_only=False
)
END
}

# LLaMA 2 7B Chat HF
download_model "meta-llama/Llama-2-7b-chat-hf" "models/llama2/7B"

# LLaMA 2 13B Chat HF
# download_model "meta-llama/Llama-2-13b-chat-hf" "models/llama2/13B"

echo "Download complete for both 7B and 13B!"
