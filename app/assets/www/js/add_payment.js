/**
 * add_payment.js - Logic for recording a new payment
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
            document.getElementById('ap-customer-info').textContent = "Error: Order ID Missing";
            return;
        }
        
        loadOrderData(navParams.order_id);
        
        document.getElementById('ap-submit-btn').addEventListener('click', function() {
            submitPayment(navParams.order_id);
        });
    }
    init();
});

let currentOrderData = null;

async function loadOrderData(orderId) {
    try {
        const data = await window.API.request('get_order_details', {id: orderId});
        currentOrderData = data;
        
        document.getElementById('ap-customer-info').textContent = `${data.customer_name} - ${data.order_number}`;
        document.getElementById('ap-order-info').textContent = `${data.clothing_type || 'Custom Item'} (Qty: ${data.quantity})`;
        
        const avatar = document.getElementById('ap-avatar');
        if (data.customer_name) {
            avatar.textContent = data.customer_name.substring(0, 2).toUpperCase();
        }
        
        // Finances
        document.getElementById('ap-order-total').textContent = window.API.formatCurrency(data.total_amount);
        const paid = data.total_amount - data.remaining_amount;
        document.getElementById('ap-previous-paid').textContent = window.API.formatCurrency(paid);
        document.getElementById('ap-current-balance').textContent = window.API.formatCurrency(data.remaining_amount);
        
        // Auto-fill amount with remaining balance
        const amountInput = document.getElementById('ap-amount');
        amountInput.value = data.remaining_amount.toFixed(2);
        amountInput.max = data.remaining_amount.toFixed(2);
        
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load order for payment: " + e, "error");
    }
}

async function submitPayment(orderId) {
    const amount = parseFloat(document.getElementById('ap-amount').value);
    
    if (isNaN(amount) || amount <= 0) {
        window.API.toast("Please enter a valid amount.", "error");
        return;
    }
    
    if (amount > currentOrderData.remaining_amount) {
        window.API.toast("Amount exceeds remaining balance.", "error");
        return;
    }
    
    // Get selected payment method
    const radios = document.getElementsByName('payment_method');
    let selectedMethod = "Cash";
    for (const r of radios) {
        if (r.checked) {
            selectedMethod = r.value;
            break;
        }
    }
    
    const btn = document.getElementById('ap-submit-btn');
    const originalContent = btn.innerHTML;
    
    btn.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> Processing...';
    btn.disabled = true;
    
    try {
        await window.API.request('create_payment', {
            order_id: orderId,
            amount: amount,
            payment_method: selectedMethod
        });
        
        btn.innerHTML = '<span class="material-symbols-outlined" data-weight="fill">done_all</span> Payment Saved';
        btn.classList.replace('bg-primary', 'bg-[#16a34a]');
        
        document.getElementById('confirmation-card').classList.remove('hidden');
        
        let navParamsStr = sessionStorage.getItem("nav_params");
        let navParams = navParamsStr ? JSON.parse(navParamsStr) : {};
        
        setTimeout(async () => {
            if (navParams.complete_after) {
                try {
                    await window.API.request('update_order_status', {order_id: orderId, status: 'DELIVERED'});
                    window.API.request('navigate_to', {page: 'orders_list'});
                } catch (e) {
                    window.API.toast("Payment saved but failed to complete order: " + e, "error");
                    window.API.request('navigate_to', {page: 'orders_list'});
                }
            } else {
                window.API.request('navigate_to', {page: 'order_details', id: orderId});
            }
        }, 1500);
        
    } catch (e) {
        btn.innerHTML = originalContent;
        btn.disabled = false;
        window.API.toast("Failed to record payment: " + e, "error");
    }
}
