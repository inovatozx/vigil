export function setupSettings(app) {
    const themeSelect = document.getElementById('themeSelect');
    const languageSelect = document.getElementById('languageSelect');

    // Load saved preferences
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const savedLanguage = localStorage.getItem('language') || 'pt-BR';

    themeSelect.value = savedTheme;
    languageSelect.value = savedLanguage;
    applyTheme(savedTheme);

    themeSelect.addEventListener('change', (e) => {
        const theme = e.target.value;
        localStorage.setItem('theme', theme);
        applyTheme(theme);
    });

    languageSelect.addEventListener('change', (e) => {
        const language = e.target.value;
        localStorage.setItem('language', language);
        // In a real app, this would reload translations
        console.log('Language changed to:', language);
    })

    function applyTheme(theme) {
        if (theme === 'light') {
            document.documentElement.style.setProperty('--background-dark', '#f5f5f5');
            document.documentElement.style.setProperty('--background-light', '#ffffff');
            document.documentElement.style.setProperty('--text-primary', '#1a1a1a');
            document.documentElement.style.setProperty('--text-secondary', '#666666');
            document.documentElement.style.setProperty('--border-color', '#e0e0e0');
        } else {
            document.documentElement.style.setProperty('--background-dark', '#0f172a');
            document.documentElement.style.setProperty('--background-light', '#1e293b');
            document.documentElement.style.setProperty('--text-primary', '#f1f5f9');
            document.documentElement.style.setProperty('--text-secondary', '#cbd5e1');
            document.documentElement.style.setProperty('--border-color', '#334155');
        }
    }
}
