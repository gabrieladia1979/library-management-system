import { Navbar } from './components/navbar.js';
import { Router } from './router.js';
import { DashboardView } from './views/dashboard.js';
import { CatalogView } from './views/catalog.js';
import { BookDetailView } from './views/bookDetail.js';
import { UsersView } from './views/users.js';
import { LoansView } from './views/loans.js';
import { LoginView } from './views/login.js';
import { Toast } from './components/toast.js';
import { api } from './services/api.js';

class App {
    constructor() {
        this.router = new Router();
        this.init();
    }

    async init() {
        // Initialize global components
        const navbar = new Navbar();
        document.getElementById('navbar-container').innerHTML = navbar.render();
        navbar.attachEvents();

        // Register routes
        this.router.addRoute('login', () => new LoginView().render());
        this.router.addRoute('', () => new DashboardView().render());
        this.router.addRoute('catalog', () => new CatalogView().render());
        this.router.addRoute('book/:id', (params) => new BookDetailView(params.id).render());
        this.router.addRoute('users', () => new UsersView().render());
        this.router.addRoute('loans', () => new LoansView().render());

        // Handle initial route
        this.router.handleRoute();
        
        // Listen to hash changes
        window.addEventListener('hashchange', () => {
            this.router.handleRoute();
            navbar.updateActiveLink();
        });

        // Add CSS for toast container
        document.getElementById('toast-container').className = 'toast-container';
    }
}

// Global Toast utility
window.toast = {
    show: (message, type = 'info') => new Toast(message, type).show()
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
