import { api } from '../services/api.js';

export class Navbar {
    render() {
        // If not authenticated, the navbar should probably be hidden, 
        // but it's handled by LoginView too.
        const authStyle = api.isAuthenticated() ? 'display: flex' : 'display: none';

        return `
            <nav class="navbar" style="${authStyle}">
                <div class="nav-brand">
                    <i class="ri-book-open-line"></i>
                    BiblioTech
                </div>
                <div class="nav-links">
                    <a href="#" class="nav-link" data-path="">Dashboard</a>
                    <a href="#catalog" class="nav-link" data-path="#catalog">Catalog</a>
                    <a href="#users" class="nav-link" data-path="#users">Users</a>
                    <a href="#loans" class="nav-link" data-path="#loans">Loans</a>
                    <button id="logout-btn" class="nav-link" style="background: none; border: none; cursor: pointer; color: var(--danger)">
                        <i class="ri-logout-box-r-line"></i> Salir
                    </button>
                </div>
            </nav>
        `;
    }

    attachEvents() {
        this.updateActiveLink();
        
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                api.logout();
                // Navbar will be hidden by next render or manual intervention
                const navbar = document.querySelector('nav');
                if (navbar) navbar.style.display = 'none';
            });
        }
    }

    updateActiveLink() {
        const hash = window.location.hash;
        // Match exact or base path (e.g., #book/1 -> #catalog could be active, but let's do simple)
        const activeHash = hash.startsWith('#book/') ? '#catalog' : hash;
        
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('data-path') === activeHash) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
}
