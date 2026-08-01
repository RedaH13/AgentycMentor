from langgraph.graph import StateGraph, END
from mas_orchestrator.state.schemas import MASState
from mas_orchestrator.nodes.ocr_node import run_ocr_node
# from mas_orchestrator.nodes.diagnostic_node import run_diagnostic_node

# Initialize the graph with your schema
workflow = StateGraph(MASState)

# Add nodes
workflow.add_node("ocr", run_ocr_node)
# workflow.add_node("diagnostic", run_diagnostic_node)

# Define the flow
workflow.set_entry_point("ocr")
# workflow.add_edge("ocr", "diagnostic")
workflow.add_edge("ocr", END)

# Compile
mas_router = workflow.compile()