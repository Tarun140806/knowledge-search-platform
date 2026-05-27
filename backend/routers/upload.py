from fastapi import APIRouter, UploadFile, File, HTTPException
from services.rag_service import store_document, get_collection_count, clear_collection
from services.supabase_service import save_document, get_documents, delete_all_documents
import tempfile
import os
import uuid

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/docs")
async def upload_docs(file: UploadFile = File(...)):
    """
    Accepts PDF or TXT file, chunks and stores in ChromaDB.
    """
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )

    file_type = "pdf" if file.filename.endswith('.pdf') else "txt"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        doc_id = str(uuid.uuid4())
        chunks_stored = store_document(doc_id, tmp_path, file_type)
        save_document(doc_id, file.filename, file_type, chunks_stored)
        
        return {
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_stored": chunks_stored,
            "total_chunks_in_db": get_collection_count(),
            "message": f"Successfully processed {chunks_stored} chunks from {file.filename}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        os.unlink(tmp_path)

@router.get("/docs")
def list_documents():
    """
    Returns all uploaded documents.
    """
    try:
        docs = get_documents()
        return {
            "success": True,
            "total_chunks_in_db": get_collection_count(),
            "documents": docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/docs")
def clear_documents():
    """
    Clears all documents from ChromaDB and Supabase.
    """
    try:
        clear_collection()
        delete_all_documents()
        return {"success": True, "message": "All documents cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))