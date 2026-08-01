from typing import TypedDict, Dict, Any, Optional

class MASState(TypedDict):
    """Global state shared across all LangGraph nodes."""
    session_id: str
    user_role: str  # 'student' or 'professor'
    file_path: Optional[str]
    
    # Data payloads
    ocr_payload: Optional[Dict[str, Any]]
    diagnostic_data: Optional[Dict[str, Any]]  # For upcoming Diagnostic Agent

    current_step: Optional[str]
    
    # Final outputs and control flow
    final_response: Optional[str]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]