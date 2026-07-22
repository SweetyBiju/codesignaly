const BACKEND_URL = "http://localhost:8000";

async function updateBadge() {
    try {
        const response = await fetch(`${BACKEND_URL}/weakspots`);
        if (response.ok) {
            const weakspots = await response.json();
            const count = weakspots.length;
            chrome.action.setBadgeText({ text: count > 0 ? String(count) : "" });
            chrome.action.setBadgeBackgroundColor({ color: "#ef4444" });
        }
    } catch (e) {
        console.error("Failed to update badge", e);
    }
}

// Update on startup
chrome.runtime.onStartup.addListener(updateBadge);
chrome.runtime.onInstalled.addListener(updateBadge);

// Listen for messages from content script when session ends
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "session_ended") {
        updateBadge();
    }
});
