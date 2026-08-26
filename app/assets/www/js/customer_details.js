/**
 * customer_details.js - Data binding for Customer Details page
 */

let currentCustomerId = null;

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        
        let navParamsStr = sessionStorage.getItem("nav_params");
        let navParams = navParamsStr ? JSON.parse(navParamsStr) : null;
        
        if (!navParams || !navParams.id) {
            window.API.toast("No customer ID provided.", "error");
            document.getElementById('cd-name').textContent = "Error: Customer ID Missing";
            return;
        }
        
        currentCustomerId = navParams.id;
        loadCustomerDetails(navParams.id);
        
        // Attach Dictation Mic to large textareas
        setTimeout(() => {
            if (window.API && window.API.attachMic) {
                window.API.attachMic('edit-address');
                window.API.attachMic('edit-notes');
            }
        }, 100);
    }
    init();
});

window.gotoNewOrder = function() {
    if (currentCustomerId) {
        window.API.request('navigate_to', {page: 'new_order', customer_id: currentCustomerId});
    }
};

window.gotoAddMeasurement = function() {
    if (currentCustomerId) {
        window.API.request('navigate_to', {page: 'add_measurement', customer_id: currentCustomerId});
    }
};

window.deleteCustomer = async function() {
    if (!currentCustomerId) return;
    
    try {
        await window.API.request('delete_customer', { id: currentCustomerId });
        window.API.toast("Customer deleted successfully", "success");
        window.API.request('navigate_to', {page: 'customers_list'});
    } catch (e) {
        window.API.toast("Failed to delete customer: " + e, "error");
        
        // Reset button state on failure
        const btn = document.getElementById('btn-confirm-delete');
        if (btn) {
            btn.innerHTML = 'Delete';
            btn.disabled = false;
        }
    }
};

window.editCustomer = function() {
    if (!currentCustomerId) return;
    
    // Pre-fill form from current displayed data
    const name = document.getElementById('cd-name').textContent;
    const mobile = document.getElementById('cd-mobile').textContent;
    const address = document.getElementById('cd-address').textContent;
    const notes = document.getElementById('cd-notes').textContent;
    
    document.getElementById('edit-name').value = (name && name !== 'Unknown Customer') ? name : '';
    document.getElementById('edit-mobile').value = (mobile && mobile !== 'No Mobile') ? mobile : '';
    document.getElementById('edit-address').value = (address && address !== 'No Address Provided') ? address : '';
    document.getElementById('edit-notes').value = (notes && notes !== 'No Notes') ? notes : '';
    
    showEditModal();
};

window.saveCustomerEdit = async function() {
    if (!currentCustomerId) return;
    
    const name = document.getElementById('edit-name').value.trim();
    if (!name) {
        window.API.toast("Customer name is required", "error");
        return;
    }
    const nameRegex = /^[A-Za-z\s]+$/;
    if (!nameRegex.test(name)) {
        window.API.toast("Name should contain only letters and spaces", "error");
        return;
    }

    const mobile = document.getElementById('edit-mobile').value.trim();
    if (!mobile) {
        window.API.toast("Mobile is required", "error");
        return;
    }
    const mobileRegex = /^\+91 [0-9]{10}$/;
    if (!mobileRegex.test(mobile)) {
        window.API.toast("Mobile number must be exactly 10 digits (e.g. +91 9876543210)", "error");
        return;
    }
    
    const btn = document.getElementById('btn-save-edit');
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span> Saving...';
    btn.disabled = true;
    
    try {
        await window.API.request('update_customer', {
            id: currentCustomerId,
            name: name,
            mobile: document.getElementById('edit-mobile').value.trim(),
            address: document.getElementById('edit-address').value.trim(),
            notes: document.getElementById('edit-notes').value.trim()
        });
        
        window.API.toast("Customer updated successfully", "success");
        hideEditModal();
        
        // Refresh the page data
        loadCustomerDetails(currentCustomerId);
    } catch (e) {
        window.API.toast("Failed to update customer: " + e, "error");
    } finally {
        btn.innerHTML = originalHTML;
        btn.disabled = false;
    }
};

async function loadCustomerDetails(id) {
    try {
        const data = await window.API.request('get_customer_details', {id: id});
        renderCustomer(data.customer);
        renderOrders(data.orders);
        renderMeasurements(data.profiles);
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load customer details: " + e, "error");
        document.getElementById('cd-name').textContent = "Error Loading Data";
    }
}

function renderCustomer(c) {
    document.getElementById('cd-name').textContent = c.name || 'Unknown Customer';
    document.getElementById('cd-mobile').textContent = c.mobile || 'No Mobile';
    document.getElementById('cd-address').textContent = c.address || 'No Address Provided';
    document.getElementById('cd-notes').textContent = c.notes || 'No Notes';
    document.getElementById('cd-subtitle').textContent = `Customer ID: #C-${c.id.toString().padStart(4, '0')}`;
}

