from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    document_id: str

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    query: str
    document_id: str
    session_id: Optional[str] = None

class ChatMessage(BaseModel):
    user: Optional[str] = None
    bot: Optional[str] = None

class ChatResponse(BaseModel):
    query: str
    response: str
    session_id: str
    chat_history: Optional[List[ChatMessage]] = None
