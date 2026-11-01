from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    student_id: str
    thread_id: str
    message: str
    student_report: Optional[str] = "Aucun rapport d'évaluation disponible."