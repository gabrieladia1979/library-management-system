const BASE_URL = '/api/v1';

class ApiService {
    async request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const finalOptions = { ...defaultOptions, ...options };

        if (finalOptions.body && typeof finalOptions.body === 'object') {
            finalOptions.body = JSON.stringify(finalOptions.body);
        }

        try {
            const response = await fetch(url, finalOptions);
            
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
            window.toast?.show(error.message, 'error');
            throw error;
        }
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
