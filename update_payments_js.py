import re

with open("app/assets/www/js/payments.js", "r") as f:
    content = f.read()

new_func = """function renderPayments(payments) {
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
}"""

content = re.sub(r'function renderPayments\(payments\) \{.*?^\}$', new_func, content, flags=re.DOTALL|re.MULTILINE)

with open("app/assets/www/js/payments.js", "w") as f:
    f.write(content)
