import { api } from '../services/api.js';
import { Modal } from '../components/modal.js';

export class UsersView {
    constructor() {
        this.container = document.getElementById('main-content');
        this.users = [];
    }

    async render() {
        this.container.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h2>User Management</h2>
                <button class="btn btn-primary" id="add-user-btn">
                    <i class="ri-user-add-line"></i> Add User
                </button>
            </div>
            
            <div class="glass-panel mb-4">
                <div class="flex gap-4 items-center">
                    <input type="text" id="search-input" class="form-control" placeholder="Search by name or email...">
                </div>
            </div>

            <div class="glass-panel table-container">
                <table id="users-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Status</th>
                            <th>Joined</th>
                        </tr>
                    </thead>
                    <tbody id="users-tbody">
                        <tr><td colspan="4" class="text-center">Loading users...</td></tr>
                    </tbody>
                </table>
            </div>
        `;

        this.attachEvents();
        await this.loadUsers();
    }

    async loadUsers(search = '') {
        try {
            this.users = await api.getUsers(search);
            this.renderTable();
        } catch (error) {
            console.error('Failed to load users', error);
        }
    }

    renderTable() {
        const tbody = document.getElementById('users-tbody');
        if (!tbody) return;

        if (this.users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-secondary">No users found.</td></tr>';
            return;
        }

        tbody.innerHTML = this.users.map(user => `
            <tr>
                <td style="font-weight: 500;">${user.name}</td>
                <td class="text-secondary">${user.email}</td>
                <td>
                    <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td class="text-secondary">${new Date(user.created_at).toLocaleDateString()}</td>
            </tr>
        `).join('');
    }

    attachEvents() {
        const searchInput = document.getElementById('search-input');
        const addBtn = document.getElementById('add-user-btn');

        let timeout = null;
        searchInput?.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.loadUsers(e.target.value);
            }, 300);
        });

        addBtn?.addEventListener('click', () => this.showUserForm());
    }

    showUserForm() {
        const modal = new Modal({
            title: 'Add New User',
            body: `
                <form id="user-form">
                    <div class="form-group">
                        <label class="form-label">Name *</label>
                        <input type="text" name="name" class="form-control" required minlength="1">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Email *</label>
                        <input type="email" name="email" class="form-control" required>
                    </div>
                </form>
            `,
            footer: `
                <button class="btn btn-secondary" id="modal-close-btn">Cancel</button>
                <button class="btn btn-primary" id="save-user-btn">Save</button>
            `,
            onClose: () => {}
        });

        modal.render();

        document.getElementById('modal-close-btn').addEventListener('click', () => modal.close());
        document.getElementById('save-user-btn').addEventListener('click', async () => {
            const form = document.getElementById('user-form');
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                await api.createUser(data);
                window.toast.show('User added successfully', 'success');
                modal.close();
                this.loadUsers(document.getElementById('search-input')?.value || '');
            } catch (error) {
                // Handled by API
            }
        });
    }
}
