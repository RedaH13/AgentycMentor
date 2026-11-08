from fastapi import APIRouter, HTTPException, Depends
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from api.schemas.chat_schemas import ChatRequest
from mas_orchestrator.graphs.chat_graph import chat_router
from api.dependencies import get_current_student

from api.database import get_db
from shared.utils.db_utils import log_chat_interaction
from shared.utils.db_utils import  get_student_threads, get_thread_messages

router = APIRouter(prefix="/chat", tags=["Conversational Tutor"])

def fetch_student_report_context(session_id: str, db: Session) -> dict:
    """
    Executes raw SQL queries via SQLAlchemy to fetch the student's grading context
    from FeedbackReports, PhaseEvaluations, and ProgressTracking
    """
    report_dict = {}

    # Fetch High-Level Feedback
    feedback_query = text("""
        SELECT ProfessorSummary, PedagogicalWarning 
        FROM FeedbackReports 
        WHERE SessionID = :session_id
    """)
    feedback_result = db.execute(feedback_query, {"session_id": session_id}).fetchone()
    
    if feedback_result:
        report_dict["FeedbackReport"] = {
            "ProfessorSummary": feedback_result.ProfessorSummary,
            "PedagogicalWarning": feedback_result.PedagogicalWarning
        }

    # Fetch Granular C2PCT Phase Scores
    phases_query = text("""
        SELECT PhaseName, Score, Justification 
        FROM PhaseEvaluations 
        WHERE SessionID = :session_id
    """)
    phases_result = db.execute(phases_query, {"session_id": session_id}).fetchall()
    
    if phases_result:
        report_dict["PhaseEvaluations"] = [
            {"PhaseName": row.PhaseName, "Score": row.Score, "Justification": row.Justification}
            for row in phases_result
        ]

    # Fetch Persistent Difficulties
    progress_query = text("""
        SELECT DifficultyText, Status 
        FROM ProgressTracking 
        WHERE SessionID = :session_id AND Status = 'Active'
    """)
    progress_result = db.execute(progress_query, {"session_id": session_id}).fetchall()
    
    if progress_result:
        report_dict["ProgressTracking"] = [
            {"DifficultyText": row.DifficultyText, "Status": row.Status}
            for row in progress_result
        ]

    # Return the dictionary if data found
    return report_dict if report_dict else None


@router.post("/invoke")
async def invoke_chat_tutor(
    request: ChatRequest, 
    db: Session = Depends(get_db),
    current_student: dict = Depends(get_current_student)
):
    try:
        # Security Check: Ensure only 'student' role can access the tutor
        config = {"configurable": {"thread_id": request.thread_id}}        
        report_str = "Aucun rapport d'évaluation disponible."
        
        # Fetch real DB data if session_id is provided
        if request.session_id:
            raw_report_dict = fetch_student_report_context(request.session_id, db)
            if raw_report_dict:
                report_str = json.dumps(raw_report_dict, ensure_ascii=False, indent=2)
                
        # LangGraph State
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "student_id": str(current_student.get("user_id")), 
            "student_report": report_str
        }
        
        # Exec Graph
        result = chat_router.invoke(input_state, config=config)
        final_message_content = result["messages"][-1].content
        
        # formatting
        clean_text = ""
        if isinstance(final_message_content, list):
            for block in final_message_content:
                if isinstance(block, dict) and block.get("type") == "text":
                    clean_text += block.get("text", "")
        else:
            clean_text = final_message_content
        
        try:
            jwt_user_id = current_student.get("user_id")
            if jwt_user_id:
                log_chat_interaction(
                    thread_id=request.thread_id,
                    session_id=request.session_id,
                    user_id=jwt_user_id,
                    user_message=request.message,
                    ai_response=clean_text
                )
        except Exception as log_err:
            print(f"Failed to log chat to SQL Server: {log_err}")
            
        return {
            "thread_id": request.thread_id,
            "response": clean_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'orchestration: {str(e)}")

@router.get("/threads")
async def fetch_user_threads(current_student: dict = Depends(get_current_student)):
    """Renvoie toutes les conversations passées de l'étudiant connecté."""
    user_id = current_student.get("user_id")
    threads = get_student_threads(user_id)
    return {"threads": threads}

@router.get("/threads/{thread_id}/messages")
async def fetch_thread_history(thread_id: str, current_student: dict = Depends(get_current_student)):
    """Renvoie les messages d'une conversation spécifique."""
    messages = get_thread_messages(thread_id)
    return {"messages": messages}