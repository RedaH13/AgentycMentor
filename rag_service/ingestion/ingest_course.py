import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

load_dotenv()

def ingest_course_material(pdf_path: str, collection_name: str = "course_materials"):
    print(f"Loading document: {pdf_path}")
    
    # Load pdf
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Chunk text
    # 1000 char per chunk, 200 char overlap to preserve context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    # Init Gemini Embeddings
    # text-embedding-004 (outputs 768 dim)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # Setup Qdrant Client
    qdrant_url = "http://localhost:6333"
    client = QdrantClient(url=qdrant_url)

    # Create collection if non-exist (Gemini embeddings use 768 dimensions)
    if not client.collection_exists(collection_name):
        print(f"Creating new collection: {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    # Upsert vectors and payload to Qdrant
    print("Generating embeddings and uploading to Qdrant...")
    QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=qdrant_url,
        collection_name=collection_name,
    )
    
    print("Ingestion complete! Check your Qdrant Dashboard.")

if __name__ == "__main__":
    # Place a sample course PDF in the same folder or provide the path
    course_pdf = r"C:\Users\Dell\Desktop\Files\Projects\Stage Cádiz\Exemples C2PCT\Rubric_ExNetwork.pdf"
    
    if os.path.exists(course_pdf):
        ingest_course_material(course_pdf)
    else:
        print(f"Error: Could not find {course_pdf}. Please provide a valid PDF file.")