const BASE_URL = '/api/v1';

class ApiService {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('token', token);
        } else {
            localStorage.removeItem('token');
        }
    }

    async request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (this.token) {
            defaultOptions.headers['Authorization'] = `Bearer ${this.token}`;
        }

        const finalOptions = { ...defaultOptions, ...options };
        
        // Merge headers if they exist in options
        if (options.headers) {
            finalOptions.headers = { ...defaultOptions.headers, ...options.headers };
        }

        if (finalOptions.body && typeof finalOptions.body === 'object' && !(finalOptions.body instanceof FormData)) {
            finalOptions.body = JSON.stringify(finalOptions.body);
        }

        try {
            const response = await fetch(url, finalOptions);
            
            if (response.status === 401) {
                this.setToken(null);
                window.location.hash = '#/login';
                throw new Error('Sesión expirada o no autorizada');
            }

            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            if (error.message !== 'Sesión expirada o no autorizada') {
                window.toast?.show(error.message, 'error');
            }
            throw error;
        }
    }

    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        // OAuth2 login expects application/x-www-form-urlencoded or multipart/form-data
        // fetch with FormData automatically sets the correct Content-Type
        const response = await fetch(`${BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error al iniciar sesión');
        }

        this.setToken(data.access_token);
        return data;
    }

    logout() {
        this.setToken(null);
        window.location.hash = '#/login';
    }

    isAuthenticated() {
        return !!this.token;
    }

    // Books
    async getBooks(search = '', genre = '', availableOnly = false) {
        let query = new URLSearchParams();
        if (search) query.append('search', search);
        if (genre) query.append('genre', genre);
        if (availableOnly) query.append('available_only', 'true');
        
        const qs = query.toString();
        return this.request(`/books/${qs ? '?' + qs : ''}`);
    }

    async getBook(id) {
        return this.request(`/books/${id}`);
    }

    async createBook(data) {
        return this.request('/books/', { method: 'POST', body: data });
    }

    async updateBook(id, data) {
        return this.request(`/books/${id}`, { method: 'PUT', body: data });
    }

    async deleteBook(id) {
        return this.request(`/books/${id}`, { method: 'DELETE' });
    }

    // Users
    async getUsers(search = '') {
        const qs = search ? `?search=${encodeURIComponent(search)}` : '';
        return this.request(`/users/${qs}`);
    }

    async createUser(data) {
        return this.request('/users/', { method: 'POST', body: data });
    }

    // Loans
    async getLoans(status = '') {
        const qs = status ? `?status=${status}` : '';
        return this.request(`/loans/${qs}`);
    }

    async borrowBook(userId, bookId) {
        return this.request('/loans/', {
            method: 'POST',
            body: { user_id: userId, book_id: bookId }
        });
    }

    async returnBook(loanId) {
        return this.request(`/loans/${loanId}/return`, { method: 'PUT' });
    }

    // Stats
    async getStats() {
        return this.request('/stats/dashboard');
    }
}

export const api = new ApiService();
