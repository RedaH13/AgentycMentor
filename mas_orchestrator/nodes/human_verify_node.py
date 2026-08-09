from mas_orchestrator.state.schemas import MASState
from shared.utils.db_utils import ensure_submission_exists

def run_human_verify_node(state: MASState) -> dict:
    """
    landing pad for the Human-In-The-Loop (HIL) step.
    When the graph resumes, it ensures the state has the confirmed text.
    """
    if not state.get("final_confirmed_text"):
        raw_text = state.get("ocr_payload", {}).get("full_text", "")
        state["final_confirmed_text"] = raw_text
    
        ensure_submission_exists(session_id=state["session_id"],student_id=state["student_id"],
        subject=state.get("diagnostic_data", {}).get("subject", "Assignment"),document_type="Assignment",
        submission_text=state["final_confirmed_text"])

        return {}