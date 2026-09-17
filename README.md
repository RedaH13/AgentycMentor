# AgentycMentor

AgentycMentor is a **multi‑agent educational platform** designed to automate the evaluation of complex engineering submissions.  
Developed during an internship at **Universidad de Cádiz – Laboratorio de Resistencia de Materiales**, the system combines **OCR engines**, **LangGraph orchestration**, and the **C2PCT pedagogical framework** to accelerate grading cycles while preserving professor authority.

---

## 🚀 Core Features
- **Multi-Agent Orchestration**: Utilizes a directed cyclic graph to route reasoning through specialized agent personas (Diagnostic, Guidance, Correction, and Feedback).
- **Human-in-the-Loop (HIL) Ingestion**: A multi-engine OCR pipeline (Tesseract, OCR.Space, Gemini Vision) that actively pauses execution, requiring student verification of extracted text to prevent LLM hallucinations.
- **Pedagogical RAG Framework**: Grounds AI evaluations strictly in professor-uploaded syllabus materials stored in a high-performance ```Qdrant``` vector database.
- **C2PCT Methodological Grading**: Strict JSON schema contract that forces the LLM to output discrete 0-3 scores and pedagogical justifications across five specific cognitive phases (Data & Planning, Decomposition, Structuring, Transfer, Communication). 

---

## 📂 Project Structure
```text
Pedago-MAS/
|── alembic/              # Database migration scripts
├── analytics/            # Telemetry, latency, and accuracy benchmark scripts & outputs
├── api/                  # FastAPI backend routing, schemas, and database dependencies
├── data/                 # Local Qdrant storage and course material embeddings
├── frontend/             # Next.js (React) application for student/professor dashboards
├── llm_clients/          # Gemini API integrations and agent prompt definitions
├── mas_orchestrator/     # LangGraph multi-agent system state machine, nodes, and router
├── ocr_service/          # OCR microservice (Tesseract, pre/post-processing)
├── rag_service/          # Qdrant vector store and document ingestion pipeline
├── shared/               # Shared utilities (auth, logging, models, db_utils)
├── docker-compose.yml    # Container orchestration
└── requirements.txt      # Python dependencies
```
---

## 🛠️ Tech Stack
- **AI Framework**: LangChain, LangGraph
- **LLM**: Gemini API
- **OCR Microservice**: Tesseract, OCR.Space, Google Vision
- **Embeddings**: Google Gemini (`gemini-embedding-001`)   
- **Vector DB**: Qdrant (3072‑dimensional, cosine similarity)
- **Backend**: FastAPI, Python
- **Database**: SQL Server
- **Frontend**: Next.js(React)
- **Security**: JWT, bcrypt

---

## Installation & Setup
```bash
# Clone the repository
git clone https://github.com/RedaH13/pedago-mas.git
cd Pedago-MAS

python -m venv venv
venv\Scripts\activate

# Backend setup
pip install -r requirements.txt

# Run Qdrant locally
docker run -p 6333:6333 qdrant/qdrant

# Set up environment variables
cp .env.example .env
# Edit .env with your DB credentials, Qdrant URL, and Gemini API key

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn main:app --reload --port 8000

# Frontend setup
cd frontend
npm install
npm run dev
```
---

## 📊 Evaluation Metrics
- **OCR Confidence Distribution**: Avg global confidence ~54%, ~3,000 low‑certainty words  
- **CER/WER Accuracy**: Word error rates up to 86% on screenshot‑heavy submissions  
- **Latency Analysis**: Pipeline execution 8.8–12.8s; Guidance & Correction agents dominate  
- **Correction Agent Reliability**: F1‑Score up to 83% across diverse submissions  

---

## 📈 Future Perspectives
- Train a custom OCR vision model  
- Deploy distributed task queues  
- Automate feedback management  

---

## 👥 Collaboration
- **Reda Hadarbach** — Backend pipeline, LangGraph orchestration, Qdrant configuration  
- **Souad Cheikh** — Frontend integration, Next.js interfaces, demo preparation  

---


