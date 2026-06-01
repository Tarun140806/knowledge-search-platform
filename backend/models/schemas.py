from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ─── Request Models ───

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SearchRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

# ─── Response Models ───
class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: str
    email: str

class LoginResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str
    user_id: str
    email: str

class UploadResponse(BaseModel):
    success: bool
    doc_id: str
    filename: str
    chunks_stored: int
    total_chunks_in_db: int
    message: str

class DocumentItem(BaseModel):
    id: str
    filename: str
    doc_type: str
    chunks_stored: int
    uploaded_at: datetime
    user_id: Optional[str]

class DocumentsListResponse(BaseModel):
    success: bool
    total_chunks_in_db: int
    documents: List[DocumentItem]

class SearchResponse(BaseModel):
    success: bool
    query: str
    answer: str
    sources: List[str]
    context_used: bool

class ChatResponse(BaseModel):
    success: bool
    session_id: str
    answer: str
    sources: List[str]

class MessageItem(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime

class ChatHistoryResponse(BaseModel):
    success: bool
    session_id: str
    messages: List[MessageItem]

class SessionItem(BaseModel):
    id: str
    user_id: str
    created_at: datetime

class SessionsResponse(BaseModel):
    success: bool
    sessions: List[SessionItem]