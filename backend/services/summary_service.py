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

        # Limit the number of chunks to process
        max_chunks = min(3, len(chunks))  # Process at most 3 chunks
        chunks = chunks[:max_chunks]

        # Limit the size of each chunk
        limited_chunks = [chunk[:3000] for chunk in chunks]  # Limit each chunk to 3000 characters
        document_text = "\n\n".join(limited_chunks)

        # Create prompt
        prompt = f"""
        You are an expert summarizer. Create a concise summary of this document excerpt:

        {document_text}

        Capture the key points and main ideas. Keep the summary under {max_length} words.
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
