export class Router {
    constructor() {
        this.routes = {};
        this.mainContainer = document.getElementById('main-content');
    }

    addRoute(path, handler) {
        this.routes[path] = handler;
    }

    matchRoute(hash) {
        const path = hash.replace('#', '') || '';
        
        // Exact match
        if (this.routes[path]) {
            return { handler: this.routes[path], params: {} };
        }

        // Parameterized match (e.g., book/:id)
        for (const routePath in this.routes) {
            if (routePath.includes(':')) {
                const routeParts = routePath.split('/');
                const pathParts = path.split('/');

                if (routeParts.length === pathParts.length) {
                    const params = {};
                    let isMatch = true;

                    for (let i = 0; i < routeParts.length; i++) {
                        if (routeParts[i].startsWith(':')) {
                            const paramName = routeParts[i].substring(1);
                            params[paramName] = pathParts[i];
                        } else if (routeParts[i] !== pathParts[i]) {
                            isMatch = false;
                            break;
                        }
                    }

                    if (isMatch) {
                        return { handler: this.routes[routePath], params };
                    }
                }
            }
        }

        // Not found, default to dashboard
        return { handler: this.routes[''], params: {} };
    }

    async handleRoute() {
        const hash = window.location.hash;
        const path = hash.replace('#', '') || '';
        
        // Import api here to check authentication
        const { api } = await import('./services/api.js');
        
        // Navigation Guard: Redirect to login if not authenticated and trying to access private route
        if (path !== 'login' && !api.isAuthenticated()) {
            window.location.hash = '#login';
            return;
        }

        // Redirect to dashboard if authenticated and trying to access login
        if (path === 'login' && api.isAuthenticated()) {
            window.location.hash = '#';
            return;
        }

        const match = this.matchRoute(hash);
        
        // Add fade out
        this.mainContainer.style.opacity = '0';
        
        setTimeout(async () => {
            try {
                // Execute handler and get content
                await match.handler(match.params);
            } catch (error) {
                console.error('Route error:', error);
                this.mainContainer.innerHTML = `
                    <div class="glass-panel text-center">
                        <i class="ri-error-warning-line" style="font-size: 3rem; color: var(--danger)"></i>
                        <h2>Error Loading Page</h2>
                        <p class="text-secondary">${error.message}</p>
                    </div>
                `;
            }
            
            // Trigger reflow and fade in
            void this.mainContainer.offsetWidth;
            this.mainContainer.style.opacity = '1';
        }, 200); // Wait for fade out
    }
}
