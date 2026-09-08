from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from typing import Optional
from api.schemas.api_schemas import ReviseReportRequest
from datetime import datetime
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag_service.vectorstore.qdrant_client import get_qdrant_vector_store
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


class PhaseMetric(BaseModel):
    phase_name: str
    average_score: float

class ErrorMetric(BaseModel):
    error_text: str
    occurrence_count: int

class ClassMetricsResponse(BaseModel):
    total_submissions: int
    average_score: float
    pass_rate: float
    phase_averages: List[PhaseMetric]
    top_errors: List[ErrorMetric]


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
    

@router.get("/reports/past", response_model=List[PendingReport])
async def get_past_reports(user: dict = Depends(get_current_professor)):
    """Fetches all previously approved reports corrected by this professor."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    fr.SessionID, 
                    fr.ProfessorSummary, 
                    fr.PedagogicalWarning, 
                    fr.StudentDraftReport, 
                    fr.GeneratedAt, 
                    sb.Langue, 
                    st.UserIdentifier as student_name, 
                    sb.DocumentType as document_type, 
                    sb.Subject_Submission as subject_submission
                FROM FeedbackReports fr 
                JOIN Submissions sb ON fr.SessionID = sb.SessionID 
                JOIN Students st ON st.StudentID = sb.StudentID
                WHERE fr.ApprovalStatus = 'Approved' AND fr.CorrectedBy = ?
                ORDER BY fr.ApprovedAt DESC;
            """
            cursor.execute(query, (user["user_id"],))
            rows = cursor.fetchall()
            
            reports = []
            for row in rows:
                cursor.execute("SELECT PhaseName, Score, Justification FROM PhaseEvaluations WHERE SessionID = ?", (row.SessionID,))
                phases = [{"phase_name": p.PhaseName, "score": p.Score, "justification": p.Justification} for p in cursor.fetchall()]
                
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
    


@router.get("/metrics/class", response_model=ClassMetricsResponse)
async def get_class_metrics(user: dict = Depends(get_current_professor)):
    """Aggregates class performance metrics from approved reports."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Overview
            query_overview = """
                SELECT 
                    COUNT(cr.SessionID) as TotalSubmissions,
                    AVG(CAST(cr.TotalScore AS FLOAT)) as AverageScore,
                    SUM(CAST(cr.Passed AS INT)) as PassedCount
                FROM CorrectionResults cr
                JOIN FeedbackReports fr ON cr.SessionID = fr.SessionID
                WHERE fr.ApprovalStatus = 'Approved'
            """
            cursor.execute(query_overview)
            overview = cursor.fetchone()
            
            total_subs = overview.TotalSubmissions or 0
            avg_score = round(overview.AverageScore, 1) if overview.AverageScore else 0.0
            passed_count = overview.PassedCount or 0
            pass_rate = round((passed_count / total_subs) * 100, 1) if total_subs > 0 else 0.0

            # Phase Averages
            query_phases = """
                SELECT 
                    pe.PhaseName, 
                    AVG(CAST(pe.Score AS FLOAT)) as AvgScore
                FROM PhaseEvaluations pe
                JOIN FeedbackReports fr ON pe.SessionID = fr.SessionID
                WHERE fr.ApprovalStatus = 'Approved'
                GROUP BY pe.PhaseName
            """
            cursor.execute(query_phases)
            phase_averages = [
                PhaseMetric(phase_name=row.PhaseName, average_score=round(row.AvgScore, 2))
                for row in cursor.fetchall()
            ]

            # Top 5 critic Err
            query_errors = """
                SELECT TOP 5 
                    ce.ErrorText, 
                    COUNT(*) as OccurrenceCount
                FROM CorrectionErrors ce
                JOIN FeedbackReports fr ON ce.SessionID = fr.SessionID
                WHERE fr.ApprovalStatus = 'Approved'
                GROUP BY ce.ErrorText
                ORDER BY OccurrenceCount DESC
            """
            cursor.execute(query_errors)
            top_errors = [
                ErrorMetric(error_text=row.ErrorText, occurrence_count=row.OccurrenceCount)
                for row in cursor.fetchall()
            ]

            return ClassMetricsResponse(
                total_submissions=total_subs,
                average_score=avg_score,
                pass_rate=pass_rate,
                phase_averages=phase_averages,
                top_errors=top_errors
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database aggregation error: {str(e)}")
    

@router.post("/knowledge/upload", response_model=ProfessorResponse)
async def upload_course_material(
    file: UploadFile = File(...), 
    user: dict = Depends(get_current_professor)
):
    """Uploads a PDF, chunks it, and ingests it into Qdrant for RAG."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are currently supported for the Knowledge Base.")

    # Save uploaded file temporarily for LangChain's PDF loader
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        # 1. Load the PDF
        loader = PyPDFLoader(temp_path)
        documents = loader.load()
        
        # 2. Add metadata (so we know who uploaded it and what it is)
        for doc in documents:
            doc.metadata["professor_id"] = user["user_id"]
            doc.metadata["source_file"] = file.filename

        # 3. Chunk the text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        # 4. Push to Qdrant
        vector_store = get_qdrant_vector_store()
        vector_store.add_documents(chunks)

        return ProfessorResponse(message=f"Successfully ingested '{file.filename}' into the Knowledge Base. ({len(chunks)} vectors created)")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge Base ingestion failed: {str(e)}")
    finally:
        # Clean up the temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)