```markdown
# Software Requirements Specification (SRS)

# CodeSignaly – AI-Powered LeetCode Tutor

---

# 1. Introduction

## 1.1 Purpose of the Document

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for **CodeSignaly**, an AI-powered tutoring system designed to help developers improve their problem-solving skills while practicing coding interview questions on LeetCode.

The purpose of this document is to provide a clear roadmap for the design, development, testing, and deployment of the application. It serves as a reference for developers, testers, project evaluators, and future contributors by documenting how the system is expected to behave, what technologies will be used, and what constraints must be followed throughout development.

Rather than acting as another AI solution that simply provides answers, CodeSignaly focuses on creating an interactive learning environment where users are guided toward solving problems independently.

---

## 1.2 Business Idea and Implementation Strategy

Many existing AI coding assistants solve programming problems instantly by generating complete solutions. While convenient, this often encourages dependency rather than learning.

CodeSignaly approaches this problem differently by implementing an AI tutor that follows the **Socratic method**. Instead of revealing the final solution, the system asks guiding questions, points out logical flaws, discusses edge cases, and encourages users to think critically before arriving at the answer.

The application follows a **hybrid architecture**, consisting of:

- A **Chrome Browser Extension** (Manifest V3) acting as the frontend.
- A **Python FastAPI** backend handling requests and maintaining conversation history.
- A **local Large Language Model (LLM)** running through Ollama for AI inference.

By running the AI model locally, the project eliminates recurring API costs while ensuring that users' code, conversations, and browsing data remain entirely on their own machines.

---

## 1.3 Scope of the Project

The scope of CodeSignaly includes designing and implementing a complete AI tutoring ecosystem capable of understanding the user's coding context directly from the browser.

The project includes:

- Developing a Chrome Extension capable of reading LeetCode problem information.
- Extracting the current problem statement, constraints, examples, and code editor contents.
- Creating a FastAPI backend responsible for prompt construction and conversation management.
- Maintaining conversational memory using SQLite.
- Integrating a locally hosted LLM through Ollama.
- Building a responsive chat interface inside Chrome's Side Panel.
- Supporting both guided tutoring and direct explanation modes.
- Implementing prompt engineering techniques to ensure educational responses rather than direct code generation.

The project does **not** include:

- Automatic code submission.
- **Automating code submissions or modifying the native LeetCode grading UI.**
- Cloud-based AI services.
- User account management.
- Online synchronization of conversations.

---

## 1.4 Overview of the Product

CodeSignaly is designed as a lightweight Chrome Extension that activates whenever a user opens a LeetCode problem.

Instead of switching between browser tabs or opening external AI tools, users can interact with an intelligent tutor directly inside the browser through a dedicated side panel.

The extension automatically understands the context of the current problem by collecting:

- Problem title
- Difficulty
- Description
- Constraints
- Examples
- User's current source code

Whenever the user asks for help, this contextual information is combined with the conversation history and sent to the local AI model.

The AI responds by encouraging analytical thinking instead of revealing the answer, making the learning experience similar to working with a real mentor.

---

# 2. General Description of the Project

## 2.1 Overall Architecture

CodeSignaly follows a modular three-layer architecture to ensure maintainability, scalability, and separation of responsibilities.

### Client Layer

The frontend consists of a Chrome Extension built using HTML, CSS, and JavaScript under the Manifest V3 specification.

Its responsibilities include:

- Rendering the user interface
- Opening the Chrome Side Panel
- Extracting problem information from the DOM
- Reading the Monaco Editor contents
- Sending requests to the backend
- Streaming AI responses to the interface

---

### Backend Layer

The backend is implemented using FastAPI.

Its primary responsibilities include:

- Managing API endpoints
- Creating and maintaining chat sessions
- Constructing prompts
- Storing conversation history
- Interacting with SQLite
- Communicating with the local AI model

This layer acts as the bridge between the browser extension and the LLM.

---

### AI Layer

The AI engine consists of a locally hosted language model running through Ollama.

Possible supported models include:

- Llama 3 8B
- DeepSeek Coder
- CodeGemma
- Mistral

The AI model receives structured prompts generated by the backend and produces tutoring responses in real time.

---

## 2.2 Core Functionalities

The system provides several integrated features that work together to create an effective learning environment.

### Automated Context Extraction

The extension automatically extracts:

- Problem title
- Difficulty level
- Full problem statement
- Constraints
- Input/output examples
- Current code inside the Monaco editor

This eliminates the need for users to manually copy and paste problem descriptions.

---

### Context-Aware Tutoring

The AI uses the extracted information along with previous conversation history to generate responses that remain relevant throughout the session.

Rather than restarting the conversation after every message, the AI understands:

- Previous hints
- User explanations
- Attempted approaches
- Existing code

This creates a more natural tutoring experience.

---

### Context Management

To ensure reliable performance with local language models that have limited context windows, the backend shall manage the amount of information sent to the AI during each request.

The system will monitor the total prompt size and, when necessary:

- Truncate older conversation messages.
- Summarize earlier parts of the conversation while preserving important context.
- Prioritize the current problem description, latest source code, and most recent interactions.

This mechanism prevents exceeding the model's context window while maintaining a coherent tutoring experience.

---

### Dual Learning Modes

The application provides two interaction modes.

**Tutor Mode**

- Gives hints
- Asks leading questions
- Discusses time complexity
- Explains concepts
- Encourages problem-solving

**Direct Mode**

When users simply want to revise a topic quickly, Direct Mode provides:

- Concise explanations
- Algorithm summaries
- Markdown notes
- Educational resources
- Video recommendations

---

## 2.3 Intended Users

The application is designed for learners across different experience levels.

Primary users include:

- Computer Science students
- Coding interview candidates
- Competitive programmers
- Software engineering interns
- Professional developers preparing for technical interviews

Users are expected to have basic programming knowledge but may require assistance in algorithm design, optimization techniques, and debugging strategies.

---

## 2.4 Target Platform and Distribution

The application is intended for desktop environments using Google Chrome or Chromium-based browsers.

The primary distribution platform will be the Chrome Web Store.

The backend and AI model are installed locally by the user, allowing the extension to operate without dependence on external AI services.

---

## 2.5 Key Features and Benefits

CodeSignaly emphasizes learning rather than solution generation.

Major benefits include:

- Encourages independent problem-solving
- Preserves user privacy through local execution
- Eliminates recurring AI API costs
- Provides conversational tutoring instead of static hints
- Maintains long-term context during discussions
- Offers flexible learning modes depending on user needs

---

# 3. Functional Requirements

## 3.1 System Workflow

The expected workflow is designed to minimize user interaction while maximizing contextual understanding.

### Typical User Flow

1. User opens a LeetCode problem.
2. User launches the Chrome extension.
3. The side panel opens automatically.
4. The extension extracts the problem statement and current source code.
5. The user asks a question.
6. The backend retrieves previous conversation history.
7. A structured prompt is generated.
8. The prompt is sent to the local LLM.
9. The AI streams its response back to the side panel.
10. The conversation is stored for future context.

---

## 3.2 Functional Modules

### Problem Extraction Module

Responsibilities include:

- Reading DOM elements
- Extracting metadata
- Monitoring code changes
- Identifying the current problem

---

### Chat Management Module

Responsible for:

- Creating sessions
- Loading previous messages
- Maintaining conversational memory
- Clearing conversations when requested

---

### Prompt Generation Module

The backend constructs structured prompts containing:

- Problem context
- Current source code
- Previous conversation
- Active tutoring mode
- System instructions

This ensures that the AI always has sufficient context before generating a response.

---

### AI Response Module

The backend communicates with Ollama and streams generated responses using Server-Sent Events (SSE).

Streaming provides a smoother user experience by displaying tokens as they are generated.

---

## 3.3 Database Design

SQLite is used as the local persistence layer because it is lightweight, portable, and requires no additional server setup.

### Sessions Table

| Field | Description |
|--------|-------------|
| session_id | Primary key |
| problem_slug | Unique problem identifier |
| created_at | Session creation timestamp |

---

### Messages Table

| Field | Description |
|--------|-------------|
| message_id | Primary key |
| session_id | Foreign key |
| role | User or Assistant |
| content | Message text |
| timestamp | Creation time |

---

### Processing Logic

Whenever a user submits a message:

1. Current problem information is extracted.
2. Current source code is collected.
3. Previous conversation history is loaded.
4. The backend constructs the final prompt.
5. The LLM generates a response.
6. Both user and assistant messages are stored in SQLite.

---

## 3.4 Development Phases

The project will be completed in multiple stages.

### Phase 1 – Environment Setup

- Create project structure
- Configure FastAPI
- Initialize Chrome Extension
- Install Ollama

---

### Phase 2 – Browser Integration

- DOM scraping
- Monaco editor extraction
- Side Panel implementation

---

### Phase 3 – Backend Development

- SQLite integration
- Session management
- API development
- SSE implementation

---

### Phase 4 – AI Prompt Engineering

- Tutor Mode prompts
- Direct Mode prompts
- Prompt injection resistance
- Response quality testing

---

### Phase 5 – UI Refinement

- Markdown rendering
- Improved responsiveness
- User experience enhancements
- Chrome Web Store preparation

---

# 4. Non-Functional Requirements

## 4.1 Performance

The system should provide responsive interactions despite running a local language model.

Performance goals include:

- Backend startup within a few seconds.
- Chat response initiation within approximately 2–5 seconds on supported hardware.
- Smooth token-by-token streaming of AI responses.
- Minimal memory usage by the browser extension.
- Efficient context management to ensure prompts remain within the supported token limit of the selected local language model.

---

## 4.2 Security

Security is achieved through local execution and restricted browser permissions.

Key requirements include:

- Manifest V3 compliance.
- No remote code execution.
- Communication restricted to localhost.
- Secure handling of browser permissions.
- Sanitization of all user inputs before prompt construction.

---

## 4.3 Privacy

User privacy is a primary design objective.

The system shall:

- Avoid collecting analytics.
- Avoid transmitting source code externally.
- Store conversations only on the user's machine.
- Operate without requiring user accounts.

---

## 4.4 Reliability

The application should continue functioning reliably under normal operating conditions.

Requirements include:

- Graceful handling of backend failures.
- Automatic reconnection when the backend restarts.
- Protection against corrupted SQLite sessions.
- Recovery from interrupted AI responses.

---

## 4.5 Availability

The application requires internet connectivity only for accessing LeetCode.

Once the webpage has loaded:

- FastAPI
- SQLite
- Ollama

operate locally, allowing AI tutoring to continue independently of cloud services.

---

## 4.6 Prompt Safety

To preserve the educational purpose of the application, the backend should prevent attempts to manipulate the AI into revealing complete solutions.

Measures include:

- Strong system prompts
- Instruction hierarchy
- Prompt sanitization
- Conversation formatting
- Input validation

---

# 5. Interface Requirements

## 5.1 Browser Interface

The extension interacts with Chrome using official browser APIs.

These include:

- `chrome.tabs`
- `chrome.runtime`
- `chrome.storage`
- `chrome.scripting`
- `chrome.sidePanel`

These APIs enable secure interaction with browser tabs while maintaining compliance with Manifest V3.

---

## 5.2 Backend Interface

Communication between the extension and backend occurs through HTTP requests over localhost.

Primary endpoints include:

| Endpoint | Purpose |
|----------|----------|
| POST /chat/stream | Send user messages and stream AI responses |
| POST /clear | Clear conversation |
| GET /health | Backend health check |

Server-Sent Events (SSE) are used for streaming responses in real time.

---

## 5.3 AI Interface

The backend communicates with Ollama using its REST API.

Typical workflow:

1. Build prompt.
2. Send request to Ollama.
3. Receive streamed tokens.
4. Forward tokens to the browser.
5. Save conversation history.

---

## 5.4 User Interface

The primary interface is a responsive Chrome Side Panel.

The interface includes:

- Chat window
- Scrollable conversation history
- Markdown rendering
- Code formatting
- Message timestamps
- Loading indicators

Messages are visually separated into user and tutor responses to improve readability.

---

## 5.5 User Controls

The interface provides a minimal set of controls to keep interactions simple and distraction-free.

Available controls include:

- **Tutor Mode** – Enables guided, Socratic-style assistance through hints and questions.
- **Direct Mode** – Provides concise explanations, reference material, or learning resources.
- **Clear Chat** – Deletes the current conversation history for the active problem.
- **New Session** – Starts a fresh tutoring session while preserving previous sessions in the database.
- **Connection Status** – Displays the availability of the local FastAPI server and AI model.

These controls allow users to adapt the tutoring experience based on their learning preferences while keeping the interface intuitive and easy to navigate.

---
```
