# Implementation Plan
## LeetCode AI Interview Coach — Chrome Extension

**Timeline:** 2 Days  
**Developer:** Solo  
**Target:** Working Prototype

---

## Table of Contents

1. [Tech Stack](#1-tech-stack)
2. [Project Structure](#2-project-structure)
3. [Build Order and Dependencies](#3-build-order-and-dependencies)
4. [Day 1 Plan — Core Plumbing](#4-day-1-plan--core-plumbing)
5. [Day 2 Plan — Intelligence + Polish](#5-day-2-plan--intelligence--polish)
6. [DSA Pattern Mapping Reference](#6-dsa-pattern-mapping-reference)
7. [Environment Setup Checklist](#7-environment-setup-checklist)
8. [Testing Checklist](#8-testing-checklist)
9. [Demo Script](#9-demo-script)

---

## 1. Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Chrome Extension | Manifest V3, Vanilla JS | No build step needed, faster to ship |
| Backend Framework | FastAPI (Python) | Auto docs, fast to write, async support |
| Database | SQLite3 (built-in Python) | Zero setup, local, no server needed |
| AI Model | Gemini 1.5 Flash via Google GenAI SDK | Free tier, fast responses, capable |
| LeetCode Data | LeetCode GraphQL API (unofficial) | Returns problem title, difficulty, tags |
| HTTP Client (backend) | httpx (async) | Works natively with FastAPI async routes |
| Environment Config | python-dotenv | Keeps API key out of source code |
| Extension ↔ Backend | fetch() to localhost:8000 | Simple, no extra libraries needed |

---

## 2. Project Structure

```
leetcode-ai-coach/
│
├── extension/                      # Chrome Extension
│   ├── manifest.json               # MV3 config
│   ├── background.js               # Service worker — routes messages
│   ├── content.js                  # Injected into LeetCode pages
│   ├── sidebar.html                # Sidebar template (injected by content.js)
│   ├── sidebar.css                 # Sidebar styles
│   ├── popup.html                  # Extension popup (dashboard)
│   ├── popup.js                    # Popup logic
│   ├── popup.css                   # Popup styles
│   └── icons/                      # Extension icons (16, 48, 128px)
│
├── backend/                        # Python FastAPI Backend
│   ├── main.py                     # FastAPI app entry point, CORS setup
│   ├── database.py                 # SQLite connection + table creation
│   ├── models.py                   # Pydantic request/response models
│   ├── services/
│   │   ├── leetcode_service.py     # LeetCode GraphQL calls + caching
│   │   ├── ai_service.py           # Gemini API calls + system prompt
│   │   ├── session_service.py      # Session start/end + logging
│   │   └── analytics_service.py   # Mastery scoring + weak spot logic
│   ├── routers/
│   │   ├── problem_router.py       # GET /problem/{slug}
│   │   ├── chat_router.py          # POST /chat
│   │   ├── session_router.py       # POST /session/start, /session/end
│   │   └── analytics_router.py    # GET /mastery, /weakspots, /stats
│   ├── data.db                     # SQLite database file (auto-created)
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # GEMINI_API_KEY=your_key (gitignored)
│
├── .gitignore
└── README.md
```

---

## 3. Build Order and Dependencies

The following dependency graph shows what must be built before each next step:

```
[Database setup]
      │
      ├──► [LeetCode Service]
      │         │
      │         └──► [Problem Router]  ──► [Content Script + Sidebar injection]
      │
      ├──► [Session Service]
      │         │
      │         └──► [Session Router]  ──► [Sidebar start/end buttons]
      │
      ├──► [AI Service]
      │         │
      │         └──► [Chat Router]  ──► [Sidebar chat UI]
      │
      └──► [Analytics Service]
                │
                └──► [Analytics Router]  ──► [Popup Dashboard]
```

**Rule:** Never build the extension side of a feature before its backend route is working and tested.

---

## 4. Day 1 Plan — Core Plumbing

**Goal by end of Day 1:** Open a LeetCode problem, see the sidebar, chat with the AI interviewer, and have the session logged to SQLite.

---

### Phase 1 — Backend Skeleton (2–3 hours)

**Step 1: Project setup**

```bash
mkdir leetcode-ai-coach && cd leetcode-ai-coach
mkdir backend extension
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install fastapi uvicorn httpx google-generativeai python-dotenv
pip freeze > requirements.txt
```

Create `.env`:
```
GEMINI_API_KEY=your_key_here
```

**Step 2: Database setup (`database.py`)**

Create three tables: `problems`, `sessions`, `pattern_mastery`.
Include a `get_db()` function that returns a connection.
Call `init_db()` on app startup to auto-create tables if they don't exist.

**Step 3: Main app (`main.py`)**

- Create FastAPI app instance
- Add CORS middleware — allow `chrome-extension://*` and `http://localhost`
- Call `init_db()` on startup
- Include all routers

> ⚠️ CORS is critical. Without it the extension's fetch() calls will be blocked by the browser.

---

### Phase 2 — LeetCode Service (1–1.5 hours)

**What it does:** Takes a slug like `two-sum`, queries LeetCode GraphQL, returns title + difficulty + tags. Caches the result in SQLite so we don't re-fetch.

**LeetCode GraphQL endpoint:** `https://leetcode.com/graphql`

**Query to use:**
```graphql
query getQuestion($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    difficulty
    topicTags {
      name
    }
  }
}
```

**Service logic:**
1. Check SQLite cache first — if found, return cached data
2. If not found, fire httpx POST to LeetCode GraphQL
3. Parse response, extract title + difficulty + tags array
4. Insert into `problems` table
5. Return to caller

**Test this route manually:**
```bash
curl http://localhost:8000/problem/two-sum
```
Expected: `{"id": 1, "title": "Two Sum", "difficulty": "Easy", "pattern_tags": ["Array", "Hash Table"]}`

---

### Phase 3 — AI Service (1–1.5 hours)

**What it does:** Takes the conversation history + problem context, adds a strict system prompt, calls Gemini, returns the reply.

**System prompt (enforce this strictly):**
```
You are a technical interviewer at a top tech company conducting a coding interview.
The candidate is attempting: {problem_title} (Difficulty: {difficulty}, Pattern: {pattern}).

Your rules:
- NEVER provide code or the solution
- Ask the candidate to explain their approach first
- Ask about time complexity and space complexity
- Challenge their reasoning with follow-up questions
- If they are stuck, guide with a question (never reveal the answer)
- Only give a hint if the user explicitly says "give me a hint"
- Keep each response to 2-3 sentences maximum
- Sound like a real interviewer, not a tutor
```

**Gemini call pattern:**
```python
import google.generativeai as genai

model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=conversation_history)
response = chat.send_message(user_message)
return response.text
```

**Test this manually with Postman or curl** before wiring it to the extension.

---

### Phase 4 — Session Service (30 min)

**Two operations:**

`start_session(problem_id, pattern)` → inserts row with `started_at = now()`, returns `session_id`

`end_session(session_id, hints_used, outcome)` → updates row: sets `ended_at`, computes `time_taken_seconds`, stores outcome, then calls `update_mastery(pattern, outcome)`

**`update_mastery(pattern, outcome)` logic:**
```python
# Upsert into pattern_mastery
# If row doesn't exist: insert with attempted=1, succeeded=(1 if success else 0)
# If row exists: increment attempted, increment succeeded if outcome=='success'
# Recompute mastery_score using formula from SRS
# Update last_practiced = now()
```

---

### Phase 5 — Chrome Extension Skeleton (1.5–2 hours)

**`manifest.json` — key fields:**
```json
{
  "manifest_version": 3,
  "name": "LeetCode AI Interview Coach",
  "version": "1.0",
  "permissions": ["activeTab", "scripting", "storage", "tabs"],
  "host_permissions": [
    "https://leetcode.com/*",
    "http://localhost:8000/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["https://leetcode.com/problems/*"],
    "js": ["content.js"],
    "css": ["sidebar.css"]
  }],
  "action": {
    "default_popup": "popup.html"
  }
}
```

**`content.js` — what it does:**
1. Extract slug from `window.location.pathname` (e.g. `/problems/two-sum/` → `two-sum`)
2. Fetch `http://localhost:8000/problem/{slug}` to get problem data
3. Create sidebar div, inject into `document.body`
4. Render sidebar HTML with problem title + difficulty badge
5. Add "Start Session" button handler
6. Add chat input + send button

**Sidebar layout (simple):**
```
┌─────────────────────────┐
│ 🎯 AI Interview Coach    │
│ Two Sum · Easy           │
│─────────────────────────│
│ [Start Session]          │
│─────────────────────────│
│ Chat history area        │
│                          │
│                          │
│─────────────────────────│
│ [Type your response...] │
│ [Send]   [Hint]  [End]  │
└─────────────────────────┘
```

**By end of Day 1, verify:**
- [ ] Sidebar appears on any `leetcode.com/problems/*` page
- [ ] Problem title and difficulty display correctly
- [ ] Chat with AI works (messages appear in sidebar)
- [ ] "End Session" logs the session (check SQLite with DB Browser)

---

## 5. Day 2 Plan — Intelligence + Polish

**Goal by end of Day 2:** Full working prototype with pattern mastery tracking, weak spot alerts, and a clean popup dashboard. Demo-ready.

---

### Phase 6 — Analytics Service (1.5 hours)

**`get_mastery_scores()`**
- Query all rows from `pattern_mastery`
- Apply recency weight to each score
- Return sorted by mastery_score ascending (weakest first)

**`get_weakspots()`**
- A pattern is a weak spot if:
  - `mastery_score < 40` (low accuracy), OR
  - `days_since_last_practiced > 7` (neglected)
- Return list with pattern name, score, days since, reason string

**`get_stats()`**
- Total sessions from `sessions` table
- Streak: count consecutive days (from today backwards) with at least one session
- Weak spot count

---

### Phase 7 — Popup Dashboard (2 hours)

**`popup.html` layout:**

```
┌─────────────────────────────┐
│  🎯 LeetCode AI Coach        │
│─────────────────────────────│
│  📊 Sessions: 24  🔥 Streak: 5d │
│─────────────────────────────│
│  ⚠️ WEAK SPOTS               │
│  Dynamic Programming  32%   │
│  "Low mastery + 9 days idle" │
│  Binary Search  61%          │
│  "Not practiced in 15 days"  │
│─────────────────────────────│
│  📈 PATTERN MASTERY          │
│  Arrays       ████████ 78%  │
│  Hash Table   ██████   61%  │
│  Sliding Win  ████     42%  │
│  DP           ███      32%  │
└─────────────────────────────┘
```

**`popup.js` logic:**
1. On load, call `/stats`, `/mastery`, `/weakspots` in parallel
2. Render stats bar (sessions + streak)
3. Render weak spot cards (yellow/red background)
4. Render mastery bars (color coded: red <40, yellow 40–70, green >70)

**Color scheme for mastery bars:**
```
0–39%   → #ef4444 (red)
40–69%  → #f59e0b (amber)
70–100% → #22c55e (green)
```

---

### Phase 8 — Badge + Alerts (30 min)

In `background.js`:
- On extension load and after each session ends, call `/weakspots`
- Set badge text to weak spot count:
```javascript
chrome.action.setBadgeText({ text: count > 0 ? String(count) : "" });
chrome.action.setBadgeBackgroundColor({ color: "#ef4444" });
```

---

### Phase 9 — Bug Fixes + Polish (1.5–2 hours)

Work through this list in order:

- [ ] Sidebar doesn't overlap problem editor (use `margin-right` on main content or absolute positioning on right edge)
- [ ] Sidebar state persists if user navigates between problems (re-fetch slug on URL change using MutationObserver)
- [ ] Error state if backend is not running (show "Start the backend server" message in sidebar)
- [ ] Empty state for popup if no sessions logged yet
- [ ] Hint counter increments correctly in session
- [ ] Session doesn't double-submit if user clicks End twice
- [ ] LeetCode GraphQL occasionally returns null — handle gracefully

---

### Phase 10 — Demo Prep (30 min)

- Load extension in Chrome (`chrome://extensions` → Developer mode → Load unpacked → select `extension/` folder)
- Start backend: `uvicorn main:app --reload`
- Solve 3–4 problems across different patterns to populate real data
- Verify popup shows mastery bars and at least one weak spot alert
- Screenshot the sidebar mid-conversation for submission docs

---

## 6. DSA Pattern Mapping Reference

LeetCode tags → internal pattern names used for mastery tracking:

| LeetCode Tags | Internal Pattern Name |
|---------------|----------------------|
| Array, Hash Table | Arrays & Hashing |
| Two Pointers | Two Pointers |
| Sliding Window | Sliding Window |
| Stack, Monotonic Stack | Stack |
| Binary Search | Binary Search |
| Linked List | Linked List |
| Tree, Binary Tree | Trees |
| Tries | Tries |
| Heap, Priority Queue | Heap / Priority Queue |
| Backtracking | Backtracking |
| Graph, BFS, DFS | Graphs |
| Dynamic Programming | Dynamic Programming |
| Greedy | Greedy |
| Intervals | Intervals |
| Bit Manipulation | Bit Manipulation |

> Use the first tag returned by LeetCode GraphQL as the primary pattern for a session.

---

## 7. Environment Setup Checklist

**Before writing a single line of code:**

- [ ] Python 3.10+ installed (`python --version`)
- [ ] pip available
- [ ] Google AI Studio account created → API key copied
- [ ] `.env` file created in `backend/` with `GEMINI_API_KEY=...`
- [ ] Chrome browser with Developer Mode enabled (`chrome://extensions`)
- [ ] DB Browser for SQLite installed (to inspect database during dev)
- [ ] Postman or Bruno installed (to test API routes manually)

---

## 8. Testing Checklist

**Backend (test each route with Postman before wiring extension):**

- [ ] `GET /problem/two-sum` → returns problem data
- [ ] `GET /problem/two-sum` again → returns same data (from cache, no new GraphQL call)
- [ ] `POST /chat` with dummy history → returns AI reply
- [ ] `POST /session/start` → returns session_id
- [ ] `POST /session/end` with session_id → returns success, check DB updated
- [ ] `GET /mastery` → returns pattern list (may be empty on first run)
- [ ] `GET /weakspots` → returns weak spots after a few sessions logged
- [ ] `GET /stats` → returns correct counts

**Extension:**
- [ ] Sidebar appears on `leetcode.com/problems/two-sum`
- [ ] Sidebar does NOT appear on `leetcode.com/` (homepage)
- [ ] Chat message sends and AI reply appears
- [ ] Hint button increments hint count
- [ ] End session + outcome selection works
- [ ] Popup opens and shows data
- [ ] Badge updates after session end

---

## 9. Demo Script

Use this order when demoing to show maximum impact:

1. **Open a LeetCode problem** → show sidebar auto-appearing, problem title detected
2. **Start session** → show AI's opening question
3. **Type an approach** → show AI follow-up questioning (not giving answers)
4. **Ask for a hint** → show hint is conditional, AI gives a nudge not a solution
5. **End session, mark as partial** → show session logged
6. **Open popup** → show mastery bar updated for that pattern
7. **Open another problem of same pattern, fail it** → show mastery score drop
8. **Open popup again** → show weak spot alert triggered
9. **Explain:** "This is stateful. It knows me. Ask Gemini on a tab cannot do this."

---

*End of Implementation Plan*
