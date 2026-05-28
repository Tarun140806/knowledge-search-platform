import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.chroma import chroma_client, embedding_model, get_collection

# Default collection
collection = get_collection()

def load_and_chunk_document(file_path: str, file_type: str) -> list:
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)
    return chunks

def store_document(doc_id: str, file_path: str, file_type: str, user_id: str = None) -> int:
    # Use user-specific collection if user_id provided
    col = get_collection(f"user_{user_id}_docs") if user_id else collection

    chunks = load_and_chunk_document(file_path, file_type)
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.encode(texts).tolist()
    ids = [f"{doc_id}-chunk-{i}" for i in range(len(texts))]
    metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(texts))]

    col.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    return len(texts)

def retrieve_relevant_context(query: str, n_results: int = 5, user_id: str = None) -> list:
    col = get_collection(f"user_{user_id}_docs") if user_id else collection

    if col.count() == 0:
        return []

    query_embedding = embedding_model.encode([query]).tolist()

    results = col.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, col.count())
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    return results["documents"][0]

def get_collection_count(user_id: str = None) -> int:
    col = get_collection(f"user_{user_id}_docs") if user_id else collection
    return col.count()

def clear_collection(user_id: str = None):
    col_name = f"user_{user_id}_docs" if user_id else "engineering_docs"
    global collection
    chroma_client.delete_collection(col_name)
    if not user_id:
        collection = get_collection()