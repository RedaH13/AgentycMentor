import uuid
from fastapi import UploadFile, File
from fastapi import APIRouter, HTTPException
from api.schemas.api_schemas import StartPipelineRequest, VerifyTextRequest, PipelineResponse
from mas_orchestrator.graphs.router_graph import mas_router

router = APIRouter(prefix="/api/v1/student", tags=["Student Interface"])

@router.post("/upload", response_model=PipelineResponse)
# def upload_submission(student_id: int, file: UploadFile= File(...)):
async def upload_submission(request: StartPipelineRequest):
    """Initiates the LangGraph pipeline up to the Human Verification breakpoint."""
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    initial_state = {
        "session_id": session_id,
        "student_id": request.student_id,
        "user_role": "student",
        "file_path": request.file_path or "mock_path.jpg"
    }
    
    try:
        # until the interrupt_before=["human_verify"]
        for _ in mas_router.stream(initial_state, config=config, stream_mode="updates"):
            pass 
            
        # Fetch the OCR output from the paused state
        current_state = mas_router.get_state(config).values
        extracted_text = current_state.get("extracted_text", "") # Adjust key if needed
        
        return PipelineResponse(
            session_id=session_id,
            status="paused_for_verification",
            message="OCR complete. Please verify the extracted text.",
            data={"extracted_text": extracted_text}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline initialization failed: {str(e)}")


@router.post("/{session_id}/verify", response_model=PipelineResponse)
async def verify_text(session_id: str, request: VerifyTextRequest):
    """Injects the corrected text and resumes the LangGraph pipeline."""
    config = {"configurable": {"thread_id": session_id}}
    
    try:
        # Update the state with the user's corrected text
        mas_router.update_state(config, {"final_confirmed_text": request.final_confirmed_text,
                                         "langue": request.langue or "Unknown"})
        
        # Resume the execution by passing None
        for _ in mas_router.stream(None, config=config, stream_mode="updates"):
            pass
        
        final_state = mas_router.get_state(config).values
        return PipelineResponse(
            session_id=session_id,
            status="completed",
            message="Pipeline executed successfully. Feedback is pending professor approval.",
            data={"feedback_data": final_state.get("feedback_data")}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline resumption failed: {str(e)}")