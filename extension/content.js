// content.js
const BACKEND_URL = "http://localhost:8000";
let problemData = null;
let currentSessionId = null;
let hintsUsed = 0;
let chatHistory = [];

function getProblemSlug() {
    const pathParts = window.location.pathname.split('/');
    const problemIndex = pathParts.indexOf("problems");
    if (problemIndex !== -1 && pathParts.length > problemIndex + 1) {
        return pathParts[problemIndex + 1];
    }
    return null;
}

async function fetchProblemData(slug) {
    try {
        const response = await fetch(`${BACKEND_URL}/problem/${slug}`);
        if (response.ok) {
            problemData = await response.json();
            document.getElementById('problem-info').innerText = `${problemData.title} · ${problemData.difficulty}`;
            document.getElementById('start-session-btn').disabled = false;
        } else {
            document.getElementById('problem-info').innerText = "Failed to load problem data.";
        }
    } catch (e) {
        console.error(e);
        document.getElementById('problem-info').innerText = "Backend not running.";
    }
}

function injectSidebar() {
    fetch(chrome.runtime.getURL('sidebar.html'))
        .then(response => response.text())
        .then(html => {
            const wrapper = document.createElement('div');
            wrapper.innerHTML = html;
            document.body.appendChild(wrapper.firstElementChild);
            
            setupEventListeners();
            
            const slug = getProblemSlug();
            if (slug) {
                fetchProblemData(slug);
            }
        });
}

function appendMessage(role, content) {
    const historyDiv = document.getElementById('chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role === 'model' || role === 'assistant' ? 'ai' : 'user'}`;
    msgDiv.innerText = content;
    historyDiv.appendChild(msgDiv);
    historyDiv.scrollTop = historyDiv.scrollHeight;
    
    if(role !== 'system') {
       chatHistory.push({ role, content });
    }
}

function setupEventListeners() {
    document.getElementById('start-session-btn').addEventListener('click', async () => {
        if (!problemData) return;
        
        document.getElementById('start-session-btn').disabled = true;
        document.getElementById('start-session-btn').innerText = "Starting...";
        
        try {
            const pattern = problemData.pattern_tags && problemData.pattern_tags.length > 0 
                ? problemData.pattern_tags[0] 
                : "Unknown";
                
            const response = await fetch(`${BACKEND_URL}/session/start`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    problem_id: problemData.id,
                    pattern: pattern
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                currentSessionId = data.session_id;
                
                document.getElementById('setup-view').style.display = 'none';
                document.getElementById('chat-view').style.display = 'flex';
                
                appendMessage('assistant', `Hello! I'm your interviewer today. We'll be working on ${problemData.title}. How would you approach this problem?`);
            }
        } catch (e) {
            console.error(e);
            alert("Failed to start session. Is backend running?");
            document.getElementById('start-session-btn').disabled = false;
            document.getElementById('start-session-btn').innerText = "Start Session";
        }
    });

    document.getElementById('send-btn').addEventListener('click', async () => {
        const inputStr = document.getElementById('chat-input').value.trim();
        if (!inputStr) return;
        
        document.getElementById('chat-input').value = "";
        appendMessage('user', inputStr);
        
        const pattern = problemData.pattern_tags && problemData.pattern_tags.length > 0 
                ? problemData.pattern_tags[0] 
                : "Unknown";

        try {
            const response = await fetch(`${BACKEND_URL}/chat/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: inputStr,
                    history: chatHistory.slice(0, -1).map(h => ({ role: h.role, content: h.content })),
                    problem_context: {
                        title: problemData.title,
                        difficulty: problemData.difficulty,
                        pattern: pattern
                    }
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                appendMessage('assistant', data.reply);
            }
        } catch(e) {
            console.error(e);
            appendMessage('assistant', "Network error connecting to AI.");
        }
    });

    document.getElementById('hint-btn').addEventListener('click', () => {
        hintsUsed++;
        document.getElementById('chat-input').value = "Can you give me a hint?";
        document.getElementById('send-btn').click();
    });

    document.getElementById('end-btn').addEventListener('click', () => {
        document.getElementById('chat-view').style.display = 'none';
        document.getElementById('outcome-view').style.display = 'block';
    });

    document.querySelectorAll('.outcome-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const outcome = e.target.getAttribute('data-outcome');
            try {
                await fetch(`${BACKEND_URL}/session/end`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: currentSessionId,
                        hints_used: hintsUsed,
                        outcome: outcome
                    })
                });
                
                document.getElementById('outcome-view').innerHTML = "<h3>Session Logged!</h3><p>Check your extension dashboard.</p>";
                chrome.runtime.sendMessage({ action: "session_ended" });
            } catch (err) {
                console.error(err);
                alert("Failed to log session");
            }
        });
    });
}

setTimeout(injectSidebar, 1500);

let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        const slug = getProblemSlug();
        if (slug && !document.getElementById('lc-ai-sidebar-container')) {
            injectSidebar();
        } else if (slug && document.getElementById('lc-ai-sidebar-container')) {
            document.getElementById('setup-view').style.display = 'block';
            document.getElementById('chat-view').style.display = 'none';
            document.getElementById('outcome-view').style.display = 'none';
            document.getElementById('start-session-btn').disabled = true;
            document.getElementById('start-session-btn').innerText = "Start Session";
            chatHistory = [];
            document.getElementById('chat-history').innerHTML = '';
            hintsUsed = 0;
            currentSessionId = null;
            fetchProblemData(slug);
        }
    }
}).observe(document, {subtree: true, childList: true});
