from langchain_openai import ChatOpenAI
from src.config import Config

class OpenAIProvider:
    """Provider for OpenAI Chat Models (compatible with GLM-4.7)."""
    
    def get_model(self, temperature: float = 1.0):
        """Get configured ChatOpenAI instance."""
        # GLM-4.7 Recommendations:
        # - temperature: default 1.0
        # - top_p: default 0.95
        # - thinking: {"type": "enabled"} for complex reasoning (optional)
        
        # Determine if we should enable thinking (e.g., for complex parsing tasks)
        # GLM-4.7 default behavior might vary, so explicit configuration is recommended.
        
        model_kwargs = {}
        
        # GLM-4.7 Thinking Mode Configuration:
        # Use 'extra_body' to pass vendor-specific parameters safely to OpenAI SDK.
        if "glm-4.7" in Config.OPENAI_MODEL_NAME:
             model_kwargs["extra_body"] = {
                 # Enable Thinking: {"type": "enabled"}
                 # Disable Thinking: {"type": "disabled"}
                 "thinking": {"type": "disabled"},
                 # Enable Tool Stream for faster response (recommended by GLM-4.7 docs)
                 # "tool_stream": True # Disabled as per user request (batch processing needed)
             }
             
        return ChatOpenAI(
            model=Config.OPENAI_MODEL_NAME,
            temperature=temperature,
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE,
            streaming=False, # Disable standard streaming
            model_kwargs=model_kwargs
        )
