from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

# Importez votre connexion Qdrant depuis votre service RAG
from rag_service.vectorstore.qdrant_client import get_qdrant_vector_store

@tool
def retrieve_course_material(query: str) -> str:
    """
    Queries the Qdrant vector database for syllabus materials, formulas, and course context.
    Use this when the student asks a theoretical question or needs a concept explained.
    """
    try:
        #instance du VectorStore LangChain
        vector_store = get_qdrant_vector_store()
        
        # recherche de similarité (3 morceaux les plus pertinents)
        docs = vector_store.similarity_search(query, k=3)
        
        # Verify fetch
        if not docs:
            return "Aucun document pertinent trouvé dans le cours pour cette requête."
            
        # Format results -> LLM
        formatted_results = []
        for i, doc in enumerate(docs):
            formatted_results.append(f"--- Extrait {i+1} ---\n{doc.page_content}")
            
        # On fusionne tout en un seul grand texte
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        print(f"Erreur lors de la recherche Qdrant : {e}")
        return "Une erreur est survenue lors de la récupération des documents du cours."

# Export the tools list to bind to the LLM in the tutor node
chat_tools = [retrieve_course_material]

# Export the runnable node for the router graph
run_chat_tools_node = ToolNode(chat_tools)