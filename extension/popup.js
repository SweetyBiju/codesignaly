const BACKEND_URL = "http://localhost:8000";

function getColorForScore(score) {
    if (score < 40) return "#ef4444"; // red
    if (score < 70) return "#f59e0b"; // amber
    return "#22c55e"; // green
}

async function loadData() {
    try {
        const [statsRes, weakspotsRes, masteryRes] = await Promise.all([
            fetch(`${BACKEND_URL}/stats`),
            fetch(`${BACKEND_URL}/weakspots`),
            fetch(`${BACKEND_URL}/mastery`)
        ]);

        const stats = await statsRes.json();
        const weakspots = await weakspotsRes.json();
        const mastery = await masteryRes.json();

        // Render Stats
        document.getElementById('total-sessions').innerText = stats.total_sessions || 0;
        document.getElementById('streak-count').innerText = `${stats.streak || 0}d`;

        // Render Weak Spots
        const weakspotsContainer = document.getElementById('weakspots-container');
        const weakspotsTitle = document.getElementById('weakspots-title');
        
        if (weakspots.length > 0) {
            weakspotsTitle.style.display = 'block';
            weakspotsContainer.innerHTML = weakspots.map(spot => `
                <div class="weakspot-card">
                    <div class="weakspot-header">
                        <span>${spot.pattern}</span>
                        <span>${Math.round(spot.mastery_score)}%</span>
                    </div>
                    <div class="weakspot-reason">${spot.reason}</div>
                </div>
            `).join('');
        } else {
            weakspotsTitle.style.display = 'none';
            weakspotsContainer.innerHTML = '';
        }

        // Render Mastery
        const masteryContainer = document.getElementById('mastery-container');
        if (mastery.length === 0) {
            masteryContainer.innerHTML = `<div style="text-align:center; padding: 20px; font-size:12px; color:#888;">No sessions recorded yet. Start practicing!</div>`;
        } else {
            // Sort by score descending (highest at top)
            mastery.sort((a, b) => b.score - a.score);
            masteryContainer.innerHTML = mastery.map(item => `
                <div class="mastery-row">
                    <div class="mastery-label">
                        <span>${item.pattern}</span>
                        <span>${Math.round(item.score)}%</span>
                    </div>
                    <div class="mastery-bar-bg">
                        <div class="mastery-bar-fill" style="width: ${Math.round(item.score)}%; background-color: ${getColorForScore(item.score)};"></div>
                    </div>
                </div>
            `).join('');
        }

    } catch (e) {
        console.error("Failed to load dashboard data", e);
        document.body.innerHTML = `<div style="padding: 20px; text-align: center;">Failed to connect to backend. Is it running?</div>`;
    }
}

document.addEventListener('DOMContentLoaded', loadData);
