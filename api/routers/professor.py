from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from api.schemas.api_schemas import ReviseReportRequest
from datetime import datetime
from shared.utils.db_utils import get_db_connection

router = APIRouter(prefix="/api/v1/professor", tags=["Professor Interface"])

class PendingReport(BaseModel):
    session_id: str
    professor_summary: str
    pedagogical_warning: str
    student_draft_report: str
    langue: str | None = None
    generated_at: datetime | None = None

class ProfessorResponse(BaseModel):
    message: str

class PhaseUpdate(BaseModel):
    phase_name: str = Field(..., description="The exact name of the C2PCT phase (e.g., 'Data and Planning')")
    score: int = Field(..., description="The revised score (0-3)")
    justification: str = Field(..., description="The revised justification for the score")


@router.get("/reports/pending", response_model= List[PendingReport])
async def get_pending_reports():
    """Fetches all reports waiting for professor approval from SQL Server."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT fr.SessionID, fr.ProfessorSummary, fr.PedagogicalWarning, fr.StudentDraftReport, fr.GeneratedAt, sb.Langue
                FROM FeedbackReports fr JOIN Submissions sb ON
                fr.SessionID = sb.SessionID
                WHERE ApprovalStatus = 'Pending'
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            reports = [
                PendingReport(
                    session_id=row.SessionID,
                    professor_summary=row.ProfessorSummary,
                    pedagogical_warning=row.PedagogicalWarning,
                    student_draft_report=row.StudentDraftReport,
                    langue=getattr(row, "Langue", None),
                    generated_at=str(getattr(row, "GeneratedAt", None)) if getattr(row, "GeneratedAt", None) else None
                )
                for row in rows
            ]
            return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database read error: {str(e)}")


@router.post("/reports/{session_id}/approve", response_model=ProfessorResponse)
async def approve_report(session_id: str):
    """Approves an AI-generated report exactly as-is."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE FeedbackReports SET ApprovalStatus = 'Approved' WHERE SessionID = ?",
                (session_id,)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Report {session_id} not found.")
            conn.commit()
        return ProfessorResponse(message=f"Report for session {session_id} approved.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")


@router.put("/reports/{session_id}/revise", response_model=ProfessorResponse)
async def revise_and_approve_report(session_id: str, request: ReviseReportRequest):
    """Overwrites the AI-generated text with the professor's edits and marks it as approved."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE FeedbackReports 
                SET ProfessorSummary = ?, PedagogicalWarning = ?, StudentDraftReport = ?, ApprovalStatus = 'Approved'
                WHERE SessionID = ?
            """
            cursor.execute(query, (
                request.professor_summary,
                request.pedagogical_warning,
                request.student_draft_report,
                session_id
            ))
            conn.commit()
        return ProfessorResponse(message=f"Report for session {session_id} successfully revised and approved.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")