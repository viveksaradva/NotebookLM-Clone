from typing import Dict, Any, List, Optional

from backend.services.vectordb_service import VectorDBService
from backend.services.llm_service import LLMService

class SummaryService:
    def __init__(self):
        self.vectordb_service = VectorDBService()
        self.llm_service = LLMService()
    
    def generate_document_summary(self, document_id: str, max_length: Optional[int] = 500) -> Dict[str, Any]:
        """Generate a summary for a document."""
        # Get document chunks
        chunks = self.vectordb_service.get_documents(document_id)
        
        if not chunks:
            return {
                "document_id": document_id,
                "summary": "No document content found."
            }
        
        # Combine chunks
        document_text = "\n\n".join(chunks)
        
        # Create prompt
        prompt = f"""
        You are an expert summarizer. Your task is to create a concise summary of the following document.
        
        Document:
        {document_text}
        
        Create a summary that captures the key points and main ideas of the document.
        Keep the summary under {max_length} words.
        """
        
        # Generate summary
        summary = self.llm_service.get_together_response(prompt)
        
        return {
            "document_id": document_id,
            "summary": summary
        }
    
    def generate_semantic_summary(self, highlights: List[str]) -> Dict[str, Any]:
        """Generate a semantic summary from highlights."""
        return self.llm_service.generate_semantic_summary(highlights)
