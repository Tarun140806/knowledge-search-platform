from groq import Groq
from config import GROQ_API_KEY
from services.rag_service import retrieve_relevant_context

client = Groq(api_key=GROQ_API_KEY)

def search(query: str) -> dict:
    """
    Takes a user question, retrieves relevant context from ChromaDB,
    and uses Groq to generate an answer based on the context.
    """
    # Step 1 — Retrieve relevant chunks from ChromaDB
    relevant_chunks = retrieve_relevant_context(query)

    if not relevant_chunks:
        return {
            "answer": "No relevant documents found. Please upload some engineering documents first.",
            "sources": [],
            "context_used": False
        }

    # Step 2 — Build context string from chunks
    context = "\n\n".join(relevant_chunks)

    # Step 3 — Build prompt
    prompt = f"""You are an intelligent engineering knowledge assistant for Indium Software.
You help engineers find information from internal engineering documents quickly and accurately.

Use ONLY the context provided below to answer the question.
If the answer is not in the context, say "I couldn't find relevant information in the uploaded documents."
Do not make up information.

Context from engineering documents:
{context}

Question: {query}

Provide a clear, concise, and accurate answer based on the context above.
If relevant, mention which part of the document the information came from.
"""

    # Step 4 — Call Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful engineering knowledge assistant. Answer questions accurately based only on the provided context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=1000
    )

    answer = response.choices[0].message.content.strip()

    return {
        "answer": answer,
        "sources": relevant_chunks,
        "context_used": True
    }