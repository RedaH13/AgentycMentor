from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

@tool
def retrieve_course_material(query: str) -> str:
    """
    Queries the Qdrant vector database for syllabus materials, formulas, and course context.
    Use this when the student asks a theoretical question or needs a concept explained.
    """
    # TODO: Import your Qdrant vector store connection from rag_service/
    # Example: return qdrant_client.similarity_search(query, k=3)
    
    return "Retrieved context from Qdrant based on the query."

# Export the tools list to bind to the LLM in the tutor node
chat_tools = [retrieve_course_material]

# Export the runnable node for the router graph
run_chat_tools_node = ToolNode(chat_tools)