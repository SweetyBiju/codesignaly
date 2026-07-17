"""
Prompt Engine for CodeSignaly.

Handles context management: fetches conversation history from the database,
formats it for the Ollama chat API, and enforces a token limit by truncating
older messages. Also defines the Socratic system prompt.
"""

from typing import Optional
from sqlalchemy.orm import Session as DBSession
from .models import Message

# Approximate token limit for context window.
# llama3:8b supports ~8192 tokens; we reserve space for the response.
MAX_CONTEXT_TOKENS = 4096

# Rough estimate: 1 token ≈ 4 characters (for English text).
CHARS_PER_TOKEN = 4

SYSTEM_PROMPT = """You are CodeSignaly, a Socratic programming tutor embedded in a browser extension for LeetCode.

Your core rules:
1. **NEVER** provide direct code solutions. You are a tutor, not a code generator.
2. Ask leading questions to guide the student toward the answer themselves.
3. When the student shares their code, evaluate its time and space complexity and explain trade-offs.
4. If the student is stuck, give progressive hints — start vague, get more specific only if they remain stuck.
5. Encourage the student to think about edge cases and constraints.
6. When relevant, reference common algorithmic patterns (sliding window, two pointers, BFS/DFS, dynamic programming, etc.) without implementing them.
7. Keep your responses concise and focused. Use markdown formatting for clarity.
8. If the student asks you to just give the answer or write the code, politely refuse and redirect them with a guiding question.

You will receive the LeetCode problem context (title, description, constraints) and the student's current code when available. Use this context to provide targeted guidance."""


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a string using a character-based heuristic."""
    return len(text) // CHARS_PER_TOKEN


def build_context(
    db: DBSession,
    session_id: str,
    user_message: str,
    problem_context: Optional[str] = None,
) -> list[dict]:
    """
    Build the full message list for the Ollama chat API.

    Fetches previous messages from the database, formats them, and truncates
    older messages if the estimated token count exceeds MAX_CONTEXT_TOKENS.

    Args:
        db: The database session.
        session_id: The current chat session ID.
        user_message: The latest user message.
        problem_context: Optional LeetCode problem context (title, description, constraints, code).

    Returns:
        A list of message dicts in the format expected by Ollama's /api/chat endpoint:
        [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]
    """
    # Start with the system prompt
    system_content = SYSTEM_PROMPT
    if problem_context:
        system_content += f"\n\n--- LeetCode Problem Context ---\n{problem_context}"

    messages = [{"role": "system", "content": system_content}]

    # Fetch previous messages from the database, ordered by timestamp
    history = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.timestamp.asc())
        .all()
    )

    # Convert DB records to the chat format
    history_messages = [
        {"role": msg.role, "content": msg.content} for msg in history
    ]

    # Add the new user message
    history_messages.append({"role": "user", "content": user_message})

    # Calculate token budget remaining after system prompt
    system_tokens = estimate_tokens(system_content)
    available_tokens = MAX_CONTEXT_TOKENS - system_tokens

    # Truncate older messages if we exceed the budget.
    # We always keep the latest user message, then add as many recent
    # messages as fit within the token limit.
    selected = []
    current_tokens = 0

    # Walk backwards through history to keep the most recent messages
    for msg in reversed(history_messages):
        msg_tokens = estimate_tokens(msg["content"])
        if current_tokens + msg_tokens > available_tokens:
            continue  # Skip this message but keep checking smaller older ones
        selected.insert(0, msg)
        current_tokens += msg_tokens

    # Ensure the latest user message is always included
    if not selected or selected[-1]["content"] != user_message:
        selected = [{"role": "user", "content": user_message}]

    messages.extend(selected)
    return messages
