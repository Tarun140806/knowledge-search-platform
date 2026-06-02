from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.rag_service import store_document, get_collection_count, clear_collection
from services.supabase_service import save_document, get_documents, delete_all_documents
from routers.auth import require_admin, get_current_user
import tempfile
import os
import uuid

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/docs")
async def upload_docs(
    file: UploadFile = File(...),
    user: dict = Depends(require_admin)  # only admins can upload
):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")

    content = await file.read()

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large — max 10MB")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    file_type = "pdf" if file.filename.endswith('.pdf') else "txt"
    company_id = user["company_id"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        doc_id = str(uuid.uuid4())
        chunks_stored = store_document(doc_id, tmp_path, file_type, company_id=company_id)
        save_document(doc_id, file.filename, file_type, chunks_stored, company_id=company_id)

        return {
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_stored": chunks_stored,
            "total_chunks_in_db": get_collection_count(company_id=company_id),
            "message": f"Successfully processed {chunks_stored} chunks from {file.filename}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        os.unlink(tmp_path)

@router.get("/docs")
def list_documents(user: dict = Depends(get_current_user)):
    """
    Both admin and user can view uploaded documents.
    """
    try:
        docs = get_documents(company_id=user["company_id"])
        return {
            "success": True,
            "total_chunks_in_db": get_collection_count(company_id=user["company_id"]),
            "documents": docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/docs")
def clear_documents(user: dict = Depends(require_admin)):
    """
    Only admins can delete documents.
    """
    try:
        clear_collection(company_id=user["company_id"])
        delete_all_documents(company_id=user["company_id"])
        return {"success": True, "message": "All documents cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))