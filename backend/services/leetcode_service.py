import httpx
import json
from database import get_db

async def get_problem_data(slug: str) -> dict:
    # 1. Check Cache
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM problems WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "title": row["title"],
                "difficulty": row["difficulty"],
                "pattern_tags": json.loads(row["pattern_tags"])
            }
    
    # 2. Fetch from LeetCode GraphQL
    query = """
    query getQuestion($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        title
        difficulty
        topicTags {
          name
        }
      }
    }
    """
    
    variables = {"titleSlug": slug}
    url = "https://leetcode.com/graphql"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()
        
    question_data = data.get("data", {}).get("question")
    if not question_data:
        raise ValueError("Problem not found")
        
    title = question_data["title"]
    difficulty = question_data["difficulty"]
    tags = [tag["name"] for tag in question_data.get("topicTags", [])]
    
    # 3. Cache into DB
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO problems (slug, title, difficulty, pattern_tags) VALUES (?, ?, ?, ?)",
            (slug, title, difficulty, json.dumps(tags))
        )
        db.commit()
        problem_id = cursor.lastrowid
        
    return {
        "id": problem_id,
        "title": title,
        "difficulty": difficulty,
        "pattern_tags": tags
    }
