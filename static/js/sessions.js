export function setupSessions(app) {
    const newSessionBtn = document.getElementById('newSessionBtn');
    const sessionsList = document.getElementById('sessionsList');

    newSessionBtn.addEventListener('click', createNewSession);
    loadSessions();

    async function loadSessions() {
        try {
            const response = await fetch('/api/sessions', {
                headers: { 'Authorization': `Bearer ${app.token}` }
            });
            if (response.ok) {
                const sessions = await response.json();
                sessionsList.innerHTML = '';
                sessions.forEach(session => {
                    const sessionItem = document.createElement('div');
                    sessionItem.className = 'session-item';
                    sessionItem.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3>${escapeHtml(session.title)}</h3>
                                <p style="font-size: 12px; color: var(--text-secondary);">
                                    ${new Date(session.updated_at).toLocaleString('pt-BR')}
                                </p>
                            </div>
                            <button class="delete-btn" data-id="${session.id}">🗑️</button>
                        </div>
                    `;
                    sessionItem.addEventListener('click', (e) => {
                        if (!e.target.classList.contains('delete-btn')) {
                            selectSession(session.id);
                        }
                    });
                    sessionItem.querySelector('.delete-btn').addEventListener('click', (e) => {
                        e.stopPropagation();
                        deleteSession(session.id);
                    });
                    sessionsList.appendChild(sessionItem);
                });
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
        }
    }

    async function createNewSession() {
        try {
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.token}`
                },
                body: JSON.stringify({ title: 'Nova Sessão' })
            });
            if (response.ok) {
                const session = await response.json();
                selectSession(session.id);
                loadSessions();
            }
        } catch (error) {
            console.error('Error creating session:', error);
        }
    }

    function selectSession(sessionId) {
        app.setCurrentSession(sessionId);
        document.getElementById('messagesContainer').innerHTML = '';
        // Switch to chat view
        document.querySelector('[data-view="chat"]').click();
    }

    async function deleteSession(sessionId) {
        if (confirm('Tem certeza que deseja deletar esta sessão?')) {
            try {
                const response = await fetch(`/api/sessions/${sessionId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${app.token}` }
                });
                if (response.ok) {
                    loadSessions();
                }
            } catch (error) {
                console.error('Error deleting session:', error);
            }
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
