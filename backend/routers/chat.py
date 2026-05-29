from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest
from services.chat_service import chat, start_session
from routers.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/")
async def chat_endpoint(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """
    Main chat endpoint — continues or starts a conversation.
    """
    try:
        # Validate message
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(request.message) > 2000:
            raise HTTPException(status_code=400, detail="Message too long — max 2000 characters")

        user_id = user["user_id"]
        session_id = request.session_id
        if not session_id:
            session_id = start_session(user_id)

        result = chat(session_id, request.message.strip(), user_id)

        return {
            "success": True,
            **result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
def get_sessions(user: dict = Depends(get_current_user)):
    """
    Returns all chat sessions for the current user.
    """
    try:
        from services.supabase_service import get_user_sessions
        sessions = get_user_sessions(user["user_id"])
        return {"success": True, "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
def get_history(session_id: str, user: dict = Depends(get_current_user)):
    """
    Returns full message history for a specific session.
    """
    try:
        from services.supabase_service import get_chat_messages
        messages = get_chat_messages(session_id)
        return {"success": True, "session_id": session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))