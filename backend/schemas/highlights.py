from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HighlightBase(BaseModel):
    text: str
    highlight_type: Optional[str] = None
    sentence_type: Optional[str] = None
    note: Optional[str] = None

class HighlightCreate(HighlightBase):
    document_id: str

class HighlightResponse(HighlightBase):
    id: int
    document_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SmartHighlightRequest(BaseModel):
    text: str

class SmartHighlightResponse(BaseModel):
    highlight_type: str
    sentence_type: str
    short_note: str
