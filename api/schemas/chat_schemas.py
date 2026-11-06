from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    student_id: str
    thread_id: str
    message: str
    session_id: Optional[str] = None