from typing import TypedDict, Dict, Any, Optional,Annotated
from langgraph.graph.message import add_messages

class MASState(TypedDict):
    """Global state shared across all LangGraph nodes."""
    session_id: str
    student_id: Optional[int]
    user_role: str  # 'student' or 'professor'
    file_path: Optional[str]
    
    # Data payloads
    ocr_payload: Optional[Dict[str, Any]]
    extracted_text: Optional[str]
    final_confirmed_text: Optional[str]
    diagnostic_data: Optional[Dict[str, Any]]
    guidance_data: Optional[Dict[str, Any]]
    correction_data: Optional[Dict[str, Any]]
    feedback_data: Optional[Dict[str, Any]]

    retrieved_context: Optional[str]
    langue: Optional[str]

    current_step: Optional[str]
    
    # Final outputs and control flow
    final_response: Optional[str]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]

    timing_metrics: Dict[str, float]


class ChatState(TypedDict):
    """State strictly for the Conversational AI Tutor"""
    messages: Annotated[list, add_messages]
    student_id: str
    student_report: str