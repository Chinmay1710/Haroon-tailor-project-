/**
 * dashboard.js - Handles data binding for the Dashboard screen.
 */

document.addEventListener("DOMContentLoaded", function() {
    // We must wait for the API to be ready before making requests.
    // However, API might not be connected immediately. We should poll or wait for QWebChannel.
    // To ensure it runs only when QWebChannel is ready, we can check for window.pyBridge
    
    function initDashboard() {
        if (!window.pyBridge) {
            setTimeout(initDashboard, 100);
            return;
        }

        loadDashboardStats();
    }
    
    initDashboard();
});

async function loadDashboardStats(date_str = null) {
    try {
        const payload = date_str ? { date: date_str } : {};
        const data = await window.API.request('get_dashboard_stats', payload);
        
        // 1. Update Top Stat Cards
        document.getElementById('stat-orders-today').innerText = data.orders_today;
        document.getElementById('stat-sales-today').innerText = window.API.formatCurrency(data.sales_today);
        document.getElementById('stat-pending-payments').innerText = window.API.formatCurrency(data.pending_payments);
        document.getElementById('stat-deliveries-today').innerText = data.deliveries_today;

        // 2. Update Order Pipeline Counts
        const counts = data.status_counts;
        document.getElementById('pipe-new').innerText = counts.NEW;
        document.getElementById('pipe-stitching').innerText = counts.CUTTING_COMPLETE || 0;
        document.getElementById('pipe-ready').innerText = counts.STITCHING_COMPLETE || 0;
        document.getElementById('pipe-delivered').innerText = counts.DELIVERED;
        document.getElementById('pipe-overdue').innerText = counts.OVERDUE;

        // 3. Populate Deliveries Today Table
        const tbody = document.getElementById('table-deliveries-today');
        if (tbody) {
            tbody.innerHTML = '';
            if (data.deliveries.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-on-surface-variant">No deliveries scheduled for today</td></tr>';
            } else {
                data.deliveries.forEach(order => {
                    const tr = document.createElement('tr');
                    tr.className = 'border-b border-surface-container last:border-0 hover:bg-surface-container-highest/20 transition-colors cursor-pointer';
                    tr.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: order.id});
                    
                    tr.innerHTML = `
                        <td class="p-4 font-medium">${order.order_number}</td>
                        <td class="p-4">${order.customer_name}</td>
                        <td class="p-4">${order.items}</td>
                        <td class="p-4">
                            <span class="px-3 py-1 rounded-full text-label-sm font-label-sm bg-primary-fixed text-on-primary-fixed">
                                ${order.status}
                            </span>
                        </td>
                        <td class="p-4">${window.API.formatCurrency(order.remaining)}</td>
                        <td class="p-4 text-right">
                            <span class="material-symbols-outlined text-on-surface-variant">chevron_right</span>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }

        // 4. Populate Recent Orders List
        const recentList = document.getElementById('recent-orders-list');
        if (recentList) {
            recentList.innerHTML = '';
            if (data.recent_orders.length === 0) {
                recentList.innerHTML = '<div class="text-center p-4 text-on-surface-variant">No recent orders</div>';
            } else {
                data.recent_orders.forEach(order => {
                    const div = document.createElement('div');
                    div.className = 'bg-surface p-4 rounded-xl border border-surface-container flex items-center justify-between cursor-pointer hover:bg-surface-container-highest/20';
                    div.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: order.id});
                    
                    // Initials logic
                    const names = order.customer_name.split(' ');
                    const initials = names.map(n => n[0]).join('').substring(0, 2).toUpperCase();

                    div.innerHTML = `
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 rounded-full bg-primary-fixed text-on-primary-fixed flex items-center justify-center font-label-lg">
                                ${initials}
                            </div>
                            <div>
                                <p class="font-label-lg text-on-surface">${order.customer_name}</p>
                                <p class="text-label-sm text-on-surface-variant">${order.order_number}</p>
                            </div>
                        </div>
                        <span class="px-3 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase bg-surface-container-high text-on-surface-variant">
                            ${order.status}
                        </span>
                    `;
                    recentList.appendChild(div);
                });
            }
        }


        
    } catch (e) {
        console.error("Failed to load dashboard stats", e);
        window.API.toast("Failed to load dashboard data", "error");
    }
}
