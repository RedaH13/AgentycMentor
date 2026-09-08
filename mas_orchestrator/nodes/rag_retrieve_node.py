from mas_orchestrator.state.schemas import MASState
from rag_service.vectorstore.qdrant_client import get_qdrant_vector_store

def run_rag_retrieve_node(state: MASState) -> dict:
    """Queries Qdrant for course materials matching the student's submission."""
    text_to_analyze = state.get("final_confirmed_text", "")
    if not text_to_analyze:
        return {"retrieved_context": "No text available to query course materials."}

    try:
        vector_store = get_qdrant_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        search_query = text_to_analyze[:500] 
        docs = retriever.invoke(search_query)
        
        if not docs:
            return {"retrieved_context": "No relevant course materials found in Qdrant."}
        formatted_context = "\n\n".join([
            f"--- Course Material {i+1} ---\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ])
        
        return {
            "retrieved_context": formatted_context,
            "error": None
        }
        
    except Exception as e:
        print(f"Qdrant Retrieval Error: {str(e)}")
        return {"retrieved_context": "Course materials database is temporarily unavailable."}