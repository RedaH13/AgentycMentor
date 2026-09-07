from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from typing import Optional
from api.schemas.api_schemas import ReviseReportRequest
from datetime import datetime
from shared.utils.db_utils import get_db_connection
from api.dependencies import get_current_professor

router = APIRouter(prefix="/api/v1/professor", tags=["Professor Interface"])

class PhaseEval(BaseModel):
    phase_name: str
    score: int
    justification: str

class PendingReport(BaseModel):
    session_id: str
    professor_summary: Optional[str] = None
    pedagogical_warning: Optional[str] = None
    student_draft_report: Optional[str] = None
    langue: Optional[str] = None
    generated_at: Optional[str] = None
    student_name: str
    subject_submission: str
    document_type: str
    phase_evaluations: List[PhaseEval] = []
    critical_errors: List[str] = []

class ProfessorResponse(BaseModel):
    message: str

@router.get("/reports/pending", response_model= List[PendingReport])
async def get_pending_reports(user: dict = Depends(get_current_professor)):
    """Fetches all reports waiting for professor approval from SQL Server."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT fr.SessionID, fr.ProfessorSummary, fr.PedagogicalWarning, fr.StudentDraftReport, fr.GeneratedAt, sb.Langue, 
                st.UserIdentifier as student_name, sb.DocumentType as document_type, sb.Subject_Submission AS subject_submission
                FROM FeedbackReports fr JOIN Submissions sb ON
                fr.SessionID = sb.SessionID JOIN Students st ON st.StudentID = sb.StudentID
                WHERE ApprovalStatus = 'Pending' 
                ORDER BY fr.GeneratedAt DESC;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            reports = []
            for row in rows:
                # 1. Fetch Phase Evaluations for this session
                cursor.execute("SELECT PhaseName, Score, Justification FROM PhaseEvaluations WHERE SessionID = ?", (row.SessionID,))
                phases = [{"phase_name": p.PhaseName, "score": p.Score, "justification": p.Justification} for p in cursor.fetchall()]
                
                # 2. Fetch Critical Errors for this session
                cursor.execute("SELECT ErrorText FROM CorrectionErrors WHERE SessionID = ?", (row.SessionID,))
                errors = [e.ErrorText for e in cursor.fetchall()]

                reports.append(
                    PendingReport(
                        session_id=row.SessionID,
                        professor_summary=row.ProfessorSummary,
                        pedagogical_warning=row.PedagogicalWarning,
                        student_draft_report=row.StudentDraftReport,
                        generated_at=str(getattr(row, "GeneratedAt", None)) if getattr(row, "GeneratedAt", None) else None,
                        langue=getattr(row, "Langue", None),
                        student_name=getattr(row, "student_name", "Unknown Student"),
                        document_type=getattr(row, "document_type", "Assignment"),
                        subject_submission=getattr(row, "subject_submission", "Unknown Subject"),
                        phase_evaluations=phases,
                        critical_errors=errors
                    )
                )
            return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database read error: {str(e)}")


@router.post("/reports/{session_id}/approve", response_model=ProfessorResponse)
async def approve_report(session_id: str, user: dict = Depends(get_current_professor)):
    """Approves an AI-generated report exactly as-is."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE FeedbackReports SET ApprovalStatus = 'Approved', CorrectedBy = ?, ApprovedAt = GETDATE() WHERE SessionID = ?",
                (user["user_id"],session_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Report {session_id} not found.")
            conn.commit()
        return ProfessorResponse(message=f"Report for session {session_id} approved.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")


@router.put("/reports/{session_id}/revise", response_model=ProfessorResponse)
async def revise_and_approve_report(session_id: str, request: ReviseReportRequest, user: dict = Depends(get_current_professor)):
    """Overwrites the AI-generated text with the professor's edits and marks it as approved."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE FeedbackReports 
                SET ProfessorSummary = ?, PedagogicalWarning = ?, StudentDraftReport = ?, 
                ProfessorObservations = ?, ApprovalStatus = 'Approved', 
                CorrectedBy = ?, ApprovedAt = GETDATE()
                WHERE SessionID = ?
            """
            cursor.execute(query, (
                request.professor_summary,
                request.pedagogical_warning,
                request.student_draft_report,
                request.professor_observations,
                user["user_id"],
                session_id
            ))

            if request.phase_evaluations:
                for phase in request.phase_evaluations:
                    cursor.execute("""
                        UPDATE PhaseEvaluations 
                        SET Score = ?, Justification = ?
                        WHERE SessionID = ? AND PhaseName = ?
                    """, (phase.score, phase.justification, session_id, phase.phase_name))
                cursor.execute("""SELECT SUM(Score) FROM PhaseEvaluations WHERE SessionID = ?""", (session_id,))
                total_score = cursor.fetchone()[0] or 0
                passed = 1 if total_score >= 10 else 0
                cursor.execute("""UPDATE CorrectionResults 
                        SET TotalScore = ?, Passed = ?, GradedAt = GETDATE() WHERE SessionID = ?""", (total_score, passed, session_id))
            
            if request.critical_errors is not None:
                cursor.execute("SELECT ErrorText FROM CorrectionErrors WHERE SessionID = ?", (session_id,))
                query_insert_error = "INSERT INTO CorrectionErrors (SessionID, ErrorText) VALUES (?, ?)"
                for error_text in request.critical_errors:
                    cursor.execute(query_insert_error, (session_id, error_text))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
            
            conn.commit()
        return ProfessorResponse(message=f"Report for session {session_id} successfully revised and approved.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")