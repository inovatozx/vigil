export function setupChat(app) {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const modelSelect = document.getElementById('modelSelect');
    const messagesContainer = document.getElementById('messagesContainer');

    // Load available models
    loadModels();

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function loadModels() {
        try {
            const response = await fetch('/api/models', {
                headers: { 'Authorization': `Bearer ${app.token}` }
            });
            if (response.ok) {
                const models = await response.json();
                modelSelect.innerHTML = '';
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = `${model.provider}:${model.name}`;
                    option.textContent = `${model.provider}: ${model.name}`;
                    modelSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message || !app.currentSession) {
            alert('Selecione uma sessão e digite uma mensagem.');
            return;
        }

        const [provider, modelName] = modelSelect.value.split(':');

        // Add user message to UI
        addMessageToUI('user', message);
        chatInput.value = '';
        sendBtn.disabled = true;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.token}`
                },
                body: JSON.stringify({
                    session_id: app.currentSession,
                    message: message,
                    model: modelName,
                    llm_provider: provider
                })
            });

            if (response.ok) {
                let assistantMessage = '';
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.content) {
                                    assistantMessage += data.content;
                                    updateLastMessage(assistantMessage);
                                }
                            } catch (e) {
                                console.error('Error parsing message:', e);
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addMessageToUI('assistant', 'Erro ao processar a mensagem.');
        } finally {
            sendBtn.disabled = false;
        }
    }

    function addMessageToUI(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function updateLastMessage(content) {
        const messages = messagesContainer.querySelectorAll('.message');
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            if (lastMessage.classList.contains('assistant')) {
                lastMessage.querySelector('.message-content').textContent = content;
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
