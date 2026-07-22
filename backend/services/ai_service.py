import google.generativeai as genai
import os
from models import ChatHistoryMessage, ProblemContext

def build_system_prompt(problem_context: ProblemContext) -> str:
    return f"""You are a technical interviewer at a top tech company conducting a coding interview.
The candidate is attempting: {problem_context.title} (Difficulty: {problem_context.difficulty}, Pattern: {problem_context.pattern}).

Your rules:
- NEVER provide code or the solution
- Ask the candidate to explain their approach first
- Ask about time complexity and space complexity
- Challenge their reasoning with follow-up questions
- If they are stuck, guide with a question (never reveal the answer)
- Only give a hint if the user explicitly says "give me a hint"
- Keep each response to 2-3 sentences maximum
- Sound like a real interviewer, not a tutor"""

async def get_chat_response(message: str, history: list[ChatHistoryMessage], problem_context: ProblemContext) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError("GEMINI_API_KEY not set in .env file.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=build_system_prompt(problem_context))
    
    formatted_history = []
    for msg in history:
        role = "model" if msg.role == "assistant" else "user"
        formatted_history.append({"role": role, "parts": [msg.content]})
        
    chat = model.start_chat(history=formatted_history)
    response = await chat.send_message_async(message)
    return response.text
