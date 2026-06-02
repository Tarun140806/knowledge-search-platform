from groq import Groq
from config import GROQ_API_KEY
from services.rag_service import retrieve_relevant_context
from services.supabase_service import (
    create_chat_session,
    save_chat_message,
    get_chat_messages
)

client = Groq(api_key=GROQ_API_KEY)

def start_session(user_id: str) -> str:
    """
    Creates a new chat session and returns session_id.
    """
    session = create_chat_session(user_id)
    return session["id"]

def chat(session_id: str, user_message: str, company_id: str) -> dict:
    """
    Takes a message, retrieves relevant context from company docs,
    builds conversation history and returns AI response.
    """
    # Step 1 — Save user message
    save_chat_message(session_id, "user", user_message)

    # Step 2 — Retrieve from company collection
    context_chunks = retrieve_relevant_context(user_message, company_id=company_id)
    context = "\n\n".join(context_chunks) if context_chunks else ""

    # Step 3 — Fetch conversation history
    history = get_chat_messages(session_id)

    # Step 4 — Build messages for Groq
    messages = [
        {
            "role": "system",
            "content": f"""You are an intelligent engineering knowledge assistant for a software development company.
You help engineers find information from internal engineering documents.
Use ONLY the context provided to answer questions.
If the answer is not in the context, say "I couldn't find relevant information in the uploaded documents."
Do not make up information.

Context from engineering documents:
{context if context else "No relevant documents found."}"""
        }
    ]

    # Add conversation history
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Step 5 — Call Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=1000
    )

    answer = response.choices[0].message.content.strip()

    # Step 6 — Save assistant response
    save_chat_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "answer": answer,
        "sources": context_chunks
    }