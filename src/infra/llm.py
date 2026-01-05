from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from src.config import Config
from src.exception.base import LLMError

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def get_model(self) -> BaseChatModel:
        """Return a configured LangChain Chat Model."""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLMProvider."""
    
    def __init__(self):
        try:
            self.model = ChatOpenAI(
                api_key=Config.OPENAI_API_KEY,
                base_url=Config.OPENAI_API_BASE,
                model=Config.OPENAI_MODEL_NAME,
                temperature=0
            )
        except Exception as e:
            raise LLMError(f"Failed to initialize OpenAI model: {str(e)}")

    def get_model(self) -> BaseChatModel:
        return self.model
