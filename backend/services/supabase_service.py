from database.supabase import supabase

def save_document(doc_id: str, filename: str, doc_type: str, chunks_stored: int, user_id: str = None) -> dict:
    """
    Saves uploaded document metadata to Supabase.
    """
    response = supabase.table("documents").insert({
        "chroma_doc_id": doc_id,
        "filename": filename,
        "doc_type": doc_type,
        "chunks_stored": chunks_stored,
        "user_id": user_id
    }).execute()
    return response.data[0]

def save_search(query: str, answer: str, sources: list, user_id: str = None) -> dict:
    """
    Saves search query and answer to Supabase.
    """
    response = supabase.table("search_history").insert({
        "query": query,
        "answer": answer,
        "sources": sources,
        "user_id": user_id
    }).execute()
    return response.data[0]

def get_search_history(user_id: str = None) -> list:
    """
    Fetches past searches — filtered by user if user_id provided.
    """
    query = supabase.table("search_history").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    return query.order("created_at", desc=True).execute().data

def get_documents(user_id: str = None) -> list:
    """
    Fetches uploaded documents — filtered by user if user_id provided.
    """
    query = supabase.table("documents").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    return query.order("uploaded_at", desc=True).execute().data

def delete_all_documents(user_id: str = None) -> None:
    """
    Deletes all documents — filtered by user if user_id provided.
    """
    query = supabase.table("documents").delete()
    if user_id:
        query = query.eq("user_id", user_id)
    else:
        query = query.neq("id", "00000000-0000-0000-0000-000000000000")
    query.execute()

def create_user(email: str, hashed_password: str) -> dict:
    """
    Creates a new user in Supabase.
    """
    response = supabase.table("users").insert({
        "email": email,
        "hashed_password": hashed_password
    }).execute()
    return response.data[0]

def get_user_by_email(email: str) -> dict:
    """
    Fetches a user by email.
    Returns None if not found.
    """
    response = supabase.table("users").select("*").eq("email", email).execute()
    if response.data:
        return response.data[0]
    return None

def create_chat_session(user_id: str) -> dict:
    response = supabase.table("chat_sessions").insert({
        "user_id": user_id
    }).execute()
    return response.data[0]

def save_chat_message(session_id: str, role: str, content: str) -> dict:
    response = supabase.table("chat_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()
    return response.data[0]

def get_chat_messages(session_id: str) -> list:
    response = supabase.table("chat_messages").select("*").eq(
        "session_id", session_id
    ).order("created_at", asc=True).execute()
    return response.data