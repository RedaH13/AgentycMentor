from langchain_core.messages import SystemMessage
from mas_orchestrator.state.schemas import ChatState
from mas_orchestrator.nodes.chat_tools_node import chat_tools
from llm_clients.prompts.chat_tutor_prompt import CHAT_TUTOR_SYSTEM_PROMPT
from llm_clients.gemini_client import get_gemini_client

# Init LLM using client factory
llm = get_gemini_client(temperature=0.3)
llm_with_tools = llm.bind_tools(chat_tools)

def run_chat_tutor_node(state: ChatState):
    """
    Evaluates the conversation history, applies Socratic guidance, 
    and determines whether to answer or query Qdrant
    """
    report_context = state.get("student_report", "Aucun rapport d'évaluation disponible.")
    
    # Format the decoupled prompt with the student's evaluation data
    formatted_prompt = CHAT_TUTOR_SYSTEM_PROMPT.format(report_context=report_context)
    system_prompt = SystemMessage(content=formatted_prompt)
    
    # Combine the system prompt with the ongoing message history
    conversation_history = [system_prompt] + state["messages"]
    
    # Invoke the model (returns an AIMessage or a ToolCall)
    response = llm_with_tools.invoke(conversation_history)
    
    return {"messages": [response]}