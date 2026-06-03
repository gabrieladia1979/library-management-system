export const StatsCard = (title, value, icon, colorClass) => `
    <div class="glass-panel flex items-center gap-4">
        <div class="stats-icon ${colorClass}" style="
            width: 48px; height: 48px; border-radius: 12px; 
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem; background: rgba(255,255,255,0.05);">
            <i class="${icon}"></i>
        </div>
        <div>
            <div class="text-secondary text-sm">${title}</div>
            <div style="font-size: 1.5rem; font-weight: 600; font-family: var(--font-heading);">${value}</div>
        </div>
    </div>
`;
