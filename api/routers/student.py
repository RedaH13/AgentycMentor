import uuid, requests, os, httpx
from fastapi import UploadFile, File, APIRouter, HTTPException, Depends, Form, BackgroundTasks
from api.schemas.api_schemas import StartPipelineRequest, VerifyTextRequest, PipelineResponse
from mas_orchestrator.graphs.router_graph import mas_router
from api.dependencies import get_current_student
from shared.utils.db_utils import get_db_connection

router = APIRouter(prefix="/api/v1/student", tags=["Student Interface"])

UPLOAD_DIR = "uploads"

def call_ocr_service(file_path: str):
    # OCR is now mounted under /ocr/api/v1/ocr
    url = "http://127.0.0.1:8001/ocr/api/v1/ocr"
    files = {"file": open(file_path, "rb")}
    response = requests.post(url, files=files)
    response.raise_for_status()
    return response.json()

@router.post("/upload", response_model=PipelineResponse)
async def upload_submission(file: UploadFile = File(...),
                            engine: str = Form("auto"),
                            user: dict = Depends(get_current_student)):
    student_id = user["user_id"]
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save file locally
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    try:
        initial_state = {
            "session_id": session_id,
            "student_id": student_id,
            "user_role": "student",
            "file_path": file_path,
            "ocr_engine": engine,
        }
        
        async for _ in mas_router.astream(initial_state, config=config, stream_mode="updates"):
            pass
            
        current_state = mas_router.get_state(config).values
        if current_state.get("error"):
            raise HTTPException(status_code=500, detail=current_state["error"])
        extracted_text = current_state.get("extracted_text", "No text found in state")
        langue = current_state.get("langue", "Unknown")
        
        return PipelineResponse(
            session_id=session_id,
            status="paused_for_verification",
            message="OCR complete. Please verify the extracted text.",
            langue=langue,
            data={"extracted_text": extracted_text}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline initialization failed: {str(e)}")
    

@router.post("/{session_id}/verify", response_model=PipelineResponse)
async def verify_text(session_id: str, request: VerifyTextRequest, user: dict = Depends(get_current_student)):
    """Injects the corrected text and resumes the LangGraph pipeline."""
    student_id = user["user_id"]
    config = {"configurable": {"thread_id": session_id}}
    try:
        current_state = mas_router.get_state(config).values
        if not current_state:
            raise HTTPException(status_code=404, detail="Submission session not found or expired.")
        if str(current_state.get("student_id")) != str(student_id):
            raise HTTPException(status_code=403, detail="You do not have permission to modify this submission.")
            
        # Add as_node="human_verify" to force the graph to move forward
        mas_router.update_state(
            config, 
            {
                "final_confirmed_text": request.final_confirmed_text,
                "langue": request.langue or "Unknown",
                "student_id": student_id
            },
            as_node="human_verify" 
        )
        
        print(f"Resuming LangGraph for session: {session_id}")
        
        # Use ainvoke to force the entire graph to run to completion synchronously
        await mas_router.ainvoke(None, config=config)
        
        final_state = mas_router.get_state(config).values

        timing_metrics = final_state.get("timing_metrics", {})
        if timing_metrics:
            import json, os
            os.makedirs("analytics/outputs/benchmarks", exist_ok=True)
            log_file = f"analytics/outputs/benchmarks/{session_id}.json"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": session_id,
                    "student_id": student_id,
                    "timings": timing_metrics
                }, f, indent=2)
            print(f"Telemetry captured: {timing_metrics}")
        print("LangGraph execution finished")
        
        # If an agent crashes, alert the frontend
        if final_state.get("error"):
            print(f"Graph Error Detected: {final_state['error']}")
            raise HTTPException(status_code=500, detail=f"Agent Error: {final_state['error']}")

        return PipelineResponse(
            session_id=session_id,
            status="completed",
            message="Pipeline executed successfully. Feedback is pending professor approval.",
            langue=final_state.get("langue"),
            data={"final_confirmed_text": final_state.get("final_confirmed_text")}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline resumption failed: {str(e)}")

@router.get("/reports")
async def get_my_reports(user: dict = Depends(get_current_student)):
    """Fetches all past submissions and their grading status for the logged-in student."""
    user_id = user["user_id"]
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT StudentID FROM Students WHERE UserID = ?", (user_id,))
            student_row = cursor.fetchone()
            
            if not student_row:
                return []
                
            student_id = student_row[0]
            
            # fetch the joined report data
            query = """
                SELECT 
                    s.SessionID, 
                    s.Subject_Submission, 
                    s.DocumentType, 
                    s.SubmissionDate,
                    cr.TotalScore,
                    cr.Passed,
                    fr.ApprovalStatus
                FROM Submissions s
                LEFT JOIN CorrectionResults cr ON s.SessionID = cr.SessionID
                LEFT JOIN FeedbackReports fr ON s.SessionID = fr.SessionID
                WHERE s.StudentID = ?
                ORDER BY s.SubmissionDate DESC
            """
            cursor.execute(query, (student_id,))
            
            # Convert pyodbc rows to dict
            columns = [column[0] for column in cursor.description]
            reports = []
            for row in cursor.fetchall():
                reports.append(dict(zip(columns, row)))
                
            return reports
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")
    
@router.get("/reports/{session_id}")
async def get_report_details(session_id: str, user: dict = Depends(get_current_student)):
    """Fetches the full, detailed feedback report for a specific approved submission."""
    user_id = user["user_id"]
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT StudentID FROM Students WHERE UserID = ?", (user_id,))
            student_row = cursor.fetchone()
            if not student_row:
                raise HTTPException(status_code=404, detail="Student profile not found.")
            student_id = student_row[0]

            
            query = """
                SELECT 
                    s.Subject_Submission, s.DocumentType, s.SubmissionDate, s.SubmissionText, s.Langue,
                    cr.TotalScore, cr.Passed, cr.GradedAt,
                    fr.StudentDraftReport, fr.ApprovalStatus
                FROM Submissions s
                LEFT JOIN CorrectionResults cr ON s.SessionID = cr.SessionID
                LEFT JOIN FeedbackReports fr ON s.SessionID = fr.SessionID
                WHERE s.SessionID = ? AND s.StudentID = ?
            """
            cursor.execute(query, (session_id, student_id))
            report_row = cursor.fetchone()

            if not report_row:
                raise HTTPException(status_code=404, detail="Report not found or you do not have access.")
                
            if getattr(report_row, "ApprovalStatus", None) != 'Approved':
                raise HTTPException(status_code=403, detail="This report is still pending professor approval.")

            # Fetch Phase Evaluations
            cursor.execute("SELECT PhaseName, Score, Justification FROM PhaseEvaluations WHERE SessionID = ?", (session_id,))
            phases = [{"phase_name": p.PhaseName, "score": p.Score, "justification": p.Justification} for p in cursor.fetchall()]

            # Fetch Critical Errors
            cursor.execute("SELECT ErrorText FROM CorrectionErrors WHERE SessionID = ?", (session_id,))
            errors = [e.ErrorText for e in cursor.fetchall()]

            return {
                "session_id": session_id,
                "subject_submission": getattr(report_row, "Subject_Submission", "Unknown"),
                "document_type": getattr(report_row, "DocumentType", "Assignment"),
                "submission_date": getattr(report_row, "SubmissionDate", None),
                "submission_text": getattr(report_row, "SubmissionText", ""),
                "langue": getattr(report_row, "Langue", "Unknown"),
                "total_score": getattr(report_row, "TotalScore", 0),
                "passed": getattr(report_row, "Passed", False),
                "graded_at": getattr(report_row, "GradedAt", None),
                "student_feedback": getattr(report_row, "StudentDraftReport", ""), # Mapped for frontend
                "phase_evaluations": phases,
                "critical_errors": errors
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report details: {str(e)}")