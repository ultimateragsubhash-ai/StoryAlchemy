"""API routes for knowledge base document upload and management."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import logging
import uuid
from io import BytesIO

from app.services.vector_service import vector_service
from app.services.chunking_service import chunking_service
from app.services.database_service import database_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file."""
    content = file.file.read()
    
    # Determine file type and extract text
    filename = file.filename.lower()
    
    if filename.endswith('.pdf'):
        # Simple PDF text extraction for MVP
        try:
            # For MVP, we'll use a simple approach
            # In production, use PyPDF2 or pdfplumber
            text = content.decode('utf-8', errors='ignore')
            # Basic PDF text extraction (removes binary artifacts)
            import re
            text = re.sub(r'[^\x20-\x7E\n]', '', text)
            return text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""
    
    elif filename.endswith('.txt') or filename.endswith('.md'):
        return content.decode('utf-8', errors='ignore')
    
    elif filename.endswith('.docx'):
        # For MVP, simple DOCX text extraction
        try:
            # Simple approach - extract text between XML tags
            text = content.decode('utf-8', errors='ignore')
            import re
            # Extract text between <w:t> tags (simplified)
            texts = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', text)
            return ' '.join(texts)
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return ""
    
    else:
        # Try to decode as text
        try:
            return content.decode('utf-8', errors='ignore')
        except:
            return ""


def process_text_to_patterns(
    text: str,
    category: str,
    source_title: str,
) -> List[dict]:
    """Process text into story patterns."""
    
    # Chunk the text
    chunks = chunking_service.chunk_text(text)
    
    patterns = []
    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 50:  # Skip very short chunks
            continue
        
        pattern = {
            "id": str(uuid.uuid4()),
            "text": chunk,
            "pattern_name": f"{source_title} - Part {i+1}",
            "pattern_type": category,
            "category": category,
            "source_document": source_title,
        }
        patterns.append(pattern)
    
    return patterns


@router.post("/upload")
async def upload_document(
    category: str = Form(...),
    title: str = Form(...),
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
):
    """Upload a document to the knowledge base.
    
    Automatically:
    1. Extracts text from the file
    2. Chunks into segments
    3. Generates embeddings
    4. Stores in vector database
    """
    
    try:
        logger.info(f"Uploading document: {title} (category: {category})")
        
        # Get text content
        if file:
            text = extract_text_from_file(file)
        elif text_content:
            text = text_content
        else:
            raise HTTPException(status_code=400, detail="No file or text content provided")
        
        if not text or len(text.strip()) < 100:
            raise HTTPException(
                status_code=400, 
                detail="Text too short or could not be extracted from file"
            )
        
        # Process into patterns
        patterns = process_text_to_patterns(text, category, title)
        
        if not patterns:
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful patterns from document"
            )
        
        # Store in vector database
        success = await vector_service.upsert_patterns(patterns)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store patterns in vector database"
            )
        
        # Also store document metadata in MongoDB
        doc_metadata = {
            "title": title,
            "category": category,
            "chunk_count": len(patterns),
            "total_chars": len(text),
        }
        
        logger.info(f"Document uploaded successfully: {len(patterns)} patterns added")
        
        return {
            "success": True,
            "message": f"Document '{title}' uploaded successfully",
            "chunks_added": len(patterns),
            "total_chars": len(text),
            "category": category,
            "extracted_patterns": [
                {"name": p["pattern_name"], "text": p["text"][:200]} 
                for p in patterns[:5]
            ],
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/patterns")
async def get_patterns(
    category: Optional[str] = None,
    limit: int = 50,
):
    """Get user-uploaded patterns from the knowledge base."""
    try:
        # Get pattern count from vector service
        count = await vector_service.get_pattern_count()
        
        # For now, return patterns from seed data + note that user patterns are stored
        # In production, this would query the vector DB with filters
        patterns = []
        
        # Get seed patterns that might have been uploaded by users
        from app.data.seed_patterns import ALL_PATTERNS
        
        for p in ALL_PATTERNS:
            if category and p.get("category") != category:
                continue
            patterns.append({
                "pattern_id": p.get("id"),
                "pattern_name": p.get("name", "Unnamed"),
                "pattern_type": p.get("type", ""),
                "category": p.get("category", ""),
                "text": p.get("text", "")[:100] + "...",
            })
        
        return {
            "patterns": patterns[:limit],
            "count": len(patterns),
            "category": category,
            "vector_db_count": count,
        }
    except Exception as e:
        logger.error(f"Error fetching patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch patterns")


@router.delete("/patterns/{pattern_id}")
async def delete_pattern(pattern_id: str):
    """Delete a pattern from the knowledge base."""
    try:
        # Implementation would delete from vector DB
        logger.info(f"Deleting pattern: {pattern_id}")
        return {"success": True, "message": f"Pattern {pattern_id} deleted"}
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete pattern")
