"""Backend configuration for AKARI."""
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent

# llama-server endpoint
LLAMA_HOST = os.environ.get("AKARI_LLAMA_HOST", "127.0.0.1")
LLAMA_PORT = int(os.environ.get("AKARI_LLAMA_PORT", "8080"))
LLAMA_URL = f"http://{LLAMA_HOST}:{LLAMA_PORT}/v1/chat/completions"

# Model path
MODEL_PATH = os.environ.get("AKARI_MODEL_PATH", str(ROOT / "models" / "akari.gguf"))

# Backend bind
BACKEND_HOST = os.environ.get("AKARI_BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.environ.get("AKARI_BACKEND_PORT", "8081"))

# Conversation storage
DATA_DIR = ROOT / "data"
CONVERSATIONS_DIR = DATA_DIR / "conversations"

# Context management
MAX_HISTORY_TOKENS = int(os.environ.get("AKARI_MAX_HISTORY_TOKENS", "6000"))
MAX_NEW_TOKENS = int(os.environ.get("AKARI_MAX_NEW_TOKENS", "512"))
DEFAULT_TEMPERATURE = float(os.environ.get("AKARI_TEMPERATURE", "0.7"))
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("AKARI_REQUEST_TIMEOUT", "180"))

# Generation defaults
DEFAULT_MAX_TOKENS = 256