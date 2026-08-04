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