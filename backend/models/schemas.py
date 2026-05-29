from pydantic import BaseModel
from typing import Optional

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