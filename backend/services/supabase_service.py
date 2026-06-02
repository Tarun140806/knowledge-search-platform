from database.supabase import supabase
import random
import string

def generate_invite_code() -> str:
    """
    Generates a random 8 character invite code.
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_company(name: str) -> dict:
    """
    Creates a new company with a unique invite code.
    """
    invite_code = generate_invite_code()
    response = supabase.table("companies").insert({
        "name": name,
        "invite_code": invite_code
    }).execute()
    return response.data[0]

def get_company_by_invite_code(invite_code: str) -> dict:
    """
    Fetches a company by invite code.
    Returns None if not found.
    """
    response = supabase.table("companies").select("*").eq(
        "invite_code", invite_code
    ).execute()
    if response.data:
        return response.data[0]
    return None

def get_company_by_id(company_id: str) -> dict:
    """
    Fetches a company by ID.
    """
    response = supabase.table("companies").select("*").eq(
        "id", company_id
    ).execute()
    if response.data:
        return response.data[0]
    return None

def create_user(email: str, hashed_password: str, company_id: str = None, role: str = "user") -> dict:
    """
    Creates a new user — updated to include company_id and role.
    """
    response = supabase.table("users").insert({
        "email": email,
        "hashed_password": hashed_password,
        "company_id": company_id,
        "role": role
    }).execute()
    return response.data[0]

def save_document(doc_id: str, filename: str, doc_type: str, chunks_stored: int, company_id: str = None) -> dict:
    """
    Saves uploaded document metadata to Supabase.
    """
    response = supabase.table("documents").insert({
        "chroma_doc_id": doc_id,
        "filename": filename,
        "doc_type": doc_type,
        "chunks_stored": chunks_stored,
        "company_id": company_id
    }).execute()
    return response.data[0]

def save_search(query: str, answer: str, sources: list, company_id: str = None) -> dict:
    """
    Saves search query and answer to Supabase.
    """
    response = supabase.table("search_history").insert({
        "query": query,
        "answer": answer,
        "sources": sources,
        "company_id": company_id
    }).execute()
    return response.data[0]

def get_search_history(company_id: str = None) -> list:
    """
    Fetches past searches — filtered by user if user_id provided.
    """
    query = supabase.table("search_history").select("*")
    if company_id:
        query = query.eq("company_id", company_id)
    return query.order("created_at", desc=True).execute().data

def get_documents(company_id: str = None) -> list:
    """
    Fetches uploaded documents — filtered by user if user_id provided.
    """
    query = supabase.table("documents").select("*")
    if company_id:
        query = query.eq("company_id", company_id)
    return query.order("uploaded_at", desc=True).execute().data

def delete_all_documents(company_id: str = None) -> None:
    """
    Deletes all documents — filtered by user if user_id provided.
    """
    query = supabase.table("documents").delete()
    if company_id:
        query = query.eq("company_id", company_id)
    else:
        query = query.neq("id", "00000000-0000-0000-0000-000000000000")
    query.execute()

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
    ).order("created_at", desc=False).execute()
    return response.data

def get_user_sessions(user_id: str) -> list:
    response = supabase.table("chat_sessions").select("*").eq(
        "user_id", user_id
    ).order("created_at", desc=True).execute()
    return response.data