from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition

from mas_orchestrator.state.schemas import ChatState
from mas_orchestrator.nodes.chat_tutor_node import run_chat_tutor_node
from mas_orchestrator.nodes.chat_tools_node import run_chat_tools_node

# Init the graph with schema
memory = MemorySaver()

workflow = StateGraph(ChatState)

# Add nodes
workflow.add_node("tutor", run_chat_tutor_node)
workflow.add_node("tools", run_chat_tools_node)

# flow
workflow.set_entry_point("tutor")

# The Socratic tutor -> call a tool (Qdrant) or end turn
workflow.add_conditional_edges(
    "tutor",
    tools_condition,
    {
        "tools": "tools",
        END: END
    }
)

# After a tool executes, it must always return to the tutor to generate the final Socratic response
workflow.add_edge("tools", "tutor")

# Compile
chat_router = workflow.compile(
    checkpointer=memory
)