import uuid, requests, os, httpx
from fastapi import UploadFile, File, APIRouter, HTTPException
from api.schemas.api_schemas import StartPipelineRequest, VerifyTextRequest, PipelineResponse
from mas_orchestrator.graphs.router_graph import mas_router

router = APIRouter(prefix="/api/v1/student", tags=["Student Interface"])

UPLOAD_DIR = "uploads"

@router.post("/upload", response_model=PipelineResponse)
async def upload_submission(student_id: int, file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    # Save file locally
    with open(file_path, "wb") as f:
        f.write(await file.read())
    try:
        # Call OCR microservice safely
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                resp = await client.post(
                    "http://127.0.0.1:8001/api/v1/ocr/extract",
                    files={"file": f},
                    data={"engine": "auto"},
                    timeout=30.0
                )
        ocr_result = resp.json()
        extracted_text = ocr_result.get("full_text", "")

        # Initialize pipeline state
        initial_state = {
            "session_id": session_id,
            "student_id": student_id,
            "user_role": "student",
            "file_path": file_path,
            "extracted_text": extracted_text,
            "langue": "Unknown"
        }
        mas_router.stream(initial_state, config=config, stream_mode="updates")

        current_state = mas_router.get_state(config).values
        return PipelineResponse(
            session_id=session_id,
            status="paused_for_verification",
            message="OCR complete. Please verify the extracted text.",
            langue=current_state.get("langue", "Unknown"),
            data={"extracted_text": current_state.get("extracted_text", extracted_text)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR call failed: {str(e)}")

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
            langue=final_state.get("langue"),
            data={"final_confirmed_text": final_state.get("final_confirmed_text")}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline resumption failed: {str(e)}")