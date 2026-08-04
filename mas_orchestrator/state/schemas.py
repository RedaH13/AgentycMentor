from typing import TypedDict, Dict, Any, Optional

class MASState(TypedDict):
    """Global state shared across all LangGraph nodes."""
    session_id: str
    student_id: Optional[int]
    user_role: str  # 'student' or 'professor'
    file_path: Optional[str]
    
    # Data payloads
    ocr_payload: Optional[Dict[str, Any]]
    final_confirmed_text: Optional[str]
    diagnostic_data: Optional[Dict[str, Any]]
    guidance_data: Optional[Dict[str, Any]]

    current_step: Optional[str]
    
    # Final outputs and control flow
    final_response: Optional[str]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]