import chromadb
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="engineering_docs",
    metadata={"hnsw:space": "cosine"}
)

def load_and_chunk_document(file_path: str, file_type: str) -> list:
    """
    Loads a document and splits into chunks.
    """
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

def store_document(doc_id: str, file_path: str, file_type: str) -> int:
    """
    Chunks document and stores embeddings in ChromaDB.
    Returns number of chunks stored.
    """
    chunks = load_and_chunk_document(file_path, file_type)

    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.encode(texts).tolist()
    ids = [f"{doc_id}-chunk-{i}" for i in range(len(texts))]
    metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(texts))]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    return len(texts)

def retrieve_relevant_context(query: str, n_results: int = 5) -> list:
    """
    Retrieves most relevant chunks for a query.
    Returns list of chunks with their text.
    """
    if collection.count() == 0:
        return []

    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count())
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    return results["documents"][0]

def get_collection_count() -> int:
    """
    Returns total number of chunks stored.
    """
    return collection.count()

def clear_collection():
    """
    Clears all documents from ChromaDB.
    """
    global collection
    chroma_client.delete_collection("engineering_docs")
    collection = chroma_client.get_or_create_collection(
        name="engineering_docs",
        metadata={"hnsw:space": "cosine"}
    )