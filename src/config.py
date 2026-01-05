import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application Configuration."""
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo")
    
    # Vector Store Settings
    VECTOR_STORE_PATH = Path(os.getenv("VECTOR_STORE_PATH", "./data/vectorstore"))
    
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/hr_recruitment")

    # App Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required in .env file")
