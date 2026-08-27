/**
 * order_details.js - Data binding for Order Details page
 */

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        
        let navParamsStr = sessionStorage.getItem("nav_params");
        let navParams = navParamsStr ? JSON.parse(navParamsStr) : null;
        
        let orderId = navParams ? (navParams.id || navParams.order_id) : null;
        
        if (!orderId) {
            window.API.toast("No order ID provided.", "error");
            document.getElementById('od-title').textContent = "Error: Order ID Missing";
            return;
        }
        
        loadOrderDetails(orderId);
        
        document.getElementById('od-status-select').addEventListener('change', async function(e) {
            const status = e.target.value;
            const oldStatus = currentOrder ? currentOrder.status : 'NEW';
            
            if (status === 'DELIVERED') {
                if (currentOrder && currentOrder.remaining_amount > 0) {
                    window.API.toast("Pending balance exists. Redirecting to payment...", "info");
                    e.target.value = oldStatus; // Revert select
                    window.API.request('navigate_to', {page: 'add_payment', order_id: orderId, complete_after: true});
                    return; // Stop update
                }
            }
            
            let confirmResult = { confirmed: true, checked: false };
            if (status === 'STITCHING_COMPLETE' || status === 'DELIVERED') {
                confirmResult = await window.API.confirmWithCheckbox(
                    'Change Status?',
                    `Are you sure you want to change the status to ${status}?`,
                    'Send WhatsApp Notification'
                );
            } else {
                const ans = await window.API.confirm('Change Status?', `Are you sure you want to change the status to ${status}?`);
                confirmResult = { confirmed: ans, checked: false };
            }
            
            if (confirmResult.confirmed) {
                updateOrderStatus(orderId, status, confirmResult.checked);
            } else {
                e.target.value = oldStatus;
            }
        });
        
        document.getElementById('od-add-payment-btn').addEventListener('click', function() {
            window.API.request('navigate_to', {page: 'add_payment', order_id: orderId});
        });

        document.getElementById('od-print-receipt-btn').addEventListener('click', function() {
            window.API.request('navigate_to', {page: 'receipt_preview', order_id: orderId});
        });
        
        document.getElementById('od-print-slip-btn').addEventListener('click', function() {
            window.API.request('navigate_to', {page: 'stitching_slip_preview', order_id: orderId});
        });
        
        document.getElementById('od-edit-order-btn').addEventListener('click', function() {
            window.API.request('navigate_to', {page: 'new_order', order_id: orderId, action: 'edit'});
        });
        
        document.getElementById('od-mark-complete-btn').addEventListener('click', async function() {
            if (currentOrder) {
                const confirmResult = await window.API.confirmWithCheckbox(
                    'Mark Stitching Complete?',
                    'Are you sure you want to mark this order as Stitching Complete?',
                    'Send WhatsApp Notification'
                );
                
                if (confirmResult.confirmed) {
                    updateOrderStatus(orderId, 'STITCHING_COMPLETE', confirmResult.checked);
                }
            }
        });
    }
    init();
});

let currentOrder = null;

async function loadOrderDetails(id) {
    try {
        const data = await window.API.request('get_order_details', {id: id});
        currentOrder = data;
        renderOrder(data);
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load order details: " + e, "error");
        document.getElementById('od-title').textContent = "Error Loading Data";
    }
}

async function updateOrderStatus(id, status, send_whatsapp = false) {
    try {
        const res = await window.API.request('update_order_status', {order_id: id, status: status, send_whatsapp: send_whatsapp});
        window.API.toast("Status updated successfully", "success");
        // Open WhatsApp with pre-typed message
        if (res && res.whatsapp_url) {
            window.API.request('open_whatsapp_url', {url: res.whatsapp_url});
        }
    } catch (e) {
        window.API.toast("Failed to update status: " + e, "error");
        // Reload order details to revert the UI to the actual state
        loadOrderDetails(id);
    }
}

