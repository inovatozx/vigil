export function setupModels(app) {
    const modelsList = document.getElementById('modelsList');

    loadModels();

    async function loadModels() {
        try {
            const response = await fetch('/api/models', {
                headers: { 'Authorization': `Bearer ${app.token}` }
            });
            if (response.ok) {
                const models = await response.json();
                modelsList.innerHTML = '';
                models.forEach(model => {
                    const modelItem = document.createElement('div');
                    modelItem.className = 'model-item';
                    modelItem.innerHTML = `
                        <h3>${escapeHtml(model.name)}</h3>
                        <p style="font-size: 12px; color: var(--text-secondary);">
                            Provedor: ${escapeHtml(model.provider)}
                        </p>
                    `;
                    modelsList.appendChild(modelItem);
                });
            }
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
