from groq import Groq
from config import GROQ_API_KEY
from services.rag_service import retrieve_relevant_context

client = Groq(api_key=GROQ_API_KEY)

def search(query: str, company_id: str = None) -> dict:
    relevant_chunks = retrieve_relevant_context(query, company_id=company_id)

    if not relevant_chunks:
        return {
            "answer": "No relevant documents found. Please upload some engineering documents first.",
            "sources": [],
            "context_used": False
        }

    context = "\n\n".join(relevant_chunks)

    prompt = f"""You are an intelligent engineering knowledge assistant for a software development company.
Use ONLY the context provided below to answer the question.
If the answer is not in the context, say "I couldn't find relevant information in the uploaded documents."
Do not make up information.

Context from engineering documents:
{context}

Question: {query}

Provide a clear, concise, and accurate answer based on the context above.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful engineering knowledge assistant. Answer questions accurately based only on the provided context."},
            {"role": "user", "content": prompt}
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