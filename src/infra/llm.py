from langchain_openai import ChatOpenAI
from src.config import Config

class OpenAIProvider:
    """Provider for OpenAI Chat Models."""
    
    def get_model(self, temperature: float = 0):
        """Get configured ChatOpenAI instance."""
        return ChatOpenAI(
            model=Config.OPENAI_MODEL_NAME,
            temperature=temperature,
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE
        )
