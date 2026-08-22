/**
 * payments.js - Data binding for Payments List
 */

let allPayments = [];
let currentlyRendered = [];

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
        applyFilters();
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load payments", "error");
    }
    
    try {
        const dash = await window.API.request('get_payments_dashboard');
        const tc = document.getElementById('dash-total-collected');
        if (tc) tc.textContent = window.API.formatCurrency(dash.total_collected || 0);
        
        const pp = document.getElementById('dash-pending-payments');
        if (pp) pp.textContent = window.API.formatCurrency(dash.pending_payments || 0);
        
        const tp = document.getElementById('dash-today-payments');
        if (tp) tp.textContent = window.API.formatCurrency(dash.today_payments || 0);
    } catch (e) {
        console.error("Failed to load dashboard metrics", e);
    }
}

function filterPayments(query) {
    applyFilters();
}

function applyFilters() {
    const q = (document.getElementById('payment-search')?.value || '').toLowerCase();
    const timeFilter = document.getElementById('filter-time')?.value || 'today';
    const methodFilter = document.getElementById('filter-method')?.value || 'all';
    
    const now = new Date();
    
    const filtered = allPayments.filter(p => {
        const matchesSearch = (p.customer_name && p.customer_name.toLowerCase().includes(q)) || 
                              (p.order_number && p.order_number.toLowerCase().includes(q));
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
