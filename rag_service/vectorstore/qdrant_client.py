from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

# 1. Initialize the embedding model (Gemini)
# Ensure your GOOGLE_API_KEY is in your environment variables
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# 2. Connect to the local Docker Qdrant instance
client = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = "course_materials"

def init_vector_store():
    """Creates the collection if it doesn't exist."""
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not exists:
        # Gemini's text-embedding-004 outputs 768 dimensions
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        print(f"Collection '{COLLECTION_NAME}' created successfully.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

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