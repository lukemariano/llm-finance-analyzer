import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    """API configuration class."""

    API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3-70b-8192")

    USE_RATE_LIMIT = os.getenv("USE_RATE_LIMIT", "true").lower() == "true"
    RATE_LIMIT_BATCH_SIZE = int(os.getenv("RATE_LIMIT_BATCH_SIZE", "30"))
    RATE_LIMIT_SLEEP_TIME = int(os.getenv("RATE_LIMIT_SLEEP_TIME", "60"))

    EXTRATOS_DIR = Path(os.getenv("EXTRATOS_DIR", "extratos"))
    OUTPUT_FILE = os.getenv("OUTPUT_FILE", "finances.csv")

    TEMPLATE_FILE = os.getenv("TEMPLATE_FILE", "templates/default_template.txt")
    CATEGORIES_FILE = os.getenv("CATEGORIES_FILE", "templates/categories.json")

    @classmethod
    def validate(cls):
        """Validates the essential configuration parameters."""
        if not cls.API_KEY:
            raise ValueError("GROQ API key is not set. Please set the GROQ_API_KEY in the .env file.")
        
        if not cls.EXTRATOS_DIR.exists():
            raise ValueError(f"Extratos directory '{cls.EXTRATOS_DIR}' does not exist. Please check the path in the .env file.")
        
        return True