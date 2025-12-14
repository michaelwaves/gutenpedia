#!/bin/bash

# start-local-inference.sh
# Start the Neuronpedia inference server locally with various model configurations
# TOKEN_LIMIT=400 ./start-local-inference.sh gemma-9b-it
# 512 had OOM on a100-40gb

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INFERENCE_DIR="inference"
DEFAULT_PORT=5002
DEFAULT_MODEL="gemma-9b-it"

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect available device
detect_device() {
    if command_exists nvidia-smi && nvidia-smi >/dev/null 2>&1; then
        echo "cuda"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Check if running on Apple Silicon
        if [[ $(uname -m) == "arm64" ]]; then
            echo "mps"
        else
            echo "cpu"
        fi
    else
        echo "cpu"
    fi
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to show available models
show_models() {
    echo ""
    echo "Available preset models:"
    echo "  gpt2-small    - GPT-2 Small with res-jb SAEs (default, lightweight)"
    echo "  gpt2-medium   - GPT-2 Medium with res-jb SAEs"
    echo "  gpt2-large    - GPT-2 Large with res-jb SAEs"
    echo "  gpt2-xl       - GPT-2 XL with res-jb SAEs"
    echo "  gemma-2b      - Gemma-2 2B with gemmascope SAEs"
    echo "  gemma-9b      - Gemma-2 9B with gemmascope SAEs"
    echo "  gemma-9b-it   - Gemma-2 9B Instruct with gemmascope SAEs (131k features)"
    echo "  llama-8b      - Llama 3.1 8B with llamascope SAEs"
    echo "  custom        - Custom configuration (pass additional args)"
    echo ""
}

# Parse command line arguments
MODEL_PRESET=${1:-$DEFAULT_MODEL}
EXTRA_ARGS="${@:2}"

# Allow TOKEN_LIMIT to be set via environment variable
TOKEN_LIMIT=${TOKEN_LIMIT:-1000}

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if inference directory exists
if [ ! -d "$INFERENCE_DIR" ]; then
    print_error "Inference directory not found: $INFERENCE_DIR"
    print_error "Make sure you're running this script from the baskerville root directory"
    exit 1
fi

# Navigate to inference directory
cd "$INFERENCE_DIR"
print_info "Changed to inference directory: $(pwd)"

# Detect device
DEVICE=$(detect_device)
print_info "Detected device: $DEVICE"
print_info "Token limit: $TOKEN_LIMIT (set TOKEN_LIMIT env var to change)"

# Check if port is already in use
PORT=${PORT:-$DEFAULT_PORT}
if check_port $PORT; then
    print_warn "Port $PORT is already in use. The inference server might already be running."
    print_warn "To stop it, find the process: lsof -i :$PORT"
    print_warn "Or specify a different port: PORT=5003 $0 $MODEL_PRESET"
    exit 1
fi

# Set up model configuration based on preset
case "$MODEL_PRESET" in
    "gpt2-small")
        print_info "Starting GPT-2 Small with res-jb SAEs..."
        CMD="poetry run python start.py \
            --model_id gpt2-small \
            --sae_sets res-jb \
            --device $DEVICE \
            --port $PORT"
        ;;

    "gpt2-medium")
        print_info "Starting GPT-2 Medium with res-jb SAEs..."
        CMD="poetry run python start.py \
            --model_id gpt2-medium \
            --sae_sets res-jb \
            --device $DEVICE \
            --port $PORT"
        ;;

    "gpt2-large")
        print_info "Starting GPT-2 Large with res-jb SAEs..."
        CMD="poetry run python start.py \
            --model_id gpt2-large \
            --sae_sets res-jb \
            --device $DEVICE \
            --port $PORT"
        ;;

    "gpt2-xl")
        print_info "Starting GPT-2 XL with res-jb SAEs..."
        CMD="poetry run python start.py \
            --model_id gpt2-xl \
            --sae_sets res-jb \
            --device $DEVICE \
            --port $PORT \
            --model_dtype float16"
        ;;

    "gemma-2b")
        print_info "Starting Gemma-2 2B with gemmascope SAEs..."
        CMD="poetry run python start.py \
            --model_id gemma-2-2b \
            --sae_sets gemmascope-res-16k \
            --device $DEVICE \
            --port $PORT \
            --model_dtype bfloat16 \
            --sae_dtype bfloat16 \
            --max_loaded_saes 200"
        ;;

    "gemma-9b")
        print_info "Starting Gemma-2 9B with gemmascope SAEs..."
        print_warn "This model requires significant memory (~18GB+)"
        CMD="poetry run python start.py \
            --model_id gemma-2-9b \
            --sae_sets gemmascope-res-16k \
            --device $DEVICE \
            --port $PORT \
            --model_dtype bfloat16 \
            --sae_dtype bfloat16 \
            --max_loaded_saes 100"
        ;;

    "gemma-9b-it")
        print_info "Starting Gemma-2 9B Instruct with gemmascope SAEs (layer 20, 131k features)..."
        print_warn "This model requires significant memory (~18GB+)"
        print_info "Memory optimizations ENABLED (torch.no_grad, stop_at_layer, auto_clear_cache)"
        CMD="poetry run python start.py \
            --model_id gemma-2-9b-it \
            --sae_sets gemmascope-res-131k \
            --device $DEVICE \
            --port $PORT \
            --model_dtype bfloat16 \
            --sae_dtype bfloat16 \
            --max_loaded_saes 100 \
            --include_sae 20-gemmascope-res-131k \
            --optimize_memory \
            --auto_clear_cache"
        ;;

    "llama-8b")
        print_info "Starting Llama 3.1 8B with llamascope SAEs..."
        print_warn "This model requires HuggingFace token for gated model access"
        CMD="poetry run python start.py \
            --model_id meta-llama/Llama-3.1-8B \
            --sae_sets llamascope-res-32k \
            --device $DEVICE \
            --port $PORT \
            --model_dtype bfloat16 \
            --sae_dtype bfloat16 \
            --max_loaded_saes 100"
        ;;

    "custom")
        print_info "Starting with custom configuration..."
        if [ -z "$EXTRA_ARGS" ]; then
            print_error "No custom arguments provided. Example:"
            echo "  $0 custom --model_id gpt2-small --sae_sets res-jb --device cuda"
            exit 1
        fi
        CMD="poetry run python start.py --port $PORT $EXTRA_ARGS"
        ;;

    *)
        print_error "Unknown model preset: $MODEL_PRESET"
        show_models
        exit 1
        ;;
esac

# Add common options
CMD="$CMD --host 0.0.0.0 --token_limit $TOKEN_LIMIT"

# Show the command being run
echo ""
print_info "Running command:"
echo "  $CMD"
echo ""

# Show connection info
echo "=========================================="
echo ""
print_info "Server will be available at:"
echo "  http://127.0.0.1:$PORT"
echo ""
print_info "API documentation available at:"
echo "  http://127.0.0.1:$PORT/docs"
echo ""
print_info "To test the server:"
echo "  curl -X POST http://127.0.0.1:$PORT/v1/activation/single \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"prompt\": \"Hello world\", \"model\": \"$MODEL_PRESET\", \"source\": \"0-res-jb\", \"index\": \"0\"}'"
echo ""
print_info "To connect from webapp, set in .env:"
echo "  USE_LOCALHOST_INFERENCE=true"
echo ""
echo "=========================================="
echo ""
print_info "Press Ctrl+C to stop the server"
echo ""

# Handle Ctrl+C gracefully
trap 'echo ""; print_info "Shutting down inference server..."; exit 0' INT TERM

# Run the server
eval $CMD