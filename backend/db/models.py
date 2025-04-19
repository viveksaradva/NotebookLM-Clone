from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    documents = relationship("Document", back_populates="owner")
    
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    document_id = Column(String, unique=True, index=True)  # UUID for vector DB reference
    file_path = Column(String)
    file_type = Column(String)  # pdf, txt, web, etc.
    chunk_count = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="documents")
    highlights = relationship("Highlight", back_populates="document")
    
class Highlight(Base):
    __tablename__ = "highlights"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    highlight_type = Column(String)  # Concept, Process, Fact, Task, Formula
    sentence_type = Column(String)  # Definition, Explanation, Quote, etc.
    note = Column(Text, nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    document = relationship("Document", back_populates="highlights")
    user = relationship("User")
    
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    document = relationship("Document")
    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="session")
    
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # user or assistant
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("ChatSession", back_populates="messages")
