import { initAuth } from './js/init.js';
import { setupChat } from './js/chat.js';
import { setupSessions } from './js/sessions.js';
import { setupModels } from './js/models.js';
import { setupSettings } from './js/settings.js';

class VigilApp {
    constructor() {
        this.currentUser = null;
        this.currentSession = null;
        this.token = localStorage.getItem('access_token');
    }

    async init() {
        if (!this.token) {
            this.showLoginModal();
        } else {
            await this.loadApp();
        }
    }

    showLoginModal() {
        const modal = document.getElementById('loginModal');
        modal.classList.add('active');
        initAuth(this);
    }

    async loadApp() {
        try {
            // Verify token is still valid
            const response = await fetch('/api/auth/me', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!response.ok) {
                this.token = null;
                localStorage.removeItem('access_token');
                this.showLoginModal();
                return;
            }

            this.currentUser = await response.json();
            document.getElementById('loginModal').classList.remove('active');
            document.getElementById('app').style.display = 'flex';

            // Setup all modules
            setupChat(this);
            setupSessions(this);
            setupModels(this);
            setupSettings(this);

            // Setup navigation
            this.setupNavigation();
            this.setupLogout();
        } catch (error) {
            console.error('Error loading app:', error);
            this.showLoginModal();
        }
    }

    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                navButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const viewName = btn.dataset.view;
                this.switchView(viewName);
            });
        });
    }

    switchView(viewName) {
        const views = document.querySelectorAll('.view');
        views.forEach(view => view.classList.remove('active'));
        
        const view = document.getElementById(`${viewName}View`);
        if (view) {
            view.classList.add('active');
        }
    }

    setupLogout() {
        document.getElementById('logoutBtn').addEventListener('click', () => {
            localStorage.removeItem('access_token');
            this.token = null;
            location.reload();
        });
    }

    setCurrentSession(sessionId) {
        this.currentSession = sessionId;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new VigilApp();
    window.vigilApp = app;
    app.init();
});
