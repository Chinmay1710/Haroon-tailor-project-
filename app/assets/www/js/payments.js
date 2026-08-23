/**
 * payments.js - Data binding for Payments List
 */

let allPayments = [];
let currentlyRendered = [];
let currentTab = 'transactions';
let allPendingOrders = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        loadPayments();
        
        const searchInput = document.getElementById('payment-search');
        if (searchInput) {
            searchInput.addEventListener('input', applyFilters);
        }
        
        const tabTransactions = document.getElementById('tab-transactions');
        const tabPending = document.getElementById('tab-pending');
        if (tabTransactions && tabPending) {
            tabTransactions.addEventListener('click', () => switchTab('transactions'));
            tabPending.addEventListener('click', () => switchTab('pending'));
        }
        
        const filterBtn = document.getElementById('filter-btn');
        const filterDropdown = document.getElementById('filter-dropdown');
        if (filterBtn && filterDropdown) {
            filterBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                filterDropdown.classList.toggle('hidden');
            });
            document.addEventListener('click', (e) => {
                if (!filterDropdown.contains(e.target) && e.target !== filterBtn) {
                    filterDropdown.classList.add('hidden');
                }
            });
        }
        
        const filterTime = document.getElementById('filter-time');
        const filterMethod = document.getElementById('filter-method');
        if (filterTime) filterTime.addEventListener('change', applyFilters);
        if (filterMethod) filterMethod.addEventListener('change', applyFilters);
        
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) exportBtn.addEventListener('click', exportToCSV);
    }
    init();
});

async function loadPayments() {
    try {
        const data = await window.API.request('get_all_payments');
        allPayments = data;
        
        // Also fetch pending orders in the background so KPI is accurate right away
        try {
            const ordersData = await window.API.request('get_all_orders');
            allPendingOrders = ordersData.filter(o => o.remaining_amount > 0 && o.status !== 'DELIVERED');
        } catch (e) {
            console.error("Failed to load pending balances for KPIs", e);
        }
        
        applyFilters();
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load payments", "error");
    }
}

function switchTab(tab) {
    currentTab = tab;
    document.getElementById('tab-transactions').className = tab === 'transactions' 
        ? "font-headline-md text-[18px] font-semibold text-primary border-b-2 border-primary pb-1"
        : "font-headline-md text-[18px] font-semibold text-on-surface-variant hover:text-on-surface border-b-2 border-transparent pb-1 transition-colors";
    
    document.getElementById('tab-pending').className = tab === 'pending'
        ? "font-headline-md text-[18px] font-semibold text-primary border-b-2 border-primary pb-1"
        : "font-headline-md text-[18px] font-semibold text-on-surface-variant hover:text-on-surface border-b-2 border-transparent pb-1 transition-colors";
        
    const controls = document.getElementById('payment-controls');
    const headerRow = document.getElementById('list-header');
    
    if (tab === 'pending') {
        if(controls) controls.classList.add('hidden');
        if(headerRow) {
            headerRow.className = "hidden md:grid grid-cols-6 gap-4 px-4 py-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider";
            headerRow.innerHTML = `
                <div>Due Date</div>
                <div>Order No.</div>
                <div>Customer</div>
                <div>Total Amount</div>
                <div>Pending</div>
                <div class="text-right">Action</div>
            `;
        }
        if (allPendingOrders.length === 0) {
            loadPendingBalances();
        } else {
            applyFilters();
        }
    } else {
        if(controls) controls.classList.remove('hidden');
        if(headerRow) {
            headerRow.className = "hidden md:grid grid-cols-6 gap-4 px-4 py-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider";
            headerRow.innerHTML = `
                <div>Date</div>
                <div>Order No.</div>
                <div>Customer</div>
                <div>Amount</div>
                <div>Method</div>
                <div class="text-right">Balance</div>
            `;
        }
        applyFilters();
    }
}

