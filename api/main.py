from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import student, professor, auth
from ocr_service.main import app as ocr_app


tags_metadata = [
    {"name": "Student Interface", "description": "Endpoints for student submissions and verification."},
    {"name": "Professor Interface", "description": "Endpoints for professor review and approval."},
    {"name": "Health Check", "description": "Basic API status check."}
]

app = FastAPI(
    title="MAS Pedagogic API",
    description="Backend API for the AI-driven Multi-Agent Grading System",
    version="1.0.0"
)

# Configure CORS
# web frontend (React, Angular, etc.) can make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the endpoints from router files
app.mount("/ocr", ocr_app)
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(professor.router)

@app.get("/", tags=["Health Check"])
async def root():
    """Simple health check endpoint to verify the server is running."""
    return {"status": "online", "message": "MAS Pedagogic API is up and running."}

@app.on_event("startup")
async def startup_event():
    print("Server starting...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Server shutting down...")