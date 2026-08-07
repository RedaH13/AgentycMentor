import uuid
import json
from mas_orchestrator.graphs.router_graph import mas_router

def print_step(node_name: str, payload: dict):
    """Helper to beautifully print the JSON output of each agent."""
    print(f"\n{'='*20} 🟢 NODE FINISHED: {node_name.upper()} {'='*20}")
    # We use default=str to handle any non-serializable objects (like datetimes)
    print(json.dumps(payload, indent=4, default=str))
    print(f"{'='*65}\n")

def run_visualization():
    # 1. Mock the initial state that your FastAPI endpoint would normally create
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # We will use a hardcoded student_id and fake a file path for this test
    initial_state = {
        "session_id": thread_id,
        "student_id": 999, 
        "user_role": "student",
        "file_path": "test_upload.pdf" 
    }

    print("\n🚀 STARTING LANGGRAPH EXECUTION: PART 1 (Pre-Verification)")
    
    # 2. Run the first half of the graph (OCR -> human_verify breakpoint)
    # stream_mode="updates" only outputs the new data added by the current node
    for event in mas_router.stream(initial_state, config=config, stream_mode="updates"):
        for node_name, state_update in event.items():
            print_step(node_name, state_update)

    # 3. Simulate the Human-in-the-Loop 
    print("\n⏸️ GRAPH PAUSED AT BREAKPOINT: 'human_verify'")
    input("Press Enter to simulate the UI sending the corrected text and resuming...")
    
    # We pretend the student fixed some OCR typos and clicked "Submit"
    simulated_ui_payload = {
        "final_confirmed_text": "Calculate minimum transmission time for a 300 KB file given MTU is 1492 bytes. Speed is 56Kbps. My answer is 43.9 seconds because I divided size by speed."
    }
    
    # Inject the corrected text into the state
    mas_router.update_state(config, simulated_ui_payload)
    print_step("human_ui_correction", simulated_ui_payload)

    print("\n▶️ RESUMING LANGGRAPH EXECUTION: PART 2 (AI Processing)")
    
    # 4. Run the rest of the graph (Diagnostic -> RAG -> Guidance -> Correction)
    # Passing 'None' tells LangGraph to pick up exactly where it left off
    for event in mas_router.stream(None, config=config, stream_mode="updates"):
        for node_name, state_update in event.items():
            print_step(node_name, state_update)

    print("\n✅ FULL PIPELINE COMPLETE.")
    
    # 5. Fetch and print the final aggregated state
    final_state = mas_router.get_state(config).values
    print("\n" + "*"*30 + " FINAL MAS STATE (JSON) " + "*"*30)
    print(json.dumps(final_state, indent=4, default=str))

if __name__ == "__main__":
    run_visualization()