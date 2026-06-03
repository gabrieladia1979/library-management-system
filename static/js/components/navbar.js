export class Navbar {
    render() {
        return `
            <nav class="navbar">
                <div class="nav-brand">
                    <i class="ri-book-open-line"></i>
                    BiblioTech
                </div>
                <div class="nav-links">
                    <a href="#" class="nav-link" data-path="">Dashboard</a>
                    <a href="#catalog" class="nav-link" data-path="#catalog">Catalog</a>
                    <a href="#users" class="nav-link" data-path="#users">Users</a>
                    <a href="#loans" class="nav-link" data-path="#loans">Loans</a>
                </div>
            </nav>
        `;
    }

    attachEvents() {
        this.updateActiveLink();
    }

    updateActiveLink() {
        const hash = window.location.hash;
        // Match exact or base path (e.g., #book/1 -> #catalog could be active, but let's do simple)
        const activeHash = hash.startsWith('#book/') ? '#catalog' : hash;
        
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('data-path') === activeHash) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
}
