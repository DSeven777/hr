class BaseAppException(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.code}] {self.message}"

class LLMError(BaseAppException):
    """Exception raised for LLM related errors."""
    def __init__(self, message: str):
        super().__init__(message, code="LLM_ERROR")

class VectorStoreError(BaseAppException):
    """Exception raised for VectorStore related errors."""
    def __init__(self, message: str):
        super().__init__(message, code="VECTOR_STORE_ERROR")

class ValidationError(BaseAppException):
    """Exception raised for validation errors."""
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")
