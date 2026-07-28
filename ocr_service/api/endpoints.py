from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from core.dispatcher import dispatch
from models.schemas import OCRResponse

app = FastAPI(title="OCR Service")

@app.post("/api/v1/extract", response_model=OCRResponse)
async def extract_text(
    file: UploadFile = File(...),
    ocr_engine: str = Form(default="auto", description="Options: auto, tesseract, gemini, ocrspace")
):
    # 1. Read the file into memory asynchronously
    file_bytes = await file.read()
    
    try:
        # 2. Pass filename, bytes, and the chosen engine to the dispatcher
        result = dispatch(file.filename, file_bytes, ocr_engine)
        return OCRResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))