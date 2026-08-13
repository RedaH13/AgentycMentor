import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establishes a connection to SQL Server."""
    conn_str = os.getenv(
        "SQL_SERVER_CONN_STR", 
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=DESKTOP-CK7HVDE;"
        "Database=MAS_Pedagogic;"
        "Trusted_Connection=yes;")
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
                WHERE s.StudentID = ? AND s.Subject_Submission = ? AND pt.Status = 'Active'
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


def ensure_student_exists(student_id: int):
    """Ensures the student exists in the Students table to avoid FK violations."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                IF NOT EXISTS (SELECT 1 FROM Students WHERE StudentID = ?)
                BEGIN
                    SET IDENTITY_INSERT Students ON;
                    INSERT INTO Students (StudentID, UserIdentifier) 
                    VALUES (?, ?);
                    SET IDENTITY_INSERT Students OFF;
                END
            """
            user_ident = f"student_{student_id}"
            cursor.execute(query, (student_id, student_id, user_ident))
            conn.commit()
    except Exception as e:
        print(f"❌ DB Ensure Student Error: {e}")

def ensure_submission_exists(session_id: str, student_id: int, subject: str, document_type: str = "Assignment", submission_text: str = None, langue: str=None):
    """
    Ensures a submission record exists in the Submissions table
    """
    try:
        ensure_student_exists(student_id)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                IF NOT EXISTS (SELECT 1 FROM Submissions WHERE SessionID = ?)
                BEGIN
                    INSERT INTO Submissions (SessionID, StudentID, Subject_Submission, DocumentType, SubmissionText, Langue)
                    VALUES (?, ?, ?, ?, ?, ?)
                END
                ELSE
                BEGIN
                    UPDATE Submissions
                    SET SubmissionText = ?, Langue= ?
                    WHERE SessionID = ?
                END
            """
            cursor.execute(query, (
                session_id,
                session_id, student_id, subject, document_type, submission_text, langue,
                submission_text, langue, session_id
            ))
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
            
            # Insert into CorrectionResults
            query_main = """
                INSERT INTO CorrectionResults (SessionID, TotalScore, Passed)
                VALUES (?, ?, ?);
            """
            cursor.execute(query_main, (session_id, total_score, passed))
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

            critical_errors_list = correction_data.get("critical_errors", [])
            if critical_errors_list:
                query_errors = """
                    INSERT INTO CorrectionErrors (SessionID, ErrorText)
                    VALUES (?, ?);
                """
                for error_text in critical_errors_list:
                    cursor.execute(query_errors, (session_id, error_text))
            
            conn.commit()

            conn.commit()            
    except Exception as e:
        print(f"DB Write Error (Correction Results): {e}")


def save_feedback_report(session_id: str, feedback_data: dict):
    """Writes the segmented feedback data to SQL Server for the Power BI report."""
    if not feedback_data:
        return
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
            IF EXISTS (SELECT 1 FROM FeedbackReports WHERE SessionID = ?)
                UPDATE FeedbackReports
                SET ProfessorSummary = ?, PedagogicalWarning = ?, StudentDraftReport = ?, ApprovalStatus = 'Pending'
                WHERE SessionID = ?
            ELSE
                INSERT INTO FeedbackReports (SessionID, ProfessorSummary, PedagogicalWarning, StudentDraftReport, ApprovalStatus)
                VALUES (?, ?, ?, ?, 'Pending');
            """
            cursor.execute(query, (
                session_id, feedback_data.get("professor_summary", ""), feedback_data.get("pedagogical_warning", ""),
                feedback_data.get("student_draft_report", ""),
                session_id,
                
                session_id,
                feedback_data.get("professor_summary", ""),
                feedback_data.get("pedagogical_warning", ""),
                feedback_data.get("student_draft_report", "")
            ))
            conn.commit()
            print(f"DB: Saved Feedback Report for Session {session_id}")
            
    except Exception as e:
        print(f"DB Error (Save Feedback Report): {e}")