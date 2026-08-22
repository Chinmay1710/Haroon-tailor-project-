/**
 * orders.js - Data binding for Orders List
 */

let allOrders = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        loadOrders();
        
        const searchInput = document.getElementById('order-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => filterOrders());
        }
        
        const filterContainer = document.getElementById('order-filter-buttons');
        if (filterContainer) {
            const buttons = filterContainer.querySelectorAll('button[data-filter]');
            buttons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    // Update active button styling
                    buttons.forEach(b => {
                        b.classList.remove('bg-surface-container-highest', 'text-primary');
                        if (!b.classList.contains('text-error')) {
                            b.classList.add('text-on-surface-variant');
                        }
                    });
                    
                    const target = e.currentTarget;
                    if (!target.classList.contains('text-error')) {
                        target.classList.remove('text-on-surface-variant');
                        target.classList.add('bg-surface-container-highest', 'text-primary');
                    }
                    
                    window.currentOrderFilter = target.getAttribute('data-filter');
                    filterOrders();
                });
            });
        }
        
        window.currentOrderFilter = 'All Orders';
    }
    init();
});

async function loadOrders() {
    try {
        const data = await window.API.request('get_all_orders');
        allOrders = data;
        filterOrders();
        
        // Render Urgent Deadline Alerts on Orders page
        const alertsContainer = document.getElementById('urgent-alerts-container');
        const alertsList = document.getElementById('urgent-alerts-list');
        
        if (alertsContainer && alertsList) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            const urgentAlerts = allOrders.filter(o => {
                if (o.status !== 'NEW' || !o.delivery_date) return false;
                const dDate = new Date(o.delivery_date);
                dDate.setHours(0, 0, 0, 0);
                const diffTime = dDate - today;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                if (diffDays <= 3) {
                    o.days_left = diffDays;
                    return true;
                }
                return false;
            });
            
            // Sort by most urgent first
            urgentAlerts.sort((a, b) => a.days_left - b.days_left);
            
            if (urgentAlerts.length > 0) {
                alertsContainer.classList.remove('hidden');
                alertsList.innerHTML = '';
                urgentAlerts.forEach(alert => {
                    const daysText = alert.days_left < 0 ? 'OVERDUE'
                                   : alert.days_left === 0 ? '⏰ TODAY!' 
                                   : alert.days_left === 1 ? '1 day left' 
                                   : `${alert.days_left} days left`;
                    const urgencyColor = alert.days_left <= 0 ? 'bg-red-600 text-white' 
                                       : alert.days_left === 1 ? 'bg-orange-500 text-white' 
                                       : 'bg-yellow-500 text-white';
                    
                    const div = document.createElement('div');
                    div.className = 'flex items-center justify-between bg-white/80 rounded-lg px-4 py-3 border border-red-100 hover:bg-white cursor-pointer transition-colors';
                    div.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: alert.id});
                    div.innerHTML = `
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-red-500">assignment_late</span>
                            <div>
                                <p class="font-bold text-[14px] text-red-900">${alert.customer_name} — ${alert.items}</p>
                                <p class="text-[12px] text-red-600">Order ${alert.order_number} • Delivery: ${window.API.formatDate(alert.delivery_date)}</p>
                            </div>
                        </div>
                        <span class="px-3 py-1 rounded-full text-[11px] font-bold ${urgencyColor}">${daysText}</span>
                    `;
                    alertsList.appendChild(div);
                });
            } else {
                alertsContainer.classList.add('hidden');
            }
        }
        
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load orders", "error");
    }
}

window.markOrderComplete = async function(id, remainingAmount) {
    if (remainingAmount > 0) {
        const collect = confirm(`This order has a remaining balance of ${window.API.formatCurrency(remainingAmount)}. Would you like to collect the payment now before completing the order?`);
        if (collect) {
            window.API.request('navigate_to', {page: 'add_payment', order_id: id, complete_after: true});
            return;
        }
    }
    
    try {
        await window.API.request('update_order_status', {order_id: id, status: 'DELIVERED'});
        window.API.toast("Order marked as Complete", "success");
        loadOrders();
    } catch (e) {
        window.API.toast("Failed to update status: " + e, "error");
    }
};

