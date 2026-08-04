import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from pydantic import BaseModel
from mas_orchestrator.graphs.router_graph import mas_router

router = APIRouter()

# Temporary local storage for uploaded files before processing
UPLOAD_DIR = "data/inputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class CorrectionPayload(BaseModel):
    corrected_text: str

@router.post("/process/start")
async def start_processing(student_id: int = Form(...), file: UploadFile = File(...)):
    """Upload the file, run OCR, and pause for human verification"""
    try:
        # Save file locally for the node to access
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Generate a unique thread ID for this user session
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Initialize the state
        initial_state = {
            "session_id": thread_id,
            "student_id": student_id,
            "user_role": "student",
            "file_path": file_path
        }
        # Run the graph. execute OCR and PAUSE before 'human_verify'
        mas_router.invoke(initial_state, config=config)
        # Fetch the current state at the breakpoint
        current_state = mas_router.get_state(config)
        state_values = current_state.values
        if "error" in state_values and state_values["error"]:
            raise HTTPException(status_code=400, detail=state_values["error"])
        raw_text = state_values.get("ocr_payload", {}).get("full_text", "")

        return {
            "message": "OCR complete. Awaiting human verification.",
            "thread_id": thread_id,
            "student_id": student_id,
            "raw_text": raw_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")


@router.post("/process/resume/{thread_id}")
async def resume_processing(thread_id: str, payload: CorrectionPayload = Body(...)):
    """
    Receive the corrected text from the UI, resume the graph, and return diagnostics.
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        
        # Verify the thread exists and is paused
        current_state = mas_router.get_state(config)
        if not current_state.next:
            raise HTTPException(status_code=400, detail="No active or paused session found for this thread ID.")

        # Update the LangGraph state with the student's confirmed text
        mas_router.update_state(
            config, 
            {"final_confirmed_text": payload.corrected_text}
        )
        # Resume the graph (passing None continues from the breakpoint)
        final_state = mas_router.invoke(None, config=config)
        if "error" in final_state and final_state["error"]:
             raise HTTPException(status_code=500, detail=final_state["error"])
        return {
            "message": "Processing complete.",
            "thread_id": thread_id,
            "diagnostic_data": final_state.get("diagnostic_data"),
            "guidance_data": final_state.get("guidance_data")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume processing: {str(e)}")