async function loadPendingBalances() {
    try {
        const data = await window.API.request('get_all_orders');
        allPendingOrders = data.filter(o => o.remaining_amount > 0 && o.status !== 'DELIVERED');
        applyFilters();
    } catch (e) {
        window.API.toast("Failed to load pending balances", "error");
    }
}

function renderPendingBalances(orders) {
    const container = document.getElementById('table-payments');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (orders.length === 0) {
        container.innerHTML = '<div class="p-4 text-center text-on-surface-variant w-full">No pending balances found</div>';
        return;
    }
    
    orders.forEach(o => {
        const div = document.createElement('div');
        div.className = 'grid grid-cols-1 md:grid-cols-6 gap-4 items-center bg-white p-4 rounded-lg border border-surface-container-highest hover:shadow-md transition-shadow cursor-pointer';
        div.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: o.id});
        
        div.innerHTML = `
            <div class="font-body-md text-body-md text-on-surface">${window.API.formatDate(o.delivery_date)}</div>
            <div class="font-label-lg text-label-lg text-primary">${o.order_number}</div>
            <div class="font-body-md text-body-md text-on-surface">${o.customer_name || 'Customer'}</div>
            <div class="font-label-lg text-label-lg text-on-surface">${window.API.formatCurrency(o.total_amount)}</div>
            <div class="font-label-lg text-label-lg text-error font-bold">${window.API.formatCurrency(o.remaining_amount)}</div>
            <div class="text-right font-body-md text-body-md flex items-center justify-end gap-3">
                <button onclick="event.stopPropagation(); window.API.request('navigate_to', {page: 'add_payment', order_id: ${o.id}});" class="px-3 py-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium border border-primary">Collect</button>
            </div>
        `;
        container.appendChild(div);
    });
}

function filterPayments(query) {
    applyFilters();
}

