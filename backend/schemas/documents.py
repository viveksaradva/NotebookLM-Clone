from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    document_id: str
    file_type: str
    chunk_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentDetail(DocumentResponse):
    file_path: str
    owner_id: int
    
    class Config:
        from_attributes = True
