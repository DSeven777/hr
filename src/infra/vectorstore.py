from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import Config
from src.exception.base import VectorStoreError

class VectorStoreProvider(ABC):
    """Abstract interface for Vector Store operations."""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents."""
        pass
        
    @abstractmethod
    def save(self) -> None:
        """Persist the vector store."""
        pass

class FAISSStore(VectorStoreProvider):
    """FAISS implementation of VectorStoreProvider."""
    
    def __init__(self):
        try:
            self.embeddings = OpenAIEmbeddings(
                api_key=Config.OPENAI_API_KEY,
                base_url=Config.OPENAI_API_BASE
            )
            self.index_path = Config.VECTOR_STORE_PATH
            
            if self.index_path.exists() and (self.index_path / "index.faiss").exists():
                self.vector_store = FAISS.load_local(
                    str(self.index_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                # Initialize empty store (requires at least one text to init in some versions, 
                # but we can handle lazy init or init with dummy)
                # For simplicity, we'll initialize when adding documents if empty, 
                # or just use a helper to create empty.
                # FAISS.from_texts([""], embedding=...) is a hack.
                # Better to store None and init on first add.
                self.vector_store = None
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize FAISS store: {str(e)}")

    def add_documents(self, documents: List[Document]) -> None:
        try:
            if not documents:
                return
                
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                self.vector_store.add_documents(documents)
            
            self.save()
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents: {str(e)}")

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if self.vector_store is None:
            return []
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            raise VectorStoreError(f"Search failed: {str(e)}")

    def save(self) -> None:
        if self.vector_store:
            try:
                Config.VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
                self.vector_store.save_local(str(Config.VECTOR_STORE_PATH))
            except Exception as e:
                raise VectorStoreError(f"Failed to save vector store: {str(e)}")