function applyFilters() {
    const q = (document.getElementById('payment-search')?.value || '').toLowerCase();
    
    if (currentTab === 'pending') {
        const filtered = allPendingOrders.filter(o => 
            (o.customer_name && o.customer_name.toLowerCase().includes(q)) || 
            (o.customer_mobile && String(o.customer_mobile).toLowerCase().includes(q)) ||
            (o.order_number && String(o.order_number).toLowerCase().includes(q)) ||
            (o.id && String(o.id).toLowerCase().includes(q))
        );
        renderPendingBalances(filtered);
        return;
    }
    
    const timeFilter = document.getElementById('filter-time')?.value || 'today';
    const methodFilter = document.getElementById('filter-method')?.value || 'all';
    
    const now = new Date();
    
    const filtered = allPayments.filter(p => {
        const matchesSearch = (p.customer_name && p.customer_name.toLowerCase().includes(q)) || 
                              (p.customer_mobile && String(p.customer_mobile).toLowerCase().includes(q)) ||
                              (p.order_number && String(p.order_number).toLowerCase().includes(q)) ||
                              (p.order_id && String(p.order_id).toLowerCase().includes(q));
        if (!matchesSearch) return false;
        
        if (methodFilter !== 'all') {
            if (!p.payment_method || p.payment_method.toUpperCase() !== methodFilter) return false;
        }
        
        if (timeFilter !== 'all' && p.payment_date) {
            const pDate = new Date(p.payment_date);
            const diffTime = Math.abs(now - pDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (timeFilter === 'today') {
                if (pDate.toDateString() !== now.toDateString()) return false;
            } else if (timeFilter === '7days') {
                if (diffDays > 7) return false;
            } else if (timeFilter === '30days') {
                if (diffDays > 30) return false;
            }
        }
        return true;
    });
    
    currentlyRendered = filtered;
    
    // Calculate pending payments using allPendingOrders if loaded, otherwise we wait for it
    let totalPendingPayments = 0;
    if (allPendingOrders.length > 0) {
        allPendingOrders.forEach(o => {
            totalPendingPayments += o.remaining_amount || 0;
        });
    }
    
    // Update KPIs based on the filtered data
    let totalCollected = 0;
    let todayCollected = 0;
    
    const uniqueOrderIds = new Set();
    const nowStr = now.toDateString();
    let todayCount = 0;
    
    allPayments.forEach(p => {
        totalCollected += p.amount || 0;
        
        if (p.payment_date) {
            const pDate = new Date(p.payment_date);
            if (pDate.toDateString() === nowStr) {
                todayCollected += p.amount || 0;
                todayCount++;
            }
        }
    });
    
    const tc = document.getElementById('dash-total-collected');
    if (tc) tc.textContent = window.API.formatCurrency(totalCollected);
    
    const pp = document.getElementById('dash-pending-payments');
    if (pp) pp.textContent = window.API.formatCurrency(totalPendingPayments);
    
    const tp = document.getElementById('dash-today-payments');
    if (tp) tp.textContent = window.API.formatCurrency(todayCollected);
    
    const tcCount = document.getElementById('dash-today-transactions-count');
    if (tcCount) tcCount.textContent = `${todayCount} transactions today`;
    
    renderPayments(filtered);
}

function exportToCSV() {
    if (currentlyRendered.length === 0) {
        window.API.toast("No transactions to export", "info");
        return;
    }
    
    let csv = "Date,Order No.,Customer,Amount,Method,Remaining Balance\n";
    currentlyRendered.forEach(p => {
        const dateStr = window.API.formatDate(p.payment_date);
        const orderNo = p.order_number || '#ORD';
        const customer = p.customer_name ? `"${p.customer_name}"` : 'Customer';
        const amount = p.amount || 0;
        const method = p.payment_method || 'CASH';
        const remaining = p.remaining_amount || 0;
        
        csv += `${dateStr},${orderNo},${customer},${amount},${method},${remaining}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'recent_transactions.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function renderPayments(payments) {
    const container = document.getElementById('table-payments');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (payments.length === 0) {
        container.innerHTML = '<div class="p-4 text-center text-on-surface-variant w-full">No payments found</div>';
        return;
    }
    
    payments.forEach(p => {
        const div = document.createElement('div');
        div.className = 'grid grid-cols-1 md:grid-cols-6 gap-4 items-center bg-white p-4 rounded-lg border border-surface-container-highest hover:shadow-md transition-shadow cursor-pointer';
        div.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: p.order_id});
        
        const methodIcons = {
            'CASH': 'payments',
            'UPI': 'qr_code_scanner',
            'CARD': 'credit_card',
            'BANK': 'account_balance'
        };
        const methodIcon = methodIcons[p.payment_method?.toUpperCase()] || 'payments';
        
        const remaining = p.remaining_amount !== undefined ? p.remaining_amount : 0;
        const remainingClass = remaining > 0 ? "text-error" : "text-on-surface-variant";
        
        div.innerHTML = `
            <div class="font-body-md text-body-md text-on-surface">${window.API.formatDate(p.payment_date)}</div>
            <div class="font-label-lg text-label-lg text-primary">${p.order_number || '#ORD'}</div>
            <div class="font-body-md text-body-md text-on-surface">${p.customer_name || 'Customer'}</div>
            <div class="font-label-lg text-label-lg text-on-surface">${window.API.formatCurrency(p.amount)}</div>
            <div>
                <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-surface-container-highest text-primary font-label-sm text-[12px]">
                    <span class="material-symbols-outlined text-[14px]">${methodIcon}</span> ${p.payment_method || 'CASH'}
                </span>
            </div>
            <div class="text-right font-body-md text-body-md ${remainingClass} flex items-center justify-end gap-2">
                ${window.API.formatCurrency(remaining)}
                <button onclick="event.stopPropagation(); window.API.request('print_receipt', {payment_id: ${p.id}, order_id: ${p.order_id}});" class="w-8 h-8 rounded-full hover:bg-surface-container-low text-primary flex items-center justify-center transition-colors">
                    <span class="material-symbols-outlined text-[18px]">print</span>
                </button>
            </div>
        `;
        container.appendChild(div);
    });
}
