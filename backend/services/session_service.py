from database import get_db
from datetime import datetime, timezone

def update_mastery(pattern: str, outcome: str):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM pattern_mastery WHERE pattern_name = ?", (pattern,))
        row = cursor.fetchone()
        
        now = datetime.now(timezone.utc)
        
        if not row:
            attempted = 1
            succeeded = 1 if outcome == "success" else 0
            # Recency weight is 1.0 immediately after practice
            mastery_score = (succeeded / attempted) * 100.0 * 1.0
            
            cursor.execute("""
                INSERT INTO pattern_mastery (pattern_name, problems_attempted, problems_succeeded, mastery_score, last_practiced)
                VALUES (?, ?, ?, ?, ?)
            """, (pattern, attempted, succeeded, mastery_score, now))
        else:
            attempted = row["problems_attempted"] + 1
            succeeded = row["problems_succeeded"] + (1 if outcome == "success" else 0)
            
            # Recency weight is 1.0 immediately after practice
            mastery_score = (succeeded / attempted) * 100.0 * 1.0
            
            cursor.execute("""
                UPDATE pattern_mastery
                SET problems_attempted = ?, problems_succeeded = ?, mastery_score = ?, last_practiced = ?
                WHERE pattern_name = ?
            """, (attempted, succeeded, mastery_score, now, pattern))
            
        db.commit()

def start_session(problem_id: int, pattern: str) -> tuple[int, str]:
    now = datetime.now(timezone.utc)
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO sessions (problem_id, pattern, started_at)
            VALUES (?, ?, ?)
        """, (problem_id, pattern, now))
        db.commit()
        return cursor.lastrowid, now.isoformat()

def end_session(session_id: int, hints_used: int, outcome: str) -> bool:
    now = datetime.now(timezone.utc)
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT pattern, started_at FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Session not found")
            
        started_at = datetime.fromisoformat(row["started_at"])
        time_taken = int((now - started_at).total_seconds())
        pattern = row["pattern"]
        
        cursor.execute("""
            UPDATE sessions
            SET ended_at = ?, time_taken_seconds = ?, hints_used = ?, outcome = ?
            WHERE id = ?
        """, (now, time_taken, hints_used, outcome, session_id))
        db.commit()
        
    update_mastery(pattern, outcome)
    return True
