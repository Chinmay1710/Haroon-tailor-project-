/**
 * payments.js - Data binding for Payments List
 * Handles: Customer Transactions, Pending Balances, Worker Payments, Stock
 */

let allPayments = [];
let currentlyRendered = [];
let currentTab = 'transactions';
let allPendingOrders = [];
let workerPaymentData = null;
let stockPaymentData = null;
let kpisVisible = false;

window.toggleKPIs = function() {
    kpisVisible = !kpisVisible;
    updateKpiDisplay();
}

function updateKpiDisplay() {
    ['dash-total-collected', 'dash-pending-payments', 'dash-today-payments', 'dash-worker-dues', 'dash-stock-value'].forEach(id => {
        const el = document.getElementById(id);
        if (el && el.dataset.amount !== undefined) {
            el.textContent = kpisVisible ? window.API.formatCurrency(parseFloat(el.dataset.amount)) : '****';
        }
    });
    const btn = document.getElementById('kpi-toggle-btn');
    if (btn) {
        btn.innerHTML = kpisVisible 
            ? `<span class="material-symbols-outlined text-[18px]">visibility_off</span> Hide Amounts`
            : `<span class="material-symbols-outlined text-[18px]">visibility</span> Show Amounts`;
    }
}

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
        
        // Tab click handlers
        const tabTransactions = document.getElementById('tab-transactions');
        const tabPending = document.getElementById('tab-pending');
        const tabWorkers = document.getElementById('tab-workers');
        const tabStock = document.getElementById('tab-stock');
        
        if (tabTransactions) tabTransactions.addEventListener('click', () => switchTab('transactions'));
        if (tabPending) tabPending.addEventListener('click', () => switchTab('pending'));
        if (tabWorkers) tabWorkers.addEventListener('click', () => switchTab('workers'));
        if (tabStock) tabStock.addEventListener('click', () => switchTab('stock'));
        
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
        
        // Pre-fetch worker payment data for KPI
        try {
            const wpData = await window.API.request('get_worker_payment_summary');
            workerPaymentData = wpData;
        } catch (e) {
            console.error("Failed to load worker payment summary", e);
        }
        
        // Pre-fetch stock payment data for KPI
        try {
            const spData = await window.API.request('get_stock_payment_summary');
            stockPaymentData = spData;
        } catch (e) {
            console.error("Failed to load stock payment summary", e);
        }
        
        applyFilters();
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load payments", "error");
    }
}

function setTabActive(tabName) {
    const tabs = ['transactions', 'pending', 'workers', 'stock'];
    const activeClass = "font-headline-md text-[18px] font-semibold text-primary border-b-2 border-primary pb-1";
    const inactiveClass = "font-headline-md text-[18px] font-semibold text-on-surface-variant hover:text-on-surface border-b-2 border-transparent pb-1 transition-colors";
    
    tabs.forEach(t => {
        const el = document.getElementById(`tab-${t}`);
        if (el) el.className = t === tabName ? activeClass : inactiveClass;
    });
}

