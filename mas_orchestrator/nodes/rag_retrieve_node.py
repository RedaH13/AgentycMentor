from mas_orchestrator.state.schemas import MASState
from qdrant_client.http import models
# from rag_service.vectorstore.qdrant_client import get_qdrant_vector_store

def run_rag_retrieve_node(state: MASState) -> dict:
    """Queries Qdrant for course materials matching the student's submission."""
    
    text_to_analyze = state.get("final_confirmed_text", "")
    diagnostic_data = state.get("diagnostic_data", {})
    subject = diagnostic_data.get("subject", "Unknown")
    return {"retrieved_context": "RAG service disabled for now.", "error": None}

    if not text_to_analyze:
        return {"retrieved_context": "No text available to query course materials."}

    try:
        # Initialize the Qdrant LangChain wrapper
        vector_store = get_qdrant_vector_store()
        
        # Configure the retriever
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 3, # Fetch the top 3 most relevant paragraphs
                #"filter": models.Filter(
                #    must=[
                #        models.FieldCondition(
                #            key="metadata.subject", # LangChain nests metadata under this key
                #            match=models.MatchValue(value=subject),
                #        )
                #    ]
                #)
            }
        )
        
        # Search Qdrant using the student's text
        search_query = text_to_analyze[:500] 
        docs = retriever.invoke(search_query)
        
        if not docs:
            return {"retrieved_context": "No relevant course materials found in Qdrant."}
            
        # Format the retrieved documents into a single string for the prompt
        formatted_context = "\n\n".join([
            f"--- Source {i+1} ---\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ])
        
        return {
            "retrieved_context": formatted_context,
            "error": None
        }
        
    except Exception as e:
        # if we have no context
        print(f"Qdrant Retrieval Error: {str(e)}")
        return {"retrieved_context": "Course materials database is temporarily unavailable."}