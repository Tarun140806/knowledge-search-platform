from fastapi import APIRouter, HTTPException
from services.search_service import search
from services.supabase_service import save_search, get_search_history
from models.schemas import SearchRequest

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/")
async def search_docs(request: SearchRequest):
    """
    Takes a question and returns an answer from uploaded documents.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        result = search(request.query)

        # Save to history
        save_search(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"]
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
def get_history():
    """
    Returns all past searches.
    """
    try:
        history = get_search_history()
        return {
            "success": True,
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))