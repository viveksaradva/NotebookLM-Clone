from typing import Dict, Any, List, Optional

from backend.services.vectordb_service import VectorDBService
from backend.services.llm_service import LLMService

class StudyGuideService:
    def __init__(self):
        self.vectordb_service = VectorDBService()
        self.llm_service = LLMService()

    def generate_study_guide(self, document_id: str, format: str = "markdown") -> Dict[str, Any]:
        """Generate a study guide for a document."""
        # Get document chunks
        chunks = self.vectordb_service.get_documents(document_id)

        if not chunks:
            return {
                "document_id": document_id,
                "study_guide": "No document content found.",
                "key_concepts": [],
                "review_questions": []
            }

        # Limit the number of chunks to process
        max_chunks = min(2, len(chunks))  # Process at most 2 chunks
        limited_chunks = chunks[:max_chunks]

        # Limit the size of each chunk
        limited_chunks = [chunk[:2000] for chunk in limited_chunks]  # Limit each chunk to 2000 characters

        # Generate study guide directly
        result = self.llm_service.generate_study_guide(limited_chunks)

        return {
            "document_id": document_id,
            "study_guide": result["study_guide"],
            "key_concepts": result["key_concepts"],
            "review_questions": result["review_questions"]
        }
