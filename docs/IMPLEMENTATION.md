# CodeSignaly: Implementation Plan

This document outlines the step-by-step development phases for the CodeSignaly browser extension and local AI backend.

## Phase 0: Repository Scaffolding & Documentation

**Objective:** Establish the production-ready project structure and documentation.

*   **Initialize the Git Repository:** Create the root repository, initialize Git, and apply a standard `.gitignore` tailored for Python and OS files.
*   **Create the Docs Folder:** Store the `SRS.md` and this `IMPLEMENTATION.md` file in a dedicated `docs/` directory.
*   **Draft the Initial README:** Create `README.md` at the root with the project title, a brief summary, and placeholders for setup instructions.
*   **Directory Structure Setup:** Scaffold the decoupled architecture:
    *   `/extension` (Vanilla JS: `manifest.json`, `/content`, `/sidepanel`, `/assets`).
    *   `/backend` (FastAPI: `requirements.txt`, `/app`, `/tests`).

## Phase 1: The Python Backend & Database (FastAPI + SQLite)

**Objective:** Build the API foundation and database schemas.

*   **Environment Setup:** Inside `/backend`, initialize a Python virtual environment (`python -m venv venv`) and install dependencies: fastapi, uvicorn, sqlalchemy, and pydantic.
*   **Database Models:** Inside `/backend/app`, configure `database.py` for SQLite connection and define `models.py` with the two core tables: `Sessions` and `Messages`.
*   **Basic Endpoints:** Set up `main.py` and implement a `GET /health` endpoint to ensure the server runs, alongside a `POST /clear` endpoint to allow users to clear the current conversation history[cite: 3].
*   **Mock the Chat Endpoint:** Create `/routers/chat.py` and implement `POST /chat/stream`. Return a hardcoded Server-Sent Events (SSE) stream to verify routing before connecting the AI.

## Phase 2: Local AI Integration (Ollama)

**Objective:** Connect the API to the local language model.

*   **Ollama Setup:** Install Ollama on the host machine and pull the desired model (e.g., `ollama run llama3:8b`).
*   **FastAPI to Ollama Bridge:** Update the `POST /chat/stream` endpoint to use httpx or requests to send the payload to Ollama's local REST API (`http://localhost:11434/api/generate`).
*   **Context Management Logic:** Implement a utility in `prompt_engine.py` that fetches previous messages from SQLite, formats them, and enforces a token limit by truncating older messages before sending the prompt to Ollama.

## Phase 3: The Chrome Extension Frontend

**Objective:** Build the user interface and extract LeetCode context.

*   **Manifest & Boilerplate:** Configure `manifest.json` (Manifest V3) with required permissions: `sidePanel`, `scripting`, `activeTab`, and `storage`.
*   **The Side Panel UI:** Build the chat interface in `/sidepanel` using `sidepanel.html`, `sidepanel.css`, and `sidepanel.js`. Include a message container, input area, mode toggles (for Tutor Mode and Direct Mode), Clear Chat/New Session controls, and a Connection Status indicator[cite: 3].
*   **DOM Scraping (Content Script):** In `/content/content.js`, write JavaScript to target LeetCode's DOM classes and extract the problem title, difficulty level, description, constraints, and input/output examples[cite: 3].
*   **Monaco Editor Extraction:** Implement logic in `content.js` to extract the inner text of the Monaco editor lines to capture the user's active code.

## Phase 4: Integration & Prompt Engineering

**Objective:** Connect the frontend and backend, and refine the AI's Socratic behavior.

*   **Frontend-to-Backend Comms:** Update `sidepanel.js` to collect user input and scraped DOM data, then POST the JSON payload to the local FastAPI backend.
*   **Handling the Stream (SSE):** Implement JavaScript logic to parse the incoming Server-Sent Events from FastAPI and dynamically append tokens to the chat UI.
*   **Dual Mode System Prompts:** Finalize `prompt_engine.py` with strict system instructions for both interaction modes[cite: 3]. For Tutor Mode, ensure the AI acts as a tutor, evaluates time complexity, asks leading questions, and explicitly refuses to output direct code solutions; for Direct Mode, instruct the AI to provide concise explanations, algorithm summaries, and educational resources[cite: 3].

## Phase 5: Polish & Open Source Launch

**Objective:** Prepare the project for public showcase and GitHub deployment.

*   **Markdown Rendering:** Integrate a lightweight library (like marked.js) into the side panel to correctly render code snippets, bold text, and math formulas.
*   **Error Handling:** Implement UI loading states and graceful error messages (e.g., "Backend offline") when the FastAPI server is unreachable.
*   **Finalize the README:** Update `README.md` with an architecture diagram, exact installation instructions (for both the backend environment and the unpacked Chrome extension), and a GIF demonstrating the tutor in action.