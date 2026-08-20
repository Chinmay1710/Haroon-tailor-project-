/**
 * receipt_preview.js - Render dynamic receipt data before printing
 */

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        
        let navParamsStr = sessionStorage.getItem("nav_params");
        let navParams = navParamsStr ? JSON.parse(navParamsStr) : null;
        
        if (!navParams || !navParams.order_id) {
            window.API.toast("No order ID provided.", "error");
            document.getElementById('rp-order-number').textContent = "Error: Order ID Missing";
            return;
        }
        
        loadOrderData(navParams.order_id);
    }
    init();
});

async function loadOrderData(orderId) {
    try {
        const o = await window.API.request('get_order_details', {id: orderId});
        
        document.getElementById('rp-order-number').textContent = o.order_number;
        document.getElementById('rp-date').textContent = "Date: " + window.API.formatDate(new Date());
        
        document.getElementById('rp-customer-name').textContent = o.customer_name || 'Walk-in Customer';
        document.getElementById('rp-customer-mobile').textContent = o.customer_mobile || '';
        document.getElementById('rp-customer-address').textContent = o.customer_address || '';
        
        document.getElementById('rp-order-date').textContent = window.API.formatDate(o.order_date);
        document.getElementById('rp-delivery-date').textContent = window.API.formatDate(o.delivery_date);
        document.getElementById('rp-status').textContent = o.status;
        
        const tbody = document.getElementById('rp-items-tbody');
        tbody.innerHTML = '';
        
        const tr = document.createElement('tr');
        tr.className = 'border-b border-outline-variant/50';
        tr.innerHTML = `
            <td class="py-4 px-2">
                <p class="font-label-lg text-label-lg">${o.clothing_type || 'Custom Item'}</p>
                <p class="text-on-surface-variant text-sm mt-1">${o.special_instructions || ''}</p>
            </td>
            <td class="py-4 px-2 text-center">${o.quantity}</td>
            <td class="py-4 px-2 text-right">${window.API.formatCurrency(o.total_amount / (o.quantity || 1))}</td>
            <td class="py-4 px-2 text-right font-label-lg text-label-lg">${window.API.formatCurrency(o.total_amount)}</td>
        `;
        tbody.appendChild(tr);
        
        document.getElementById('rp-total').textContent = window.API.formatCurrency(o.total_amount);
        
        const histContainer = document.getElementById('rp-paid-history');
        histContainer.innerHTML = '';
        
        if (o.payments && o.payments.length > 0) {
            o.payments.forEach(p => {
                const div = document.createElement('div');
                div.className = 'flex justify-between py-2 font-body-md text-body-md text-on-surface';
                div.innerHTML = `
                    <span>Payment (${window.API.formatDate(p.payment_date)}) - ${p.payment_method}:</span>
                    <span class="text-primary-fixed-dim">-${window.API.formatCurrency(p.amount)}</span>
                `;
                histContainer.appendChild(div);
            });
        }
        
        document.getElementById('rp-balance').textContent = window.API.formatCurrency(o.remaining_amount);
        
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load receipt: " + e, "error");
    }
}
