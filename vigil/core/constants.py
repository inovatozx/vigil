import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")
CHROMA_DATA_PATH = os.path.join(DATA_DIR, "chroma_db")
MODELS_DIR = os.path.join(DATA_DIR, "models")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")

# API
API_PREFIX = "/api"

# Auth
TOKEN_TYPE = "bearer"

# Roles
USER_ROLE = "user"
ADMIN_ROLE = "admin"

# Chat
CHAT_ROLES = ["user", "assistant", "system", "tool"]

# Document Formats
DOCUMENT_FORMATS = ["markdown", "html", "csv", "txt", "pdf"]

# Task Status
TASK_STATUS = ["pending", "in_progress", "done", "cancelled"]

# Memory Categories
MEMORY_CATEGORIES = ["fact", "preference", "context", "skill"]

# LLM Providers (example, expand as needed)
LLM_PROVIDERS = [
    "ollama", "openai", "anthropic", "gemini", "groq", "deepseek", "mistral", "xai"
]

# Default values
DEFAULT_LANGUAGE = "pt-BR"
DEFAULT_THEME = "dark"
