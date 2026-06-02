import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.chroma import chroma_client, embedding_model, get_collection
from rank_bm25 import BM25Okapi
import numpy as np

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

def store_document(doc_id: str, file_path: str, file_type: str, company_id: str = None) -> int:
    col = get_collection(f"company_{company_id}_docs") if company_id else collection

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

def hybrid_search(query: str, n_results: int = 5, company_id: str = None) -> list:
    """
    Combines dense (ChromaDB) and sparse (BM25) retrieval.
    Returns reranked results using Reciprocal Rank Fusion.
    """
    col = get_collection(f"company_{company_id}_docs") if company_id else collection

    if col.count() == 0:
        return []

    # Get ALL documents from ChromaDB
    all_docs = col.get()
    all_texts = all_docs["documents"]

    if not all_texts:
        return []

    # ── Dense retrieval (ChromaDB) ──
    query_embedding = embedding_model.encode([query]).tolist()
    dense_results = col.query(
        query_embeddings=query_embedding,
        n_results=min(n_results * 2, len(all_texts))
    )
    dense_docs = dense_results["documents"][0]

    # ── Sparse retrieval (BM25) ──
    tokenized_corpus = [doc.lower().split() for doc in all_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    top_bm25_indices = np.argsort(bm25_scores)[::-1][:n_results * 2]
    sparse_docs = [all_texts[i] for i in top_bm25_indices]

    # ── Reciprocal Rank Fusion (RRF) ──
    k = 60
    scores = {}

    for rank, doc in enumerate(dense_docs):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    for rank, doc in enumerate(sparse_docs):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    # Sort by combined score
    reranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [doc for doc, score in reranked[:n_results]]

def retrieve_relevant_context(query: str, n_results: int = 5, company_id: str = None) -> list:
    return hybrid_search(query, n_results=n_results, company_id=company_id)

def get_collection_count(company_id: str = None) -> int:
    col = get_collection(f"company_{company_id}_docs") if company_id else collection
    return col.count()

def clear_collection(company_id: str = None):
    col_name = f"company_{company_id}_docs" if company_id else "engineering_docs"
    global collection
    chroma_client.delete_collection(col_name)
    if not company_id:
        collection = get_collection()