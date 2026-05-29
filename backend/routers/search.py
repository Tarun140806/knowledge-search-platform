from fastapi import APIRouter, HTTPException, Depends
from models.schemas import SearchRequest
from services.search_service import search
from services.supabase_service import save_search, get_search_history
from routers.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/")
async def search_docs(request: SearchRequest, user=Depends(get_current_user)):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        user_id = user["user_id"]
        result = search(request.query, user_id=user_id)

        save_search(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"],
            user_id=user_id
        )

        return {
            "success": True,
            "query": request.query,
            "answer": result["answer"],
            "sources": result["sources"],
            "context_used": result["context_used"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_history(user=Depends(get_current_user)):
    try:
        history = get_search_history(user_id=user["user_id"])
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))