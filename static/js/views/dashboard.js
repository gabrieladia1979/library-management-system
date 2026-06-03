import { api } from '../services/api.js';
import { StatsCard } from '../components/statsCard.js';

export class DashboardView {
    constructor() {
        this.container = document.getElementById('main-content');
    }

    async render() {
        this.container.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h2>Dashboard</h2>
            </div>
            <div id="dashboard-stats" class="grid grid-cols-3 gap-4 mb-4">
                <div class="glass-panel text-center">Loading stats...</div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div class="glass-panel">
                    <h3 class="mb-4">Quick Actions</h3>
                    <div class="flex gap-4">
                        <button class="btn btn-primary" onclick="window.location.hash='#catalog'">
                            <i class="ri-book-add-line"></i> Manage Books
                        </button>
                        <button class="btn btn-secondary" onclick="window.location.hash='#loans'">
                            <i class="ri-arrow-left-right-line"></i> Manage Loans
                        </button>
                    </div>
                </div>
                
                <div class="glass-panel">
                    <h3 class="mb-4">System Status</h3>
                    <p class="text-secondary"><i class="ri-checkbox-circle-line" style="color: var(--success)"></i> API Connected</p>
                    <p class="text-secondary"><i class="ri-checkbox-circle-line" style="color: var(--success)"></i> Database Online</p>
                    <button class="btn btn-secondary mt-4" id="check-overdue-btn">
                        <i class="ri-refresh-line"></i> Check Overdue Loans
                    </button>
                </div>
            </div>
        `;

        await this.loadStats();
        this.attachEvents();
    }

    async loadStats() {
        try {
            const stats = await api.getStats();
            const statsContainer = document.getElementById('dashboard-stats');
            
            if (statsContainer) {
                statsContainer.innerHTML = `
                    ${StatsCard('Total Books', stats.total_books, 'ri-book-2-line', 'badge-info')}
                    ${StatsCard('Total Users', stats.total_users, 'ri-user-line', 'badge-success')}
                    ${StatsCard('Active Loans', stats.active_loans, 'ri-arrow-left-right-line', 'badge-warning')}
                    ${StatsCard('Overdue Loans', stats.overdue_loans, 'ri-alert-line', 'badge-danger')}
                    ${StatsCard('Available Books', stats.available_books, 'ri-checkbox-multiple-line', 'badge-success')}
                    ${StatsCard('Total Copies', stats.total_copies, 'ri-stack-line', 'badge-info')}
                `;
            }
        } catch (error) {
            console.error('Failed to load stats', error);
        }
    }

    attachEvents() {
        const checkBtn = document.getElementById('check-overdue-btn');
        if (checkBtn) {
            checkBtn.addEventListener('click', async () => {
                try {
                    const res = await api.request('/loans/check-overdue', { method: 'POST' });
                    window.toast.show(`Updated ${res.overdue_count} overdue loans.`, 'success');
                    this.loadStats();
                } catch (error) {
                    // Handled by API service
                }
            });
        }
    }
}
