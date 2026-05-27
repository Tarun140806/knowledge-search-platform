from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_document(filename: str, doc_type: str, chunks_stored: int) -> dict:
    """
    Saves uploaded document metadata to Supabase.
    """
    response = supabase.table("documents").insert({
        "filename": filename,
        "doc_type": doc_type,
        "chunks_stored": chunks_stored
    }).execute()
    return response.data[0]

def save_search(query: str, answer: str, sources: list) -> dict:
    """
    Saves search query and answer to Supabase.
    """
    response = supabase.table("search_history").insert({
        "query": query,
        "answer": answer,
        "sources": sources
    }).execute()
    return response.data[0]

def get_search_history() -> list:
    """
    Fetches all past searches ordered by newest first.
    """
    response = supabase.table("search_history").select("*").order("created_at", desc=True).execute()
    return response.data

def get_documents() -> list:
    """
    Fetches all uploaded documents.
    """
    response = supabase.table("documents").select("*").order("uploaded_at", desc=True).execute()
    return response.data