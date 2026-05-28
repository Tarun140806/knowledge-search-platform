from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    session_id: str = None  # for chat

class ChatRequest(BaseModel):
    message: str
    session_id: str

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str