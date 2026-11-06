from fastapi import APIRouter, HTTPException, Depends
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from api.schemas.chat_schemas import ChatRequest
from mas_orchestrator.graphs.chat_graph import chat_router

from api.database import get_db

router = APIRouter(prefix="/chat", tags=["Conversational Tutor"])

@router.post("/invoke")
async def invoke_chat_tutor(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Standard REST endpoint to test the conversational agent.
    Maintains memory across requests using thread_id
    """
    try:
        # Config memory tracking for specific convers thread
        config = {"configurable": {"thread_id": request.thread_id}}
        
        report_str = "Aucun rapport d'évaluation disponible."
        
        if request.session_id:
            raw_report_dict = fetch_student_report_context(request.session_id, db)
            if raw_report_dict:
                report_str = json.dumps(raw_report_dict, ensure_ascii=False, indent=2)

        # state payload
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "student_id": request.student_id,
            "student_report": report_str
        }
        # exec cyclic graph
        result = chat_router.invoke(input_state, config=config)
        final_message_content = result["messages"][-1].content
        
        # concatenate Gemini array -> 1 string
        clean_text = ""
        if isinstance(final_message_content, list):
            for block in final_message_content:
                if isinstance(block, dict) and block.get("type") == "text":
                    clean_text += block.get("text", "")
        else:
            clean_text = final_message_content
        
        return {
            "thread_id": request.thread_id,
            "response": clean_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'orchestration: {str(e)}")
    

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