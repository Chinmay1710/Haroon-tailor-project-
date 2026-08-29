/**
 * receipt_preview.js - Render dynamic receipt data before printing (58mm POS format)
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
            document.getElementById('rp-order-number').textContent = "Error";
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
        document.getElementById('rp-date').textContent = window.API.formatDate(new Date());
        
        document.getElementById('rp-customer-name').textContent = o.customer_name || 'Walk-in';
        document.getElementById('rp-customer-mobile').textContent = o.customer_mobile ? `Ph: ${o.customer_mobile}` : '';
        
        document.getElementById('rp-delivery-date').textContent = window.API.formatDate(o.delivery_date);
        
        const tbody = document.getElementById('rp-items-tbody');
        tbody.innerHTML = '';
        
        if (o.items && o.items.length > 0) {
            o.items.forEach(item => {
                const total = (item.price || 0) * (item.quantity || 1);
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.marginBottom = '2px';
                div.innerHTML = `
                    <div style="width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${item.clothing_type || 'Custom'}</div>
                    <div style="width: 15%; text-align: center;">${item.quantity || 1}</div>
                    <div style="width: 35%; text-align: right;">${window.API.formatCurrency(total)}</div>
                `;
                tbody.appendChild(div);
                
            });
        } else {
            const div = document.createElement('div');
            div.style.display = 'flex';
            div.innerHTML = `
                <div style="width: 50%;">Custom</div>
                <div style="width: 15%; text-align: center;">1</div>
                <div style="width: 35%; text-align: right;">${window.API.formatCurrency(o.total_amount)}</div>
            `;
            tbody.appendChild(div);
        }
        
        document.getElementById('rp-total').textContent = window.API.formatCurrency(o.total_amount);
        
        const histContainer = document.getElementById('rp-paid-history');
        histContainer.innerHTML = '';
        
        if (o.payments && o.payments.length > 0) {
            o.payments.forEach(p => {
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.justifyContent = 'space-between';
                div.innerHTML = `
                    <span>Paid (${window.API.formatDate(p.payment_date)}):</span>
                    <span>-${window.API.formatCurrency(p.amount)}</span>
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

window.savePdf = async function() {
    let navParamsStr = sessionStorage.getItem("nav_params");
    let navParams = navParamsStr ? JSON.parse(navParamsStr) : null;
    if (!navParams || !navParams.order_id) return;
    
    try {
        const res = await window.API.request('save_pdf', {type: 'receipt', order_id: navParams.order_id});
        window.API.toast(res?.message || "Saved successfully!", "success");
    } catch (e) {
        if (e !== "Save cancelled") {
            console.error(e);
            window.API.toast(e, "error");
        }
    }
};
