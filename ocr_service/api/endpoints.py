from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ocr_service.core.dispatcher import dispatch
import traceback

router = APIRouter()

@router.post("/extract")
async def extract_document(
    file: UploadFile = File(...),
    engine: str = Form("auto", description="Options: auto, tesseract, gemini, ocrspace")
):
    
    # Receives an academic document (Image or PDF) and returns a structured JSON payload.
    try:
        file_bytes = await file.read()
        # Run the file through unified pipeline
        result = dispatch(file.filename, file_bytes, engine)
        
        if "error" in result and result["error"]:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Extraction pipeline failed: {str(e)}")