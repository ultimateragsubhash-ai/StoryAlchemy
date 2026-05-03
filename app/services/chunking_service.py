"""Simple chunking service (replaces docling for MVP)."""

from typing import List
import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    """Simple text chunking service for MVP."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks.
        
        Simple approach: split by sentences (approximate) and combine.
        """
        # Split into sentences (rough approximation)
        sentences = text.replace(". ", ".|").replace("! ", "!|").replace("? ", "?|").split("|")
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return [text] if text else []
        
        # Combine sentences into chunks
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(" ".join(current_chunk))
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [text]
    
    def chunk_text_simple(self, text: str, max_chars: int = 1000) -> List[str]:
        """Simple character-based chunking."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chars
            
            # Try to break at a sentence
            if end < len(text):
                # Look for sentence ending
                for i in range(end, start, -1):
                    if text[i] in ".!?" and i + 1 < len(text) and text[i + 1] in " \n":
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end
        
        return chunks if chunks else [text] if text else []


# Global service instance
chunking_service = ChunkingService()
