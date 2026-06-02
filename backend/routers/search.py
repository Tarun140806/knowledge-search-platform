from fastapi import APIRouter, HTTPException, Depends
from models.schemas import SearchRequest, SearchResponse
from services.search_service import search
from services.supabase_service import save_search, get_search_history
from routers.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/")
async def search_docs(
    request: SearchRequest,
    user: dict = Depends(get_current_user)
):
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if len(request.query) > 1000:
            raise HTTPException(status_code=400, detail="Query too long — max 1000 characters")

        # Use company_id so all employees search same docs
        result = search(request.query.strip(), company_id=user["company_id"])

        save_search(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"],
            company_id=user["company_id"]
        )

        return {
            "success": True,
            "query": request.query,
            "answer": result["answer"],
            "sources": result["sources"],
            "context_used": result["context_used"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_history(user: dict = Depends(get_current_user)):
    try:
        history = get_search_history(company_id=user["company_id"])
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))