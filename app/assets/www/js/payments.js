/**
 * payments.js - Data binding for Payments List
 */

let allPayments = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        loadPayments();
        
        const searchInput = document.getElementById('payment-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => filterPayments(e.target.value));
        }
    }
    init();
});

async function loadPayments() {
    try {
        const data = await window.API.request('get_all_payments');
        allPayments = data;
        renderPayments(allPayments);
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
    const q = query.toLowerCase();
    const filtered = allPayments.filter(p => 
        (p.customer_name && p.customer_name.toLowerCase().includes(q)) || 
        (p.order_number && p.order_number.toLowerCase().includes(q))
    );
    renderPayments(filtered);
}

function renderPayments(payments) {
    const tbody = document.getElementById('table-payments');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (payments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="p-4 text-center text-on-surface-variant">No payments found</td></tr>';
        return;
    }
    
    payments.forEach(p => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-surface-container last:border-0 hover:bg-surface-container-highest/20 transition-colors cursor-pointer';
        // Assume navigate to order details to see payment history
        tr.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: p.order_id});
        
        const methodIcons = {
            'CASH': 'payments',
            'UPI': 'qr_code_scanner',
            'CARD': 'credit_card',
            'BANK': 'account_balance'
        };
        const methodIcon = methodIcons[p.payment_method?.toUpperCase()] || 'payments';
        
        tr.innerHTML = `
            <td class="p-4 font-medium text-primary">${p.order_number}</td>
            <td class="p-4">
                <p class="font-label-lg text-on-surface">${p.customer_name}</p>
            </td>
            <td class="p-4 text-on-surface-variant">${window.API.formatDate(p.payment_date)}</td>
            <td class="p-4">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-outline text-[18px]">${methodIcon}</span>
                    <span class="text-on-surface-variant">${p.payment_method || 'CASH'}</span>
                </div>
            </td>
            <td class="p-4 font-medium">${window.API.formatCurrency(p.amount)}</td>
            <td class="p-4 text-right">
                <button onclick="event.stopPropagation(); window.API.request('print_receipt', {payment_id: ${p.id}});" class="w-8 h-8 rounded-full hover:bg-surface-container-highest text-on-surface-variant flex items-center justify-center transition-colors">
                    <span class="material-symbols-outlined text-[20px]">print</span>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}
