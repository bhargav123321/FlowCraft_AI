
import os
from dotenv import load_dotenv

# Load environment variables from the project's .env file
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "llama-3.3-70b-versatile"
)

def validate_config():
    """
    Validate the configuration before making AI requests.
    """

    if LLM_PROVIDER.lower() != "groq":
        raise ValueError(
            "Currently, only the Groq provider is supported."
        )

    if not GROQ_API_KEY:
        raise ValueError(
            "Groq API key is missing. Add GROQ_API_KEY to your .env file."
        )

    if GROQ_API_KEY == "your_groq_api_key_here":
        raise ValueError(
            "Replace the placeholder in .env with your actual Groq API key."
        )

    if not MODEL_NAME:
        raise ValueError(
            "MODEL_NAME is missing from your .env file."
        )

    return True
