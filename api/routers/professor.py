from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from api.schemas.api_schemas import ReviseReportRequest
from shared.utils.db_utils import get_db_connection

router = APIRouter(prefix="/api/v1/professor", tags=["Professor Interface"])

class PendingReport(BaseModel):
    session_id: str
    professor_summary: str
    pedagogical_warning: str
    student_draft_report: str
    language: str | None = None
    generated_at: str | None = None

class ProfessorResponse(BaseModel):
    message: str

@router.get("/reports/pending", response_model= List[PendingReport])
async def get_pending_reports():
    """Fetches all reports waiting for professor approval from SQL Server."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT SessionID, ProfessorSummary, PedagogicalWarning, StudentDraftReport, Langue, GeneratedAt
                FROM FeedbackReports 
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
                    language=getattr(row, "Langue", None),
                    generated_at=getattr(row, "GeneratedAt", None)
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