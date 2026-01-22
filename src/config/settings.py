import os
from typing import Optional

# Load environment variables
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

# Constants
DEFAULT_LLM_MODEL = "llama3-8b-8192"  # Groq model
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Validation
def validate_config():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY must be set")
    # Add more validations as needed

# Call on import
validate_config()