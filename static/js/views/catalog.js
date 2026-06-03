import { api } from '../services/api.js';
import { Modal } from '../components/modal.js';

export class CatalogView {
    constructor() {
        this.container = document.getElementById('main-content');
        this.books = [];
    }

    async render() {
        this.container.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h2>Book Catalog</h2>
                <button class="btn btn-primary" id="add-book-btn">
                    <i class="ri-add-line"></i> Add Book
                </button>
            </div>
            
            <div class="glass-panel mb-4">
                <div class="flex gap-4 items-center">
                    <input type="text" id="search-input" class="form-control" placeholder="Search by title or author...">
                    <label class="flex items-center gap-4 text-secondary">
                        <input type="checkbox" id="available-only"> Available Only
                    </label>
                </div>
            </div>

            <div class="glass-panel table-container">
                <table id="books-table">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Author</th>
                            <th>ISBN</th>
                            <th>Genre</th>
                            <th>Availability</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="books-tbody">
                        <tr><td colspan="6" class="text-center">Loading books...</td></tr>
                    </tbody>
                </table>
            </div>
        `;

        this.attachEvents();
        await this.loadBooks();
    }

    async loadBooks(search = '', availableOnly = false) {
        try {
            this.books = await api.getBooks(search, '', availableOnly);
            this.renderTable();
        } catch (error) {
            console.error('Failed to load books', error);
        }
    }

    renderTable() {
        const tbody = document.getElementById('books-tbody');
        if (!tbody) return;

        if (this.books.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-secondary">No books found.</td></tr>';
            return;
        }

        tbody.innerHTML = this.books.map(book => `
            <tr>
                <td style="font-weight: 500;">${book.title}</td>
                <td class="text-secondary">${book.author}</td>
                <td class="text-secondary">${book.isbn}</td>
                <td><span class="badge badge-info">${book.genre || 'N/A'}</span></td>
                <td>
                    <span class="badge ${book.available_copies > 0 ? 'badge-success' : 'badge-danger'}">
                        ${book.available_copies} / ${book.quantity}
                    </span>
                </td>
                <td>
                    <button class="btn btn-secondary btn-view" data-id="${book.id}">View</button>
                    <button class="btn btn-secondary btn-edit" data-id="${book.id}">Edit</button>
                </td>
            </tr>
        `).join('');

        // Attach action events
        document.querySelectorAll('.btn-view').forEach(btn => {
            btn.addEventListener('click', (e) => {
                window.location.hash = `#book/${e.target.dataset.id}`;
            });
        });

        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const book = this.books.find(b => b.id == e.target.dataset.id);
                this.showBookForm(book);
            });
        });
    }

    attachEvents() {
        const searchInput = document.getElementById('search-input');
        const availableOnly = document.getElementById('available-only');
        const addBtn = document.getElementById('add-book-btn');

        let timeout = null;
        searchInput?.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.loadBooks(e.target.value, availableOnly.checked);
            }, 300);
        });

        availableOnly?.addEventListener('change', (e) => {
            this.loadBooks(searchInput.value, e.target.checked);
        });

        addBtn?.addEventListener('click', () => this.showBookForm());
    }

    showBookForm(book = null) {
        const isEdit = !!book;
        const modal = new Modal({
            title: isEdit ? 'Edit Book' : 'Add New Book',
            body: `
                <form id="book-form">
                    <div class="form-group">
                        <label class="form-label">Title *</label>
                        <input type="text" name="title" class="form-control" required value="${book?.title || ''}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Author *</label>
                        <input type="text" name="author" class="form-control" required value="${book?.author || ''}">
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="form-group">
                            <label class="form-label">ISBN *</label>
                            <input type="text" name="isbn" class="form-control" required value="${book?.isbn || ''}" ${isEdit ? 'disabled' : ''}>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Quantity *</label>
                            <input type="number" name="quantity" class="form-control" required min="1" value="${book?.quantity || '1'}">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="form-group">
                            <label class="form-label">Genre</label>
                            <input type="text" name="genre" class="form-control" value="${book?.genre || ''}">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Published Year</label>
                            <input type="number" name="published_year" class="form-control" value="${book?.published_year || ''}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Description</label>
                        <textarea name="description" class="form-control" rows="3">${book?.description || ''}</textarea>
                    </div>
                </form>
            `,
            footer: `
                <button class="btn btn-secondary" id="modal-close-btn">Cancel</button>
                <button class="btn btn-primary" id="save-book-btn">Save</button>
            `,
            onClose: () => {}
        });

        modal.render();

        document.getElementById('modal-close-btn').addEventListener('click', () => modal.close());
        document.getElementById('save-book-btn').addEventListener('click', async () => {
            const form = document.getElementById('book-form');
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data.quantity = parseInt(data.quantity, 10);
            if (data.published_year) data.published_year = parseInt(data.published_year, 10);
            else delete data.published_year;

            try {
                if (isEdit) {
                    await api.updateBook(book.id, data);
                    window.toast.show('Book updated successfully', 'success');
                } else {
                    await api.createBook(data);
                    window.toast.show('Book added successfully', 'success');
                }
                modal.close();
                this.loadBooks(document.getElementById('search-input')?.value || '');
            } catch (error) {
                // Handled by API
            }
        });
    }
}
