import { api } from '../services/api.js';
import { Modal } from '../components/modal.js';

export class LoansView {
    constructor() {
        this.container = document.getElementById('main-content');
        this.loans = [];
    }

    async render() {
        this.container.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h2>Loan Management</h2>
                <button class="btn btn-primary" id="add-loan-btn">
                    <i class="ri-add-circle-line"></i> Borrow Book
                </button>
            </div>
            
            <div class="glass-panel mb-4">
                <div class="flex gap-4 items-center">
                    <select id="status-filter" class="form-control" style="max-width: 200px;">
                        <option value="">All Statuses</option>
                        <option value="active">Active</option>
                        <option value="returned">Returned</option>
                        <option value="overdue">Overdue</option>
                    </select>
                </div>
            </div>

            <div class="glass-panel table-container">
                <table id="loans-table">
                    <thead>
                        <tr>
                            <th>Book</th>
                            <th>User</th>
                            <th>Loan Date</th>
                            <th>Due Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="loans-tbody">
                        <tr><td colspan="6" class="text-center">Loading loans...</td></tr>
                    </tbody>
                </table>
            </div>
        `;

        this.attachEvents();
        await this.loadLoans();
    }

    async loadLoans(status = '') {
        try {
            this.loans = await api.getLoans(status);
            this.renderTable();
        } catch (error) {
            console.error('Failed to load loans', error);
        }
    }

    renderTable() {
        const tbody = document.getElementById('loans-tbody');
        if (!tbody) return;

        if (this.loans.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-secondary">No loans found.</td></tr>';
            return;
        }

        tbody.innerHTML = this.loans.map(loan => {
            let statusBadge = 'badge-info';
            if (loan.status === 'active') statusBadge = 'badge-success';
            if (loan.status === 'overdue') statusBadge = 'badge-danger';
            if (loan.status === 'returned') statusBadge = 'badge-secondary';

            const canReturn = loan.status !== 'returned';

            return `
            <tr>
                <td style="font-weight: 500;">${loan.book_title || `Book #${loan.book_id}`}</td>
                <td class="text-secondary">${loan.user_name || `User #${loan.user_id}`}</td>
                <td class="text-secondary">${new Date(loan.loan_date).toLocaleDateString()}</td>
                <td class="text-secondary">${new Date(loan.due_date).toLocaleDateString()}</td>
                <td><span class="badge ${statusBadge}">${loan.status.toUpperCase()}</span></td>
                <td>
                    ${canReturn ? `<button class="btn btn-secondary btn-return" data-id="${loan.id}">Return</button>` : '-'}
                </td>
            </tr>
            `;
        }).join('');

        // Attach events
        document.querySelectorAll('.btn-return').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                if (confirm('Mark this book as returned?')) {
                    try {
                        await api.returnBook(id);
                        window.toast.show('Book returned successfully', 'success');
                        this.loadLoans(document.getElementById('status-filter')?.value || '');
                    } catch (err) {}
                }
            });
        });
    }

    attachEvents() {
        const filter = document.getElementById('status-filter');
        filter?.addEventListener('change', (e) => {
            this.loadLoans(e.target.value);
        });

        document.getElementById('add-loan-btn')?.addEventListener('click', async () => {
            // Fetch users and books for dropdowns
            try {
                const [users, books] = await Promise.all([
                    api.getUsers(),
                    api.getBooks('', '', true) // Only available books
                ]);
                this.showBorrowForm(users, books);
            } catch (error) {
                window.toast.show('Failed to load data for form', 'error');
            }
        });
    }

    showBorrowForm(users, books) {
        const modal = new Modal({
            title: 'Borrow Book',
            body: `
                <form id="loan-form">
                    <div class="form-group">
                        <label class="form-label">User *</label>
                        <select name="user_id" class="form-control" required>
                            <option value="">Select a user...</option>
                            ${users.filter(u => u.is_active).map(u => `<option value="${u.id}">${u.name} (${u.email})</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Book (Available Only) *</label>
                        <select name="book_id" class="form-control" required>
                            <option value="">Select a book...</option>
                            ${books.map(b => `<option value="${b.id}">${b.title} - ${b.author}</option>`).join('')}
                        </select>
                    </div>
                </form>
            `,
            footer: `
                <button class="btn btn-secondary" id="modal-close-btn">Cancel</button>
                <button class="btn btn-primary" id="save-loan-btn">Confirm Borrow</button>
            `,
            onClose: () => {}
        });

        modal.render();

        document.getElementById('modal-close-btn').addEventListener('click', () => modal.close());
        document.getElementById('save-loan-btn').addEventListener('click', async () => {
            const form = document.getElementById('loan-form');
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const formData = new FormData(form);
            const data = {
                user_id: parseInt(formData.get('user_id'), 10),
                book_id: parseInt(formData.get('book_id'), 10)
            };

            try {
                await api.borrowBook(data.user_id, data.book_id);
                window.toast.show('Book borrowed successfully', 'success');
                modal.close();
                this.loadLoans(document.getElementById('status-filter')?.value || '');
            } catch (error) {
                // Handled by API
            }
        });
    }
}
