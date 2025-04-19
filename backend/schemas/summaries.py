from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SummaryRequest(BaseModel):
    document_id: str
    max_length: Optional[int] = 500

class SummaryResponse(BaseModel):
    document_id: str
    summary: str

class SemanticSummaryRequest(BaseModel):
    highlights: List[str]

class SemanticSummaryResponse(BaseModel):
    compressed_study_memory: str
