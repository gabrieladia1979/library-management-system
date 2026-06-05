import { api } from '../services/api.js';

export class LoginView {
    constructor() {
        this.container = document.getElementById('main-content');
    }

    async render() {
        // Hide navbar during login if it exists
        const navbar = document.querySelector('nav');
        if (navbar) navbar.style.display = 'none';

        this.container.innerHTML = `
            <div class="flex items-center justify-center" style="min-height: 80vh;">
                <div class="glass-panel" style="width: 100%; max-width: 400px; padding: 2rem;">
                    <div class="text-center mb-6">
                        <h1 style="color: var(--primary); margin-bottom: 0.5rem;">BiblioTech</h1>
                        <p class="text-secondary">Ingrese sus credenciales de administrador</p>
                    </div>
                    
                    <form id="login-form">
                        <div class="form-group">
                            <label for="username">Usuario</label>
                            <input type="text" id="username" class="form-control" required placeholder="admin">
                        </div>
                        
                        <div class="form-group">
                            <label for="password">Contraseña</label>
                            <input type="password" id="password" class="form-control" required placeholder="admin123">
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-full mt-4" id="login-btn">
                            <i class="ri-login-box-line"></i> Iniciar Sesión
                        </button>
                    </form>
                    
                    <div id="login-error" class="mt-4 text-center text-danger" style="display: none; font-size: 0.875rem;">
                        Credenciales incorrectas
                    </div>
                </div>
            </div>
        `;

        this.attachEvents();
    }

    attachEvents() {
        const form = document.getElementById('login-form');
        const errorDiv = document.getElementById('login-error');
        const loginBtn = document.getElementById('login-btn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> Cargando...';
            errorDiv.style.display = 'none';

            try {
                await api.login(username, password);
                
                // Show navbar again
                const navbar = document.querySelector('nav');
                if (navbar) navbar.style.display = 'flex';
                
                window.location.hash = '#dashboard';
            } catch (error) {
                console.error('Login failed', error);
                errorDiv.textContent = error.message || 'Error al iniciar sesión';
                errorDiv.style.display = 'block';
                loginBtn.disabled = false;
                loginBtn.innerHTML = '<i class="ri-login-box-line"></i> Iniciar Sesión';
            }
        });
    }
}
