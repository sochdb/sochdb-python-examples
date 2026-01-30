"""Embedding generation client for vector search."""

import os
from typing import List, Optional, Dict
from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class EmbeddingClient:
    """OpenAI embeddings client with caching support."""
    
    def __init__(
        self,
        model: Optional[str] = "text-embedding-3-small",
        api_key: Optional[str] = None,
    ):
        """Initialize embedding client.
        
        Args:
            model: OpenAI embedding model name
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        azure_embedding = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

        if azure_endpoint and azure_api_key:
            self.model = azure_embedding or model
            self.client = AzureOpenAI(
                api_key=azure_api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
            )
        else:
            self.model = model or "text-embedding-3-small"
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._cache: Dict[str, List[float]] = {}
    
    def embed(self, text: str, use_cache: bool = True) -> List[float]:
        """Generate embedding for text.
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector as list of floats
        """
        if use_cache and text in self._cache:
            return self._cache[text]
        
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        
        embedding = response.data[0].embedding
        
        if use_cache:
            self._cache[text] = embedding
        
        return embedding
    
    def embed_batch(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            List of embedding vectors
        """
        # Check cache first
        if use_cache:
            uncached_texts = [t for t in texts if t not in self._cache]
            if not uncached_texts:
                return [self._cache[t] for t in texts]
        else:
            uncached_texts = texts
        
        # Batch API call for uncached texts
        if uncached_texts:
            response = self.client.embeddings.create(
                model=self.model,
                input=uncached_texts
            )
            
            for text, data in zip(uncached_texts, response.data):
                if use_cache:
                    self._cache[text] = data.embedding
        
        # Return in original order
        return [self._cache.get(t) or self.embed(t, use_cache=False) for t in texts]
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension for the model."""
        # text-embedding-3-small: 1536 dimensions
        # text-embedding-3-large: 3072 dimensions
        if "small" in self.model:
            return 1536
        elif "large" in self.model:
            return 3072
        else:
            return 1536  # default
