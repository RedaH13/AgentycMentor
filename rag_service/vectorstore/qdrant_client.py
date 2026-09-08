from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

# Initialize the embedding model (Gemini)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Connect to the local Docker Qdrant instance
client = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = "course_materials"

def init_vector_store():
    """Creates the collection if it doesn't exist, or recreates it if dimensions mismatch."""
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if exists:
        collection_info = client.get_collection(COLLECTION_NAME)
        vectors_config = getattr(collection_info.config.params, "vectors", None)
        current_size = getattr(vectors_config, "size", 0) if vectors_config else 0
        
        if current_size != 3072:
            print(f"Dimension mismatch detected (Found {current_size}, Expected 3072). Wiping old collection...")
            client.delete_collection(collection_name=COLLECTION_NAME)
            exists = False
    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )
        print(f"Collection '{COLLECTION_NAME}' created successfully with 3072 dimensions.")
    else:
        print(f"Collection '{COLLECTION_NAME}' is active and dimensions match.")


def get_qdrant_vector_store():
    """Returns the LangChain wrapper for Qdrant to use in the retrieve node."""
    from langchain_qdrant import QdrantVectorStore
    
    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

# Run this once when the module loads to ensure the DB is ready
init_vector_store()