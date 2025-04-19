from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class StudyGuideRequest(BaseModel):
    document_id: str
    format: Optional[str] = "markdown"  # markdown, html, text

class StudyGuideResponse(BaseModel):
    document_id: str
    study_guide: str
    key_concepts: List[str]
    review_questions: List[str]
