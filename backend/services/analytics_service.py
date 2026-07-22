from database import get_db
from datetime import datetime, timezone, timedelta
import math

def get_recency_weight(days_since: float) -> float:
    if days_since < 3:
        return 1.0
    elif days_since <= 7:
        return 0.85
    elif days_since <= 14:
        return 0.65
    else:
        return 0.4

def get_mastery_scores():
    now = datetime.now(timezone.utc)
    results = []
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM pattern_mastery")
        rows = cursor.fetchall()
        
        for row in rows:
            last_practiced = datetime.fromisoformat(row["last_practiced"])
            days_since = max(0, (now - last_practiced).total_seconds() / (24 * 3600))
            
            base_score = (row["problems_succeeded"] / row["problems_attempted"]) * 100.0 if row["problems_attempted"] > 0 else 0
            live_score = base_score * get_recency_weight(days_since)
            
            results.append({
                "pattern": row["pattern_name"],
                "score": round(live_score, 1),
                "days_since": int(math.floor(days_since)),
                "last_practiced": row["last_practiced"]
            })
            
    results.sort(key=lambda x: x["score"])
    return results

def get_weakspots():
    mastery_scores = get_mastery_scores()
    weakspots = []
    
    for item in mastery_scores:
        if item["score"] < 40:
            weakspots.append({
                "pattern": item["pattern"],
                "mastery_score": item["score"],
                "days_since": item["days_since"],
                "reason": f"Low mastery score ({item['score']})"
            })
        elif item["days_since"] > 7:
            weakspots.append({
                "pattern": item["pattern"],
                "mastery_score": item["score"],
                "days_since": item["days_since"],
                "reason": f"Not practiced in {item['days_since']} days"
            })
            
    return weakspots

def get_stats():
    now = datetime.now(timezone.utc)
    with get_db() as db:
        cursor = db.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM sessions")
        total_sessions = cursor.fetchone()["count"]
        
        cursor.execute("SELECT started_at FROM sessions ORDER BY started_at DESC")
        rows = cursor.fetchall()
        
    weakspots = get_weakspots()
    
    practiced_dates = set()
    for row in rows:
        dt = datetime.fromisoformat(row["started_at"])
        practiced_dates.add(dt.date())
        
    sorted_dates = sorted(list(practiced_dates), reverse=True)
    
    streak = 0
    current_date = now.date()
    
    if sorted_dates and sorted_dates[0] == current_date:
        pass
    elif sorted_dates and (current_date - sorted_dates[0]).days == 1:
        current_date = sorted_dates[0]
    else:
        sorted_dates = [] # Streak is broken if not practiced today or yesterday
        
    for d in sorted_dates:
        if d == current_date:
            streak += 1
            current_date = current_date - timedelta(days=1)
        else:
            break
                
    return {
        "total_sessions": total_sessions,
        "streak": streak,
        "weakspot_count": len(weakspots)
    }
