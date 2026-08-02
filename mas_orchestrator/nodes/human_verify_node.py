from mas_orchestrator.state.schemas import MASState

def run_human_verify_node(state: MASState) -> dict:
    """
    landing pad for the Human-In-The-Loop (HIL) step.
    When the graph resumes, it ensures the state has the confirmed text.
    """
    # If the user didn't make edits, default to raw OCR text
    if not state.get("final_confirmed_text"):
        raw_text = state.get("ocr_payload", {}).get("full_text", "")
        return {"final_confirmed_text": raw_text}
    
    # If the user did provide edits, LangGraph's state update will already have injected it.
    return {}