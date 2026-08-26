/**
 * orders.js - Data binding for Orders List
 */

let allOrders = [];
let currentPage = 1;
const itemsPerPage = 10;


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
                        b.className = "px-5 py-2.5 rounded-full bg-surface-container border border-outline-variant/50 text-on-surface-variant font-label-lg hover:bg-surface-container-high whitespace-nowrap transition-all";
                    });
                    
                    const target = e.currentTarget;
                    target.className = "px-5 py-2.5 rounded-full bg-primary text-on-primary font-label-lg shadow-sm whitespace-nowrap transition-all";
                    
                    window.currentOrderFilter = target.getAttribute('data-filter');
                    filterOrders();
                });
            });
        }
        
        window.currentOrderFilter = 'All Orders';
        
        const btnPrev = document.getElementById('btn-prev-page');
        const btnNext = document.getElementById('btn-next-page');
        if (btnPrev && btnNext) {
            btnPrev.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    filterOrders(false);
                }
            });
            btnNext.addEventListener('click', () => {
                currentPage++;
                filterOrders(false);
            });
        }
    }
    init();
});

async function loadOrders() {
    try {
        const data = await window.API.request('get_all_orders');
        allOrders = data;
        filterOrders();
        

    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load orders", "error");
    }
}

window.markOrderComplete = async function(id) {
    const confirmResult = await window.API.confirmWithCheckbox(
        'Mark Stitching Complete?',
        'Are you sure you want to mark this order as Stitching Complete? This means the item is ready for delivery.',
        'Send WhatsApp Notification'
    );
    
    if (confirmResult.confirmed) {
        try {
            const res = await window.API.request('update_order_status', {order_id: id, status: 'STITCHING_COMPLETE', send_whatsapp: confirmResult.checked});
            window.API.toast("Order marked as Stitching Complete", "success");
            // Open WhatsApp with pre-typed message
            if (res && res.whatsapp_url) {
                window.API.request('open_whatsapp_url', {url: res.whatsapp_url});
            }
            loadOrders();
        } catch (e) {
            window.API.toast("Failed to update status: " + e, "error");
        }
    }
};