function switchTab(tab) {
    currentTab = tab;
    setTabActive(tab);
    
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
    } else if (tab === 'workers') {
        if(controls) controls.classList.add('hidden');
        if(headerRow) {
            headerRow.className = "hidden md:grid grid-cols-5 gap-4 px-4 py-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider";
            headerRow.innerHTML = `
                <div>Worker</div>
                <div>Total Earned</div>
                <div>Advances Given</div>
                <div>Remaining Due</div>
                <div class="text-right">Action</div>
            `;
        }
        loadWorkerPayments();
    } else if (tab === 'stock') {
        if(controls) controls.classList.add('hidden');
        if(headerRow) {
            headerRow.className = "hidden md:grid grid-cols-6 gap-4 px-4 py-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider";
            headerRow.innerHTML = `
                <div>Item Name</div>
                <div>Category</div>
                <div>In Stock</div>
                <div>Unit Cost</div>
                <div>Total Value</div>
                <div class="text-right">Status</div>
            `;
        }
        loadStockPayments();
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

// ─── Worker Payments ───────────────────────────────────────────────

async function loadWorkerPayments() {
    const container = document.getElementById('table-payments');
    if (!container) return;
    
    container.innerHTML = '<div class="p-4 text-center text-on-surface-variant">Loading worker payments...</div>';
    
    try {
        const data = await window.API.request('get_worker_payment_summary');
        workerPaymentData = data;
        renderWorkerPayments(data.workers || []);
        
        // Update worker KPI
        if (data.summary) {
            const wd = document.getElementById('dash-worker-dues');
            if (wd) wd.dataset.amount = data.summary.total_dues || 0;
            const wc = document.getElementById('dash-worker-count');
            if (wc) wc.innerText = `${data.summary.worker_count || 0} active workers`;
            updateKpiDisplay();
        }
    } catch (e) {
        console.error(e);
        container.innerHTML = '<div class="p-4 text-center text-error">Failed to load worker payments</div>';
    }
}

function renderWorkerPayments(workers) {
    const container = document.getElementById('table-payments');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (workers.length === 0) {
        container.innerHTML = '<div class="p-4 text-center text-on-surface-variant w-full">No workers found</div>';
        return;
    }
    
    workers.forEach(w => {
        const div = document.createElement('div');
        div.className = 'grid grid-cols-1 md:grid-cols-5 gap-4 items-center bg-white p-4 rounded-lg border border-surface-container-highest hover:shadow-md transition-shadow cursor-pointer';
        div.onclick = () => window.API.request('navigate_to', {page: 'workers'});
        
        const dueClass = w.remaining_due > 0 ? 'text-[#f59e0b] font-bold' : 'text-on-surface-variant';
        const typeLabel = w.worker_type === 'DAILY_SALARY' ? 'Daily' : 'Piece Rate';
        
        div.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-[#f59e0b]/10 flex items-center justify-center text-[#f59e0b] font-label-lg">
                    ${w.name.charAt(0).toUpperCase()}
                </div>
                <div>
                    <p class="font-label-lg text-label-lg text-on-surface">${w.name}</p>
                    <p class="font-label-sm text-label-sm text-on-surface-variant">${typeLabel}${w.phone ? ' • ' + w.phone : ''}</p>
                </div>
            </div>
            <div class="font-label-lg text-label-lg text-on-surface">${window.API.formatCurrency(w.total_earned)}</div>
            <div class="font-label-lg text-label-lg text-error">${window.API.formatCurrency(w.total_advance)}</div>
            <div class="font-label-lg text-label-lg ${dueClass}">${window.API.formatCurrency(w.remaining_due)}</div>
            <div class="text-right flex items-center justify-end gap-2">
                <button onclick="event.stopPropagation(); window.API.request('navigate_to', {page: 'workers'});" class="px-3 py-1.5 bg-surface-container-highest text-on-surface rounded-lg hover:bg-surface-container-low transition-colors text-sm font-medium">
                    <span class="material-symbols-outlined text-[16px] align-middle">visibility</span> Details
                </button>
                ${w.remaining_due > 0 ? `
                <button onclick="event.stopPropagation(); settleWorkerFromPayments(${w.id}, '${w.name.replace(/'/g, "\\'")}')" class="px-3 py-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium">
                    Settle
                </button>
                ` : ''}
            </div>
        `;
        container.appendChild(div);
    });
}

window.settleWorkerFromPayments = async function(workerId, workerName) {
    if (!confirm(`Are you sure you want to settle all dues for ${workerName}? This will mark all current work entries and advances as settled.`)) {
        return;
    }
    try {
        await window.API.request('settle_worker_account', { worker_id: workerId });
        window.API.toast(`${workerName}'s account settled successfully`, 'success');
        loadWorkerPayments(); // Refresh
    } catch (e) {
        window.API.toast('Failed to settle worker account', 'error');
    }
}

// ─── Stock Payments ────────────────────────────────────────────────

async function loadStockPayments() {
    const container = document.getElementById('table-payments');
    if (!container) return;
    
    container.innerHTML = '<div class="p-4 text-center text-on-surface-variant">Loading stock data...</div>';
    
    try {
        const response = await window.API.request('get_stock_payment_summary');
        stockPaymentData = response;
        
        const summary = response.summary || { total_value: 0, total_items: 0, low_stock_count: 0 };
        
        const sv = document.getElementById('dash-stock-value');
        if (sv) {
            sv.dataset.amount = summary.total_value;
            updateKpiDisplay();
        }
        const sc = document.getElementById('dash-stock-count');
        if (sc) {
            sc.innerText = `${summary.total_items} items in inventory`;
        }

        renderStockPayments(response.items || []);
    } catch (e) {
        console.error(e);
        container.innerHTML = '<div class="p-4 text-center text-error">Failed to load stock data</div>';
    }
}

function renderStockPayments(items) {
    const container = document.getElementById('table-payments');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (items.length === 0) {
        container.innerHTML = '<div class="p-4 text-center text-on-surface-variant w-full">No stock items found</div>';
        return;
    }
    
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'grid grid-cols-1 md:grid-cols-6 gap-4 items-center bg-white p-4 rounded-lg border border-surface-container-highest hover:shadow-md transition-shadow';
        
        const lowClass = item.is_low ? 'bg-error/10 border-error/30' : '';
        if (item.is_low) div.className += ' ' + lowClass;
        
        const statusBadge = item.is_low 
            ? '<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-error/10 text-error font-label-sm text-[12px]"><span class="material-symbols-outlined text-[14px]">warning</span> Low Stock</span>'
            : '<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#10b981]/10 text-[#10b981] font-label-sm text-[12px]"><span class="material-symbols-outlined text-[14px]">check_circle</span> In Stock</span>';
        
        div.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-surface-container-highest flex items-center justify-center text-on-surface-variant">
                    <span class="material-symbols-outlined text-[20px]">inventory_2</span>
                </div>
                <div>
                    <p class="font-label-lg text-label-lg text-on-surface">${item.name}</p>
                </div>
            </div>
            <div class="font-body-md text-body-md text-on-surface-variant">${item.category}</div>
            <div class="font-label-lg text-label-lg text-on-surface">${item.quantity} ${item.unit}</div>
            <div class="font-body-md text-body-md text-on-surface-variant">${item.unit_cost > 0 ? window.API.formatCurrency(item.unit_cost) : '—'}</div>
            <div class="font-label-lg text-label-lg text-on-surface">${item.total_value > 0 ? window.API.formatCurrency(item.total_value) : '—'}</div>
            <div class="text-right">${statusBadge}</div>
        `;
        container.appendChild(div);
    });
}

// ─── Existing Payments Logic ───────────────────────────────────────

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
    
    // Filter pending orders
    const filteredPending = allPendingOrders.filter(o => 
        (o.customer_name && o.customer_name.toLowerCase().includes(q)) || 
        (o.customer_mobile && String(o.customer_mobile).toLowerCase().includes(q)) ||
        (o.order_number && String(o.order_number).toLowerCase().includes(q)) ||
        (o.id && String(o.id).toLowerCase().includes(q))
    );

    // Filter transactions
    const timeFilter = document.getElementById('filter-time')?.value || 'all';
    const methodFilter = document.getElementById('filter-method')?.value || 'all';
    const now = new Date();
    
    const filteredPayments = allPayments.filter(p => {
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

    if (currentTab === 'pending') {
        renderPendingBalances(filteredPending);
    } else if (currentTab === 'workers') {
        // Workers tab uses its own loading, don't re-render here
        return;
    } else if (currentTab === 'stock') {
        // Stock tab uses its own loading, don't re-render here
        return;
    } else {
        renderPayments(filteredPayments);
        currentlyRendered = filteredPayments;
    }
    
    // Calculate pending payments using filteredPending
    let totalPendingPayments = 0;
    filteredPending.forEach(o => {
        totalPendingPayments += o.remaining_amount || 0;
    });
    
    // Update KPIs based on the filtered data
    let totalCollected = 0;
    let todayCollected = 0;
    const nowStr = now.toDateString();
    let todayCount = 0;
    
    filteredPayments.forEach(p => {
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
    if (tc) tc.dataset.amount = totalCollected;
    
    const pp = document.getElementById('dash-pending-payments');
    if (pp) pp.dataset.amount = totalPendingPayments;
    
    const tp = document.getElementById('dash-today-payments');
    if (tp) tp.dataset.amount = todayCollected;
    
    const tCount = document.getElementById('dash-today-transactions-count');
    if (tCount) tCount.innerText = `${todayCount} transactions today`;
    
    // Worker dues KPI
    if (workerPaymentData && workerPaymentData.summary) {
        const wd = document.getElementById('dash-worker-dues');
        if (wd) wd.dataset.amount = workerPaymentData.summary.total_dues || 0;
        const wc = document.getElementById('dash-worker-count');
        if (wc) wc.innerText = `${workerPaymentData.summary.worker_count || 0} active workers`;
    }
    
    // Stock value KPI
    if (stockPaymentData && stockPaymentData.summary) {
        const sv = document.getElementById('dash-stock-value');
        if (sv) sv.dataset.amount = stockPaymentData.summary.total_value || 0;
        const sc = document.getElementById('dash-stock-count');
        if (sc) sc.innerText = `${stockPaymentData.summary.total_items || 0} items in inventory`;
    }
    
    updateKpiDisplay();
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
