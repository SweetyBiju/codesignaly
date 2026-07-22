from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import problem_router, chat_router, session_router, analytics_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LeetCode AI Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(problem_router.router)
app.include_router(chat_router.router)
app.include_router(session_router.router)
app.include_router(analytics_router.router)