function filterOrders() {
    const q = (document.getElementById('order-search')?.value || '').toLowerCase();
    const status = window.currentOrderFilter || 'All Orders';
    
    const countBadge = document.getElementById('overdue-count');
    if (countBadge) {
        countBadge.classList.add('hidden');
    }
    
    const filtered = allOrders.filter(o => {
        const matchesSearch = 
            (o.customer_name && o.customer_name.toLowerCase().includes(q)) || 
            (o.customer_mobile && o.customer_mobile.includes(q)) ||
            (o.order_number && o.order_number.toLowerCase().includes(q));
            
        const isOverdue = o.status === 'OVERDUE' || (o.status !== 'DELIVERED' && o.status !== 'CANCELLED' && o.delivery_date && new Date(o.delivery_date) < new Date());
        
        let matchesStatus = false;
        if (status === 'All Orders') {
            matchesStatus = true;
        } else if (status === 'Incomplete') {
            matchesStatus = (o.status !== 'DELIVERED' && o.status !== 'CANCELLED');
        } else if (status === 'Complete') {
            matchesStatus = (o.status === 'DELIVERED');
        }
        
        return matchesSearch && matchesStatus;
    });
    renderOrders(filtered);
}

function renderOrders(orders) {
    const container = document.getElementById('orders-container');
    if (!container) return;
    
    // Clear everything except headers
    const headersHTML = `
    <div class="hidden md:grid grid-cols-12 gap-4 px-4 py-2 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
        <div class="col-span-2">Order Info</div>
        <div class="col-span-3">Customer &amp; Item</div>
        <div class="col-span-2">Dates</div>
        <div class="col-span-2">Financials</div>
        <div class="col-span-2">Status</div>
        <div class="col-span-1 text-right">Action</div>
    </div>`;
    
    container.innerHTML = headersHTML;
    
    if (orders.length === 0) {
        container.innerHTML += '<div class="p-4 text-center text-on-surface-variant bg-surface-container-lowest rounded-xl border border-outline-variant/30">No orders found</div>';
        return;
    }
    
    orders.forEach(o => {
        const isOverdue = o.status === 'OVERDUE' || (o.status !== 'DELIVERED' && o.status !== 'CANCELLED' && o.delivery_date && new Date(o.delivery_date) < new Date());
        const displayStatus = isOverdue ? 'OVERDUE' : o.status;
        
        let statusColor, statusBg, statusDot;
        let cardBg = 'bg-surface-container-lowest';
        let cardBorder = 'border-outline-variant/30';
        let errorHighlight = '';
        
        if (isOverdue) {
            statusColor = 'text-on-error-container';
            statusBg = 'bg-error-container';
            statusDot = 'bg-error';
            cardBg = 'bg-error-container/20';
            cardBorder = 'border-error/20';
            errorHighlight = '<div class="absolute left-0 top-0 bottom-0 w-1 bg-error"></div>';
        } else {
            switch(o.status) {
                case 'NEW':
                    statusColor = 'text-on-surface-variant';
                    statusBg = 'bg-surface-container-low border border-outline-variant/50';
                    statusDot = 'bg-outline';
                    break;
                case 'STITCHING':
                    statusColor = 'text-primary';
                    statusBg = 'bg-surface-container-high';
                    statusDot = 'bg-primary';
                    break;
                case 'READY':
                    statusColor = 'text-on-tertiary-container';
                    statusBg = 'bg-tertiary-fixed';
                    statusDot = 'bg-tertiary-fixed-dim';
                    break;
                case 'DELIVERED':
                    statusColor = 'text-on-secondary-container';
                    statusBg = 'bg-secondary-fixed';
                    statusDot = 'bg-secondary-fixed-dim';
                    break;
                case 'CANCELLED':
                    statusColor = 'text-on-surface-variant';
                    statusBg = 'bg-surface-dim';
                    statusDot = 'bg-outline';
                    break;
                default:
                    statusColor = 'text-primary';
                    statusBg = 'bg-surface-container-high';
                    statusDot = 'bg-primary';
            }
        }
        
        const card = document.createElement('div');
        card.className = `${cardBg} rounded-xl shadow-sm border ${cardBorder} p-4 hover:shadow-md transition-shadow group grid grid-cols-1 md:grid-cols-12 gap-4 items-center relative overflow-hidden cursor-pointer`;
        card.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: o.id});
        
        card.innerHTML = `
            ${errorHighlight}
            <div class="col-span-1 md:col-span-2 flex flex-row md:flex-col justify-between md:justify-start ${isOverdue ? 'pl-2' : ''}">
                <div class="flex items-center gap-1">
                    ${isOverdue ? '<span class="material-symbols-outlined text-error text-[18px]">error</span>' : ''}
                    <span class="font-label-lg text-label-lg text-primary">${o.order_number}</span>
                </div>
            </div>
            <div class="col-span-1 md:col-span-3 flex flex-row md:flex-col justify-between md:justify-start">
                <div class="flex flex-col items-start" onclick="event.stopPropagation(); window.API.request('navigate_to', {page: 'customer_details', id: ${o.customer_id}})">
                    <span class="font-label-lg text-label-lg text-primary hover:underline cursor-pointer">${o.customer_name}</span>
                    <span class="font-body-sm text-[12px] text-on-surface-variant">${o.customer_mobile || ''}</span>
                </div>
                <span class="font-body-md text-body-md text-on-surface-variant text-sm truncate w-full pr-4 mt-1" title="${o.items || 'Custom'}">${o.items || 'Custom'}</span>
            </div>
            <div class="col-span-1 md:col-span-2 flex flex-row md:flex-col justify-between md:justify-start">
                <div class="flex flex-col">
                    <span class="font-label-sm text-label-sm text-on-surface-variant uppercase">Ordered</span>
                    <span class="font-body-md text-body-md text-on-surface">${window.API.formatDate(o.order_date)}</span>
                </div>
                <div class="flex flex-col mt-2 md:mt-1">
                    <span class="font-label-sm text-label-sm ${isOverdue ? 'text-error font-bold' : 'text-on-surface-variant'} uppercase">Delivery</span>
                    <span class="font-body-md text-body-md ${isOverdue ? 'text-error font-semibold' : 'text-on-surface'}">${window.API.formatDate(o.delivery_date)}</span>
                </div>
            </div>
            <div class="col-span-1 md:col-span-2 flex flex-row md:flex-col justify-between md:justify-start">
                <div class="flex items-baseline gap-2">
                    <span class="font-body-md text-body-md text-on-surface-variant text-sm">Total:</span>
                    <span class="font-label-lg text-label-lg text-on-surface">${window.API.formatCurrency(o.total_amount)}</span>
                </div>
            </div>
            <div class="col-span-1 md:col-span-2 flex justify-start">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm ${statusBg} ${statusColor}">
                    <span class="w-1.5 h-1.5 rounded-full ${statusDot} mr-2"></span>
                    ${displayStatus}
                </span>
            </div>
            <div class="col-span-1 md:col-span-1 flex justify-end items-center gap-1">
                ${(o.status !== 'DELIVERED' && o.status !== 'CANCELLED') ? `
                <button class="mark-complete-btn w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center hover:bg-primary hover:text-on-primary transition-colors" title="Mark as Complete">
                    <span class="material-symbols-outlined text-[18px]">check</span>
                </button>
                ` : ''}
                <button class="w-8 h-8 rounded-full flex items-center justify-center text-on-surface-variant hover:${isOverdue ? 'bg-error-container hover:text-error' : 'bg-surface-container-highest hover:text-primary'} transition-colors">
                    <span class="material-symbols-outlined text-[20px]">chevron_right</span>
                </button>
            </div>
        `;
        
        container.appendChild(card);
        
        const completeBtn = card.querySelector('.mark-complete-btn');
        if (completeBtn) {
            completeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                window.markOrderComplete(o.id, o.remaining_amount || 0);
            });
        }
    });
}
