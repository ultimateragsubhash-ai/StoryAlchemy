"""BM25 keyword search service."""

from rank_bm25 import BM25Okapi
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BM25Service:
    """Service for BM25 keyword search."""
    
    def __init__(self):
        self.documents: List[str] = []
        self.tokenized_docs: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.doc_metadata: List[Dict[str, Any]] = []
    
    def index_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Index documents for BM25 search."""
        self.documents = documents
        self.doc_metadata = metadata or [{} for _ in documents]
        
        # Simple tokenization (can be improved with spacy)
        self.tokenized_docs = [doc.lower().split() for doc in documents]
        
        # Build BM25 index
        self.bm25 = BM25Okapi(self.tokenized_docs)
        
        logger.info(f"Indexed {len(documents)} documents for BM25")
    
    def search(
        self,
        query: str,
        top_k: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search documents using BM25."""
        
        if not self.bm25:
            logger.warning("BM25 not initialized - no documents indexed")
            return []
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        import numpy as np
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # Return results
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include positive scores
                results.append({
                    "id": str(idx),
                    "score": float(scores[idx]),
                    "text": self.documents[idx],
                    **self.doc_metadata[idx],
                })
        
        return results
    
    def add_document(
        self,
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a single document to the index."""
        self.documents.append(document)
        self.doc_metadata.append(metadata or {})
        self.tokenized_docs.append(document.lower().split())
        
        # Rebuild index
        self.bm25 = BM25Okapi(self.tokenized_docs)
        
        logger.info(f"Added document, total: {len(self.documents)}")


# Global service instance
bm25_service = BM25Service()
