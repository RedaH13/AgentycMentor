import uuid
import json
from mas_orchestrator.graphs.router_graph import mas_router
import os

def save_student_answer_to_file(session_id: str, answer_text: str):
    """Save the student's raw/corrected answer to a text file for diagnosis."""
    folder = "diagnostics"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{session_id}_answer.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(answer_text)
    print(f"✅ Student answer saved to {file_path}")


def print_step(node_name: str, payload: dict):
    """Helper to beautifully print the JSON output of each agent."""
    print(f"\n{'='*20} 🟢 NODE FINISHED: {node_name.upper()} {'='*20}")
    # We use default=str to handle any non-serializable objects (like datetimes)
    print(json.dumps(payload, indent=4, default=str))
    print(f"{'='*65}\n")

def parse_ocr_json_to_text(ocr_payload) -> str:
    """
    Recursively searches a complex OCR JSON structure for 'line_text'
    and concatenates them into a single string.
    """
    extracted_lines = []
    
    def traverse(node):
        if isinstance(node, dict):
            # If we find a line of text, save it
            if "line_text" in node:
                extracted_lines.append(node["line_text"])
            # Otherwise, keep digging into the dictionary
            else:
                for key, value in node.items():
                    traverse(value)
        elif isinstance(node, list):
            # If it's a list, check every item inside
            for item in node:
                traverse(item)
                
    traverse(ocr_payload)
    # Join all found lines with a newline character
    return "\n".join(extracted_lines)

def run_visualization():
    # 1. Mock the initial state that your FastAPI endpoint would normally create
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # We will use a hardcoded student_id and fake a file path for this test
    initial_state = {
        "session_id": thread_id,
        "student_id": 999, 
        "user_role": "student",
        "file_path": "test/IMG_0635.jpeg" 
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
    current_state = mas_router.get_state(config).values

    raw_ocr_json = (
        current_state.get("extracted_text") or 
        current_state.get("final_confirmed_text") or 
        current_state.get("raw_text") or 
        current_state
    )
    actual_ocr_text = parse_ocr_json_to_text(raw_ocr_json)
    if not actual_ocr_text.strip():
        actual_ocr_text = "Failed to parse text from the OCR JSON structure."
    save_student_answer_to_file(thread_id, actual_ocr_text)

    simulated_ui_payload = {
        "final_confirmed_text": actual_ocr_text
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