export class Toast {
    constructor(message, type = 'info') {
        this.message = message;
        this.type = type; // success, error, warning, info
    }

    show() {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${this.type}`;
        
        const iconMap = {
            success: 'ri-checkbox-circle-line',
            error: 'ri-error-warning-line',
            warning: 'ri-alert-line',
            info: 'ri-information-line'
        };

        toast.innerHTML = `
            <i class="${iconMap[this.type]}"></i>
            <span>${this.message}</span>
        `;

        container.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}
