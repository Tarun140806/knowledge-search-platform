import chromadb
from sentence_transformers import SentenceTransformer

chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_collection(name: str = "engineering_docs"):
    return chroma_client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )