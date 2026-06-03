import { api } from '../services/api.js';

export class BookDetailView {
    constructor(id) {
        this.container = document.getElementById('main-content');
        this.bookId = id;
        this.book = null;
    }

    async render() {
        this.container.innerHTML = `
            <div class="mb-4">
                <button class="btn btn-secondary" onclick="window.history.back()">
                    <i class="ri-arrow-left-line"></i> Back
                </button>
            </div>
            <div id="book-detail-content" class="glass-panel">
                <div class="text-center"><i class="ri-loader-4-line ri-spin"></i> Loading...</div>
            </div>
        `;

        await this.loadBook();
    }

    async loadBook() {
        try {
            this.book = await api.getBook(this.bookId);
            this.renderDetail();
        } catch (error) {
            document.getElementById('book-detail-content').innerHTML = `
                <div class="text-center text-secondary py-4">Book not found or error loading.</div>
            `;
        }
    }

    renderDetail() {
        const content = document.getElementById('book-detail-content');
        if (!content || !this.book) return;

        const b = this.book;
        const availableClass = b.available_copies > 0 ? 'badge-success' : 'badge-danger';

        content.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <div>
                    <h2 style="font-size: 2rem; margin-bottom: 0.5rem;">${b.title}</h2>
                    <p class="text-secondary" style="font-size: 1.1rem;">By ${b.author}</p>
                </div>
                <div class="text-right">
                    <div class="badge ${availableClass} mb-4" style="font-size: 1rem; padding: 0.5rem 1rem;">
                        ${b.available_copies} / ${b.quantity} Available
                    </div>
                </div>
            </div>

            <hr style="border-color: var(--glass-border); margin: 1.5rem 0;">

            <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <h4 class="text-secondary mb-4">Details</h4>
                    <p><strong>ISBN:</strong> ${b.isbn}</p>
                    <p><strong>Genre:</strong> ${b.genre || 'N/A'}</p>
                    <p><strong>Published:</strong> ${b.published_year || 'N/A'}</p>
                    <p><strong>Added On:</strong> ${new Date(b.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                    <h4 class="text-secondary mb-4">Description</h4>
                    <p>${b.description || 'No description available.'}</p>
                </div>
            </div>
            
            <hr style="border-color: var(--glass-border); margin: 1.5rem 0;">
            
            <div class="flex gap-4 justify-end">
                <button class="btn btn-danger" id="delete-btn">
                    <i class="ri-delete-bin-line"></i> Delete Book
                </button>
            </div>
        `;

        document.getElementById('delete-btn').addEventListener('click', async () => {
            if (confirm(`Are you sure you want to delete "${b.title}"?`)) {
                try {
                    await api.deleteBook(b.id);
                    window.toast.show('Book deleted successfully', 'success');
                    window.location.hash = '#catalog';
                } catch (error) {
                    // Handled by api service
                }
            }
        });
    }
}
