from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from mas_orchestrator.state.schemas import MASState
from mas_orchestrator.nodes.ocr_node import run_ocr_node
from mas_orchestrator.nodes.human_verify_node import run_human_verify_node
from mas_orchestrator.nodes.diagnostic_node import run_diagnostic_node
from mas_orchestrator.nodes.guidance_generation_node import run_guidance_node
from mas_orchestrator.nodes.rag_retrieve_node import run_rag_retrieve_node
from mas_orchestrator.nodes.correction_node import run_correction_node

def route_after_diagnostic(state: MASState) -> str:
    """
    Checks the diagnostic data. If unreadable, loops back to HIL.
    Otherwise, proceeds to the next stage (currently END).
    """
    if state.get("error"):
        return END
    diagnostic_data = state.get("diagnostic_data", {})
    is_readable = diagnostic_data.get("is_readable", True)
    if not is_readable:
        return "human_verify"
    return "rag_retrieve"


# Initialize the graph with schema
memory = MemorySaver()

def human_verify_node(state: MASState):
    return state

workflow = StateGraph(MASState)

# Add nodes
workflow.add_node("ocr", run_ocr_node)
workflow.add_node("human_verify", run_human_verify_node)
workflow.add_node("diagnostic", run_diagnostic_node)
workflow.add_node("rag_retrieve", run_rag_retrieve_node)
workflow.add_node("guidance", run_guidance_node)
workflow.add_node("correction", run_correction_node)

# Define the flow
workflow.set_entry_point("ocr")
workflow.add_edge("ocr", "human_verify")
workflow.add_edge("human_verify", "diagnostic")
workflow.add_conditional_edges(
    "diagnostic",
    route_after_diagnostic,
    {
        "human_verify": "human_verify",
        "rag_retrieve": "rag_retrieve"
    }
)
workflow.add_edge("diagnostic","rag_retrieve")
workflow.add_edge("rag_retrieve","guidance")
workflow.add_edge("guidance","correction")
workflow.add_edge("correction",END)


# Compile
mas_router = workflow.compile(
    checkpointer = memory,
    interrupt_before=["human_verify"]
)