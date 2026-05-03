"""Local embedding service using sentence-transformers."""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings locally."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._model is None:
            logger.info(f"Loading embedding model: {model_name}")
            self._model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.embed([text])[0]
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._model.get_sentence_embedding_dimension()
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return float(dot_product / (norm1 * norm2))


# Global service instance
embedding_service = EmbeddingService()
