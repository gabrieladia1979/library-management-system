export class Modal {
    constructor({ title, body, footer, onClose }) {
        this.title = title;
        this.body = body;
        this.footer = footer || '';
        this.onClose = onClose;
        this.container = document.getElementById('modal-container');
    }

    render() {
        const modalHtml = `
            <div class="modal-backdrop fade-in" id="current-modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${this.title}</h3>
                        <button class="close-btn" id="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        ${this.body}
                    </div>
                    ${this.footer ? `
                    <div class="modal-footer">
                        ${this.footer}
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        this.container.innerHTML = modalHtml;
        
        // Attach events
        document.getElementById('modal-close').addEventListener('click', () => this.close());
        document.getElementById('current-modal').addEventListener('click', (e) => {
            if (e.target.id === 'current-modal') this.close();
        });
    }

    close() {
        const modal = document.getElementById('current-modal');
        if (modal) {
            modal.style.opacity = '0';
            setTimeout(() => {
                this.container.innerHTML = '';
                if (this.onClose) this.onClose();
            }, 300);
        }
    }
}
