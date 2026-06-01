from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.rag_service import store_document, get_collection_count, clear_collection
from services.supabase_service import save_document, get_documents, delete_all_documents
from routers.auth import get_current_user
import tempfile
import os
import uuid

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/docs")
async def upload_docs(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")

    content = await file.read()
    
    # 10MB limit
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large — max 10MB")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    file_type = "pdf" if file.filename.endswith('.pdf') else "txt"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        doc_id = str(uuid.uuid4())
        chunks_stored = store_document(doc_id, tmp_path, file_type, user_id=user["user_id"])
        save_document(doc_id, file.filename, file_type, chunks_stored, user_id=user["user_id"])

        return {
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_stored": chunks_stored,
            "total_chunks_in_db": get_collection_count(user_id=user["user_id"]),
            "message": f"Successfully processed {chunks_stored} chunks from {file.filename}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        os.unlink(tmp_path)

@router.get("/docs")
def list_documents(user=Depends(get_current_user)):
    try:
        user_id = user["user_id"]
        docs = get_documents(user_id=user_id)
        return {
            "success": True,
            "total_chunks_in_db": get_collection_count(user_id=user_id),
            "documents": docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/docs")
def clear_documents(user=Depends(get_current_user)):
    try:
        user_id = user["user_id"]
        clear_collection(user_id=user_id)
        delete_all_documents(user_id=user_id)
        return {"success": True, "message": "All documents cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))