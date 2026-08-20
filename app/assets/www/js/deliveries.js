/**
 * deliveries.js - Data binding for Deliveries page
 */

let allDeliveries = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        loadDeliveries();
    }
    init();
});

async function loadDeliveries() {
    try {
        const data = await window.API.request('get_deliveries_dashboard');
        
        document.getElementById('del-due-today').innerText = data.counts.due_today;
        document.getElementById('del-due-tmr').innerText = data.counts.due_tomorrow;
        document.getElementById('del-upcoming').innerText = data.counts.upcoming;
        document.getElementById('del-overdue').innerText = data.counts.overdue;
        
        allDeliveries = data.deliveries;
        renderDeliveries(allDeliveries);
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load deliveries", "error");
    }
}

function renderDeliveries(deliveries) {
    const tbody = document.getElementById('table-deliveries');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (deliveries.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="p-4 text-center text-on-surface-variant">No deliveries found</td></tr>';
        return;
    }
    
    deliveries.forEach(d => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-surface-container last:border-0 hover:bg-surface-container-highest/20 transition-colors cursor-pointer';
        tr.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: d.id});
        
        const isOverdue = new Date(d.delivery_date) < new Date(new Date().toDateString());
        const dateColor = isOverdue ? 'text-error' : 'text-on-surface';
        const dateIcon = isOverdue ? 'warning' : 'calendar_today';
        
        const colors = {
            'NEW': 'bg-primary-fixed text-on-primary-fixed',
            'STITCHING': 'bg-tertiary-fixed text-on-tertiary-fixed',
            'READY': 'bg-surface-container-high text-on-surface-variant',
            'DELIVERED': 'bg-surface-container text-on-surface',
            'OVERDUE': 'bg-error-container text-on-error-container',
            'CANCELLED': 'bg-surface-dim text-on-surface-variant'
        };
        const statusClass = colors[d.status] || colors['NEW'];
        
        tr.innerHTML = `
            <td class="p-4 font-medium text-primary">${d.order_number}</td>
            <td class="p-4">
                <p class="font-label-lg text-on-surface">${d.customer_name}</p>
                <p class="font-label-sm text-on-surface-variant">${d.mobile || ''}</p>
            </td>
            <td class="p-4 text-on-surface-variant">${d.items || 'Custom'}</td>
            <td class="p-4">
                <div class="flex items-center gap-2 ${dateColor}">
                    <span class="material-symbols-outlined text-[18px]">${dateIcon}</span>
                    <span class="font-medium">${window.API.formatDate(d.delivery_date)}</span>
                </div>
            </td>
            <td class="p-4">
                <span class="px-3 py-1 rounded-full text-label-sm font-label-sm uppercase tracking-wider ${statusClass}">
                    ${d.status}
                </span>
            </td>
            <td class="p-4">
                <div class="flex items-center justify-end gap-2">
                    <button onclick="event.stopPropagation(); updateStatus(${d.id}, 'READY');" class="bg-surface-container-high hover:bg-primary-fixed text-on-surface-variant hover:text-on-primary-fixed w-10 h-10 rounded-full flex items-center justify-center transition-colors" title="Mark Ready">
                        <span class="material-symbols-outlined text-[20px]">check_room</span>
                    </button>
                    <button onclick="event.stopPropagation(); updateStatus(${d.id}, 'DELIVERED');" class="bg-primary text-on-primary hover:bg-primary/90 w-10 h-10 rounded-full flex items-center justify-center transition-colors shadow-sm" title="Mark Delivered">
                        <span class="material-symbols-outlined text-[20px]">local_shipping</span>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

window.updateStatus = async function(orderId, newStatus) {
    try {
        await window.API.request('update_order_status', {id: orderId, status: newStatus});
        window.API.toast(`Order marked as ${newStatus}`, "success");
        loadDeliveries();
    } catch (e) {
        window.API.toast(e.toString(), "error");
    }
}
