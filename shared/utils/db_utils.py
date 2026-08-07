import pyodbc
import os

def get_db_connection():
    """Establishes a connection to SQL Server."""
    conn_str = os.getenv("SQL_SERVER_CONN_STR", "Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DB;UID=user;PWD=password;")
    return pyodbc.connect(conn_str)

def fetch_active_difficulties(student_id: int, subject: str) -> str:
    """Reads historical difficulties from SQL Server for the prompt."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT TOP 3 pt.DifficultyText
                FROM ProgressTracking pt
                JOIN Submissions s ON pt.SessionID = s.SessionID
                WHERE s.StudentID = ? AND s.Subject = ? AND pt.Status = 'Active'
                ORDER BY s.SubmissionDate DESC;
            """
            cursor.execute(query, (student_id, subject))
            rows = cursor.fetchall()            
            if not rows:
                return "No previous difficulties recorded."
            return "\n".join([f"- {row.DifficultyText}" for row in rows])
    except Exception as e:
        print(f"DB Read Error: {e}")
        return "Could not fetch historical data."

def save_new_difficulties(session_id: str, difficulties: list[str]):
    """Writes the newly found difficulties back to SQL Server."""
    if not difficulties:
        return
        
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO ProgressTracking (SessionID, DifficultyText, Status)
                VALUES (?, ?, 'Active');
            """
            for diff in difficulties:
                cursor.execute(query, (session_id, diff))
            conn.commit()
    except Exception as e:
        print(f"DB Write Error: {e}")


def ensure_submission_exists(session_id: str, student_id: int, subject: str, document_type: str = "Assignment"):
    """
    Ensures a submission record exists in the Submissions table
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                IF NOT EXISTS (SELECT 1 FROM Submissions WHERE SessionID = ?)
                BEGIN
                    INSERT INTO Submissions (SessionID, StudentID, Subject, DocumentType)
                    VALUES (?, ?, ?, ?)
                END
            """
            cursor.execute(query, (session_id, session_id, student_id, subject, document_type))
            conn.commit()
    except Exception as e:
        print(f"DB Ensure Submission Error: {e}")


def save_correction_results(session_id: str, correction_data: dict):
    """Writes the overall grade and C2PCT phase breakdown to SQL Server."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Prepare data for CorrectionResults
            total_score = correction_data.get("total_score", 0)
            passed = 1 if total_score >= 8 else 0 
            
            critical_errors_list = correction_data.get("critical_errors", [])
            # Convert the list of errors into a single string for SQL storage
            critical_errors_str = "\n".join([f"- {err}" for err in critical_errors_list]) if critical_errors_list else None

            # Insert into CorrectionResults
            query_main = """
                INSERT INTO CorrectionResults (SessionID, TotalScore, Passed, CriticalErrors)
                VALUES (?, ?, ?, ?);
            """
            cursor.execute(query_main, (session_id, total_score, passed, critical_errors_str))

            # Insert individual Phase Evaluations (Phases 1-5)
            academic_evaluations = correction_data.get("academic_evaluations", [])
            if academic_evaluations:
                query_phases = """
                    INSERT INTO PhaseEvaluations (SessionID, PhaseName, Score, Justification)
                    VALUES (?, ?, ?, ?);
                """
                for phase in academic_evaluations:
                    cursor.execute(query_phases, (
                        session_id,
                        phase.get("phase_name"),
                        phase.get("score"),
                        phase.get("justification")
                    ))
            conn.commit()            
    except Exception as e:
        print(f"DB Write Error (Correction Results): {e}")