function filterOrders(resetPage = true) {
    if (resetPage) currentPage = 1;
    const q = (document.getElementById('order-search')?.value || '').toLowerCase();
    const status = window.currentOrderFilter || 'All Orders';
    
    const countBadge = document.getElementById('overdue-count');
    if (countBadge) {
        countBadge.classList.add('hidden');
    }
    
    const filtered = allOrders.filter(o => {
        const matchesSearch = 
            (o.customer_name && o.customer_name.toLowerCase().includes(q)) || 
            (o.customer_mobile && String(o.customer_mobile).toLowerCase().includes(q)) ||
            (o.order_number && String(o.order_number).toLowerCase().includes(q)) ||
            (o.id && String(o.id).toLowerCase().includes(q));
            
        const isOverdue = o.status === 'OVERDUE' || (o.status !== 'DELIVERED' && o.status !== 'CANCELLED' && o.delivery_date && new Date(o.delivery_date) < new Date());
        
        let matchesStatus = false;
        if (status === 'All Orders') {
            matchesStatus = true;
        } else if (status === 'Incomplete') {
            matchesStatus = (o.status !== 'DELIVERED' && o.status !== 'CANCELLED' && o.status !== 'STITCHING_COMPLETE');
        } else if (status === 'Cutting Complete') {
            matchesStatus = (o.status === 'CUTTING_COMPLETE');
        } else if (status === 'Stitching & Press Complete') {
            matchesStatus = (o.status === 'STITCHING_COMPLETE');
        } else if (status === 'Complete') {
            matchesStatus = (o.status === 'DELIVERED');
        }
        
        return matchesSearch && matchesStatus;
    });

    filtered.sort((a, b) => {
        if (status === 'All Orders' || status === 'Complete') {
            // Stack system: newest updated/created orders first
            const timeA = a.updated_at ? new Date(a.updated_at).getTime() : (a.id || 0);
            const timeB = b.updated_at ? new Date(b.updated_at).getTime() : (b.id || 0);
            return timeB - timeA;
        } else {
            // Incomplete orders: sort red alert (overdue and urgent) orders to top, then by closest delivery date
            const checkAlert = (o) => {
                if (o.status === 'OVERDUE' || (o.status !== 'DELIVERED' && o.status !== 'CANCELLED' && o.delivery_date && new Date(o.delivery_date) < new Date())) return true;
                if (o.status === 'NEW' && o.delivery_date) {
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const dDate = new Date(o.delivery_date);
                    dDate.setHours(0, 0, 0, 0);
                    const diffDays = Math.ceil((dDate - today) / (1000 * 60 * 60 * 24));
                    if (diffDays >= 0 && diffDays <= 3) return true;
                }
                return false;
            };
            
            const isAAlert = checkAlert(a);
            const isBAlert = checkAlert(b);
            
            if (isAAlert && !isBAlert) return -1;
            if (!isAAlert && isBAlert) return 1;

            const dateA = a.delivery_date ? new Date(a.delivery_date).getTime() : Infinity;
            const dateB = b.delivery_date ? new Date(b.delivery_date).getTime() : Infinity;
            return dateA - dateB;
        }
    });

    const totalItems = filtered.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
    if (currentPage > totalPages) currentPage = totalPages;
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, totalItems);
    
    const pInfo = document.getElementById('pagination-info');
    if (pInfo) {
        if (totalItems === 0) {
            pInfo.innerText = "Showing 0 orders";
        } else {
            pInfo.innerText = `Showing ${startIndex + 1} to ${endIndex} of ${totalItems} orders`;
        }
    }
    
    const btnPrev = document.getElementById('btn-prev-page');
    const btnNext = document.getElementById('btn-next-page');
    if (btnPrev) btnPrev.disabled = currentPage === 1;
    if (btnNext) btnNext.disabled = currentPage === totalPages;

    const pagedData = filtered.slice(startIndex, endIndex);
    renderOrders(pagedData);
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
        <div class="col-span-1">Financials</div>
        <div class="col-span-2">Status</div>
        <div class="col-span-2 text-right">Action</div>
    </div>`;
    
    container.innerHTML = headersHTML;
    
    if (orders.length === 0) {
        container.innerHTML += '<div class="p-4 text-center text-on-surface-variant bg-surface-container-lowest rounded-xl border border-outline-variant/30">No orders found</div>';
        return;
    }
    
    orders.forEach(o => {
        const isOverdue = o.status === 'OVERDUE' || (o.status !== 'DELIVERED' && o.status !== 'CANCELLED' && o.delivery_date && new Date(o.delivery_date) < new Date());
        
        let isUrgent = false;
        let daysLeft = null;
        let daysText = '';
        if (o.status === 'NEW' && o.delivery_date) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const dDate = new Date(o.delivery_date);
            dDate.setHours(0, 0, 0, 0);
            const diffTime = dDate - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            if (diffDays >= 0 && diffDays <= 3) {
                isUrgent = true;
                daysLeft = diffDays;
                daysText = daysLeft === 0 ? '⏰ TODAY!' : (daysLeft === 1 ? '1 day left' : `${daysLeft} days left`);
            }
        }

        let displayStatus = o.status.replace(/_/g, ' ').replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
        if (isOverdue) displayStatus = 'Overdue';
        
        let statusColor, statusBg, statusDot;
        let cardBg = 'bg-surface-container-lowest';
        let cardBorder = 'border-outline-variant/30';
        let errorHighlight = '';
        let urgentBadge = '';
        
        if (isOverdue) {
            statusColor = 'text-on-error-container';
            statusBg = 'bg-error-container';
            statusDot = 'bg-error';
            cardBg = 'bg-error-container/20';
            cardBorder = 'border-error/20';
            errorHighlight = '<div class="absolute left-0 top-0 bottom-0 w-1 bg-error"></div>';
        } else if (isUrgent) {
            const urgencyColor = daysLeft === 0 ? 'bg-red-600 text-white' 
                               : daysLeft === 1 ? 'bg-orange-500 text-white' 
                               : 'bg-yellow-500 text-white';
            urgentBadge = `<span class="inline-flex items-center px-2 py-0.5 ml-2 rounded-md font-label-sm text-[10px] uppercase font-bold ${urgencyColor}">${daysText}</span>`;
            cardBorder = 'border-red-400/50';
            cardBg = 'bg-red-50/50';
            errorHighlight = '<div class="absolute left-0 top-0 bottom-0 w-1 bg-red-400"></div>';
            statusColor = 'text-on-surface-variant';
            statusBg = 'bg-surface-container-low border border-outline-variant/50';
            statusDot = 'bg-outline';
        } else {
            switch(o.status) {
                case 'NEW':
                    statusColor = 'text-on-surface-variant';
                    statusBg = 'bg-surface-container-low border border-outline-variant/50';
                    statusDot = 'bg-outline';
                    break;
                case 'CUTTING_COMPLETE':
                    statusColor = 'text-primary';
                    statusBg = 'bg-surface-container-high';
                    statusDot = 'bg-primary';
                    break;
                case 'STITCHING_COMPLETE':
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
                    <span class="font-label-sm text-label-sm ${isOverdue || isUrgent ? 'text-error font-bold' : 'text-on-surface-variant'} uppercase">Delivery</span>
                    <div class="flex items-center">
                        <span class="font-body-md text-body-md ${isOverdue || isUrgent ? 'text-error font-semibold' : 'text-on-surface'}">${window.API.formatDate(o.delivery_date)}</span>
                        ${urgentBadge}
                    </div>
                </div>
            </div>
            <div class="col-span-1 md:col-span-1 flex flex-row md:flex-col justify-between md:justify-start items-start md:items-center">
                <div class="flex flex-col items-end">
                    <span class="font-body-md text-body-md text-on-surface-variant text-sm">Total:</span>
                    <span class="font-label-lg text-label-lg text-on-surface">${window.API.formatCurrency(o.total_amount)}</span>
                </div>
            </div>
            <div class="col-span-1 md:col-span-2 flex justify-start">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-[11px] ${statusBg} ${statusColor}">
                    <span class="w-1.5 h-1.5 rounded-full ${statusDot} mr-1.5"></span>
                    ${displayStatus}
                </span>
            </div>
            <div class="col-span-1 md:col-span-2 flex justify-end items-center gap-2">
                ${(o.status !== 'STITCHING_COMPLETE' && o.status !== 'DELIVERED' && o.status !== 'CANCELLED') ? `
                <button class="mark-complete-btn px-3 py-1.5 rounded-md bg-primary/10 text-primary font-label-sm hover:bg-primary hover:text-on-primary transition-all whitespace-nowrap shadow-sm border border-primary/20 flex items-center gap-1" title="Mark Stitching Complete">
                    <span class="material-symbols-outlined text-[16px]">check_circle</span>
                    Complete
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
