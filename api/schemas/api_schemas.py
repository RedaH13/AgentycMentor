from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# STUDENT SCHEMAS (Ingestion & Verification)
class StartPipelineRequest(BaseModel):
    student_id: int = Field(..., description="The ID of the student submitting the work.")
    # In a real frontend, the image would be sent as a multipart form data (UploadFile).
    # We include file_path here to simulate the payload for now.
    file_path: Optional[str] = Field(None, description="Path to the local file for processing.")

class VerifyTextRequest(BaseModel):
    session_id: str = Field(..., description="The session ID of the submission.")
    final_confirmed_text: str = Field(..., description="The OCR text confirmed or corrected by the student.")
    langue: Optional[str] = Field(None, description="Detected language of the submission text.")

class PipelineResponse(BaseModel):
    session_id: str
    status: str
    message: str
    langue: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# PROFESSOR SCHEMAS (Review & Approval)
class PhaseEvaluationUpdate(BaseModel):
    phase_name: str = Field(..., description="Name of the C2PCT phase")
    score: int = Field(..., description="Revised score (0-3)")
    justification: str = Field(..., description="Revised justification")

class ReviseReportRequest(BaseModel):
    professor_summary: str = Field(..., description="The manually edited executive summary.")
    pedagogical_warning: str = Field(..., description="The manually edited warning.")
    student_draft_report: str = Field(..., description="The manually edited student feedback.")
    professor_observations: Optional[str] = None

    critical_errors: Optional[List[str]] = Field(None, description="The final, approved list of critical error bullet points")
    total_score: Optional[int] = Field(None, description="The manually overridden total score")
    passed: Optional[bool] = Field(None, description="Manually overridden Pass/Fail status")
    phase_evaluations: Optional[List[PhaseEvaluationUpdate]] = Field(None, description="List of any phases the professor manually adjusted")