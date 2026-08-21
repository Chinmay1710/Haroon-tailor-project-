with open("app/assets/www/js/add_payment.js", "r") as f:
    content = f.read()

new_content = """/**
 * add_payment.js - Logic for recording a new payment
 */

let currentOrderData = null;
let allActiveOrders = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        
        let navParamsStr = sessionStorage.getItem("nav_params");
        let navParams = navParamsStr ? JSON.parse(navParamsStr) : null;
        
        const changeBtn = document.getElementById('change-order-btn');
        const select = document.getElementById('ap-order-select');
        const card = document.getElementById('order-info-card');
        
        if (changeBtn) {
            changeBtn.addEventListener('click', () => {
                card.classList.add('hidden');
                select.classList.remove('hidden');
                loadAllOrdersForSelection();
            });
        }
        
        if (select) {
            select.addEventListener('change', (e) => {
                if (e.target.value) {
                    loadOrderData(e.target.value);
                    select.classList.add('hidden');
                    card.classList.remove('hidden');
                }
            });
        }
        
        if (navParams && navParams.order_id) {
            // Passed from another page
            loadOrderData(navParams.order_id);
            if (changeBtn) changeBtn.classList.add('hidden'); // don't let them change if coming from context
        } else {
            // Opened from generic Payments dashboard
            document.getElementById('ap-customer-info').textContent = "Select an order";
            document.getElementById('ap-order-info').textContent = "No order selected";
            card.classList.add('hidden');
            select.classList.remove('hidden');
            loadAllOrdersForSelection();
        }
        
        document.getElementById('ap-submit-btn').addEventListener('click', function() {
            if (!currentOrderData) {
                window.API.toast("Please select an order first.", "error");
                return;
            }
            submitPayment(currentOrderData.id);
        });
    }
    init();
});

async function loadAllOrdersForSelection() {
    try {
        const select = document.getElementById('ap-order-select');
        select.innerHTML = '<option value="">Loading orders...</option>';
        
        const orders = await window.API.request('get_all_orders');
        allActiveOrders = orders.filter(o => o.remaining_amount > 0 && o.status !== 'DELIVERED');
        
        select.innerHTML = '<option value="">Select an active order...</option>';
        
        if (allActiveOrders.length === 0) {
            select.innerHTML = '<option value="">No orders with pending balance</option>';
            return;
        }
        
        allActiveOrders.forEach(o => {
            const opt = document.createElement('option');
            opt.value = o.id;
            opt.textContent = `${o.order_number} - ${o.customer_name} (Due: ${window.API.formatCurrency(o.remaining_amount)})`;
            select.appendChild(opt);
        });
        
    } catch (e) {
        console.error("Failed to load orders for selection", e);
        window.API.toast("Failed to load orders", "error");
    }
}

async function loadOrderData(orderId) {
    try {
        const data = await window.API.request('get_order_details', {id: orderId});
        currentOrderData = data;
        
        document.getElementById('ap-customer-info').textContent = `${data.customer_name} - ${data.order_number}`;
        
        const garmentText = data.items && data.items.length > 0 
            ? data.items.map(i => `${i.clothing_type || 'Custom Item'} (x${i.quantity || 1})`).join(", ")
            : "Custom Item (x1)";
            
        document.getElementById('ap-order-info').textContent = garmentText;
        
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
        
        const changeBtn = document.getElementById('change-order-btn');
        if (changeBtn) changeBtn.classList.remove('hidden');
        
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
        
        window.API.toast("Payment recorded successfully", "success");
        
        setTimeout(() => {
            window.API.navigate('payments');
        }, 1500);
        
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to record payment: " + e, "error");
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}
"""

with open("app/assets/www/js/add_payment.js", "w") as f:
    f.write(new_content)