function renderOrder(o) {
    document.getElementById('od-title').textContent = `Order ${o.order_number}`;
    document.getElementById('od-subtitle').textContent = `Created on ${window.API.formatDate(o.order_date)} • Due: ${window.API.formatDate(o.delivery_date)}`;
    document.getElementById('od-status-select').value = o.status;
    
    document.getElementById('od-customer-name').textContent = o.customer_name || 'Unknown';
    document.getElementById('od-customer-mobile').textContent = o.customer_mobile || 'No mobile provided';
    document.getElementById('od-customer-address').textContent = o.customer_address || '';
    
    const markBtn = document.getElementById('od-mark-complete-btn');
    if (o.status !== 'STITCHING_COMPLETE' && o.status !== 'DELIVERED' && o.status !== 'CANCELLED') {
        markBtn.classList.remove('hidden');
    } else {
        markBtn.classList.add('hidden');
    }
    
    document.getElementById('od-view-customer-btn').onclick = () => {
        if (o.customer_id) {
            window.API.request('navigate_to', {page: 'customer_details', id: o.customer_id});
        }
    };
    
    document.getElementById('od-notes').textContent = o.special_instructions || "No special instructions provided.";
    
    // Order Items & Measurements
    const itemsContainer = document.getElementById('od-items-container');
    itemsContainer.innerHTML = '';
    
    // Fallback if no items array (legacy or backward compat)
    const items = o.items || [{
        clothing_type: o.clothing_type,
        quantity: o.quantity || 1,
        price: o.total_amount,
        measurements: o.measurement_profile ? o.measurement_profile.values : {}
    }];
    
    const totalItems = items.reduce((acc, item) => acc + (item.quantity || 1), 0);
    document.getElementById('od-items-count').textContent = totalItems + ' Items';
    
    // Clear out the old single measurement container since we'll show measurements per item
    const measContainer = document.getElementById('od-measurements-container');
    if (measContainer) {
        measContainer.parentElement.style.display = 'none';
    }
    
    items.forEach((item, index) => {
        const itemTotal = (item.quantity || 1) * (item.price || 0);
        
        const itemDiv = document.createElement('div');
        itemDiv.className = 'flex flex-col border border-outline-variant rounded-lg bg-surface mb-4 overflow-hidden';
        
        let photoHtml = '';
        if (item.image_path) {
            const paths = item.image_path.split(',').map(p => p.trim()).filter(p => p);
            photoHtml = '<div class="flex gap-2 mr-4">';
            paths.forEach(imgSrc => {
                photoHtml += `<div class="w-12 h-12 rounded overflow-hidden flex-shrink-0 border border-outline-variant cursor-pointer hover:opacity-80 transition-opacity" onclick="openImageModal('${imgSrc}')"><img src="${imgSrc}" class="w-full h-full object-cover"></div>`;
            });
            photoHtml += '</div>';
        }

        // Header
        const headerDiv = document.createElement('div');
        headerDiv.className = 'flex items-start justify-between p-4 bg-surface-container-low border-b border-outline-variant';
        headerDiv.innerHTML = `
            <div class="flex items-center">
                ${photoHtml}
                <div>
                    <h3 class="font-label-lg text-label-lg text-on-surface">${item.clothing_type || 'Custom Item'} (x${item.quantity || 1})</h3>
                    ${item.notes ? `<p class="text-body-sm text-on-surface-variant mt-1">${item.notes}</p>` : ''}
                </div>
            </div>
            <div class="text-right flex-shrink-0">
                <span class="font-label-lg text-label-lg text-on-surface">${window.API.formatCurrency(itemTotal)}</span>
            </div>
        `;
        itemDiv.appendChild(headerDiv);
        
        // Measurements for this item
        if (item.measurements && Object.keys(item.measurements).length > 0) {
            const mGrid = document.createElement('div');
            mGrid.className = 'grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2 p-4';
            
            Object.keys(item.measurements).slice(0, 12).forEach(key => {
                const val = item.measurements[key];
                const mDiv = document.createElement('div');
                mDiv.className = 'bg-surface-container-lowest rounded flex flex-col items-center justify-center text-center p-2 border border-outline-variant/30';
                mDiv.innerHTML = `
                    <span class="font-body-sm text-[10px] text-on-surface-variant uppercase truncate w-full" title="${key}">${key.replace('_', ' ')}</span>
                    <span class="font-label-lg text-primary">${val}<span class="text-xs">"</span></span>
                `;
                mGrid.appendChild(mDiv);
            });
            itemDiv.appendChild(mGrid);
        } else {
            const emptyDiv = document.createElement('div');
            emptyDiv.className = 'p-4 text-on-surface-variant text-sm italic';
            emptyDiv.textContent = 'No measurements linked.';
            itemDiv.appendChild(emptyDiv);
        }
        
        itemsContainer.appendChild(itemDiv);
    });
    
    // Finances
    document.getElementById('od-total').textContent = window.API.formatCurrency(o.total_amount);
    const paid = o.total_amount - o.remaining_amount;
    document.getElementById('od-paid').textContent = window.API.formatCurrency(paid);
    document.getElementById('od-balance').textContent = window.API.formatCurrency(o.remaining_amount);
    
    const payHistory = document.getElementById('od-payments-history');
    payHistory.innerHTML = '';
    
    if (!o.payments || o.payments.length === 0) {
        payHistory.innerHTML = '<div class="text-on-surface-variant text-center p-2">No payments yet.</div>';
    } else {
        // Sort descending
        const sortedPayments = [...o.payments].sort((a, b) => new Date(b.payment_date) - new Date(a.payment_date));
        sortedPayments.forEach(p => {
            const pDiv = document.createElement('div');
            pDiv.className = 'flex items-center justify-between';
            pDiv.innerHTML = `
                <div>
                    <p class="font-label-lg text-label-lg text-on-surface">Payment via ${p.payment_method}</p>
                    <p class="font-body-sm text-body-sm text-on-surface-variant">${window.API.formatDate(p.payment_date)}</p>
                </div>
                <span class="font-label-lg text-label-lg text-on-surface">${window.API.formatCurrency(p.amount)}</span>
            `;
            payHistory.appendChild(pDiv);
        });
    }
}

window.openImageModal = function(src) {
    if (window.event) window.event.stopPropagation();
    const modal = document.getElementById('image-modal');
    const img = document.getElementById('image-modal-content');
    if (modal && img) {
        img.src = src;
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.remove('opacity-0');
        }, 10);
    }
}

window.closeImageModal = function(event) {
    if (event) event.stopPropagation();
    const modal = document.getElementById('image-modal');
    if (modal) {
        modal.classList.add('opacity-0');
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
    }
}
