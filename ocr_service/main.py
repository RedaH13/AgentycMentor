from fastapi import FastAPI
from ocr_service.api.endpoints import router as ocr_router


app = FastAPI(
    title="OCR Extraction Service",
    description="Independent API module for testing the OCR pipeline.",
    version="1.0.0"
)

app.include_router(ocr_router, prefix="/api/v1/ocr", tags=["Extraction"])

@app.get("/")
def health_check():
    """Simple root check to verify the server is live."""
    return {"status": "online", "module": "ocr_service"}