function renderOrders(orders) {
    const list = document.getElementById('cd-orders-list');
    if (!list) return;
    
    list.innerHTML = '';
    
    if (!orders || orders.length === 0) {
        list.innerHTML = '<div class="p-4 text-center text-on-surface-variant bg-surface-container-lowest rounded-xl border border-surface-container-high/50">No orders found</div>';
        return;
    }
    
    // Sort by order_date desc
    orders.sort((a, b) => new Date(b.order_date) - new Date(a.order_date));
    
    orders.forEach(o => {
        let isOverdue = o.status === 'OVERDUE' || (o.status !== 'DELIVERED' && o.status !== 'CANCELLED' && o.delivery_date && new Date(o.delivery_date) < new Date());
        
        let statusStyle = 'bg-surface-container-highest text-on-surface-variant';
        let statusIcon = 'inventory_2';
        let displayStatus = o.status;
        
        if (isOverdue) {
            statusStyle = 'bg-error-container text-on-error-container';
            statusIcon = 'error';
            displayStatus = 'OVERDUE';
        } else if (o.status === 'STITCHING_COMPLETE') {
            statusStyle = 'bg-tertiary-container text-on-tertiary-container';
            statusIcon = 'check_circle';
        } else if (o.status === 'CUTTING_COMPLETE') {
            statusStyle = 'bg-primary-container text-on-primary-container';
            statusIcon = 'cut';
        } else if (o.status === 'NEW') {
            statusStyle = 'bg-surface-container text-on-surface';
            statusIcon = 'add_circle';
        }

        const div = document.createElement('div');
        div.className = 'bg-surface-container-lowest rounded-xl p-4 shadow-[0_2px_10px_rgba(0,0,0,0.02)] border border-surface-container-high/50 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:shadow-[0_4px_15px_rgba(0,0,0,0.05)] transition-shadow cursor-pointer';
        div.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: o.id});
        
        div.innerHTML = `
            <div class="flex items-center gap-4 w-full md:w-auto">
                <div class="w-12 h-12 bg-surface-container rounded-lg flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-primary">checkroom</span>
                </div>
                <div>
                    <p class="font-label-lg text-label-lg text-on-surface">${o.clothing_type || 'Custom Item'}</p>
                    <p class="font-body-md text-body-md text-on-surface-variant">${o.order_number} • ${window.API.formatDate(o.order_date)}</p>
                </div>
            </div>
            <div class="flex items-center justify-between w-full md:w-auto gap-8">
                <div class="text-left md:text-right">
                    <p class="font-label-sm text-label-sm text-on-surface-variant">Amount</p>
                    <p class="font-label-lg text-label-lg text-on-surface">${window.API.formatCurrency(o.total_amount)}</p>
                </div>
                <div class="text-left md:text-right">
                    <p class="font-label-sm text-label-sm text-on-surface-variant">Delivery</p>
                    <p class="font-label-lg text-label-lg text-on-surface">${window.API.formatDate(o.delivery_date)}</p>
                </div>
                <span class="${statusStyle} px-3 py-1 rounded-full font-label-sm text-label-sm shrink-0 flex items-center gap-1">
                    <span class="material-symbols-outlined text-[14px]">${statusIcon}</span> ${displayStatus}
                </span>
            </div>
        `;
        list.appendChild(div);
    });
}

function renderMeasurements(profiles) {
    const grid = document.getElementById('cd-measurements-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    if (!profiles || profiles.length === 0) {
        grid.innerHTML = '<div class="col-span-2 text-center text-on-surface-variant p-4">No measurements available.</div>';
        return;
    }
    
    // Pick the most recent profile to show on the dashboard
    profiles.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    const p = profiles[0];
    
    const keys = Object.keys(p.values);
    if (keys.length === 0) {
        grid.innerHTML = '<div class="col-span-2 text-center text-on-surface-variant p-4">Measurement profile is empty.</div>';
        return;
    }
    
    keys.slice(0, 8).forEach(key => { // Show up to 8 fields
        const div = document.createElement('div');
        div.className = 'bg-surface p-3 rounded-lg border border-surface-container-high text-center';
        div.innerHTML = `
            <p class="font-label-sm text-label-sm text-on-surface-variant uppercase truncate" title="${key}">${key.replace('_', ' ')}</p>
            <p class="font-headline-md text-headline-md text-primary mt-1">${p.values[key]}<span class="text-sm font-normal text-on-surface-variant">"</span></p>
        `;
        grid.appendChild(div);
    });
}
