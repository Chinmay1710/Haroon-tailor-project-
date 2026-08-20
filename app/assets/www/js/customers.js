/**
 * customers.js - Data binding for Customer List
 */

let allCustomers = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        loadCustomers();
        
        const searchInput = document.getElementById('customer-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => filterCustomers(e.target.value));
        }
    }
    init();
});

async function loadCustomers() {
    try {
        window.API.toast("Loading customers...", "info");
        const data = await window.API.request('get_customers');
        window.API.toast("Loaded " + data.length + " customers", "success");
        allCustomers = data;
        renderCustomers(allCustomers);
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load customers: " + e, "error");
    }
}

function filterCustomers(query) {
    const q = query.toLowerCase();
    const filtered = allCustomers.filter(c => 
        c.name.toLowerCase().includes(q) || 
        c.mobile.toLowerCase().includes(q) || 
        (c.id && c.id.toString().includes(q))
    );
    renderCustomers(filtered);
}

function renderCustomers(customers) {
    try {
        const container = document.getElementById('customer-list-container');
        if (!container) {
            window.API.toast("customer-list-container not found", "error");
            return;
        }
        
        container.innerHTML = '';
        
        if (customers.length === 0) {
            container.innerHTML = '<div class="p-4 text-center text-on-surface-variant">No customers found</div>';
            return;
        }
        
        customers.forEach(customer => {
            const div = document.createElement('div');
            div.className = 'bg-surface-container-lowest rounded-xl card-shadow p-4 lg:px-6 lg:py-5 flex flex-col lg:grid lg:grid-cols-12 gap-4 lg:gap-4 items-center hover:card-shadow-hover transition-all duration-300 border border-transparent hover:border-outline-variant/20 relative group cursor-pointer';
            div.onclick = () => window.API.request('navigate_to', {page: 'customer_details', id: customer.id});
            
            const names = (customer.name || 'Unknown').split(' ');
            const initials = names.map(n => n && n.length > 0 ? n[0] : '').join('').substring(0, 2).toUpperCase() || 'CU';
            const pendingAmount = customer.pending_amount || 0;
            const lastOrder = customer.last_order || '-';
            
            div.innerHTML = `
                <div class="col-span-1 w-full flex justify-between lg:block font-body-md text-body-md text-on-surface-variant">
                    <span class="lg:hidden font-label-sm text-label-sm">ID</span>
                    #C-${customer.id.toString().padStart(4, '0')}
                </div>
                <div class="col-span-3 w-full flex items-center gap-4">
                    <div class="w-10 h-10 rounded-full bg-surface-container-highest flex items-center justify-center font-label-lg text-primary shrink-0">
                        ${initials}
                    </div>
                    <div>
                        <h3 class="font-label-lg text-label-lg text-on-surface">${customer.name}</h3>
                        <p class="font-body-sm text-[13px] text-on-surface-variant lg:hidden">#C-${customer.id.toString().padStart(4, '0')}</p>
                    </div>
                </div>
                <div class="col-span-2 w-full flex justify-between lg:block font-body-md text-body-md text-on-surface">
                    <span class="lg:hidden font-label-sm text-label-sm text-on-surface-variant">Mobile</span>
                    ${customer.mobile}
                </div>
                <div class="col-span-2 w-full flex justify-between lg:justify-center lg:block text-center font-label-lg text-label-lg text-on-surface">
                    <span class="lg:hidden font-label-sm text-label-sm text-on-surface-variant">Orders</span>
                    <span class="inline-flex items-center justify-center bg-surface-container w-8 h-8 rounded-full">${customer.orders_count || 0}</span>
                </div>
                <div class="col-span-2 w-full flex justify-between lg:justify-end lg:block text-right font-label-lg text-label-lg ${pendingAmount > 0 ? 'text-error' : 'text-on-surface-variant font-body-md'}">
                    <span class="lg:hidden font-label-sm text-label-sm text-on-surface-variant">Pending</span>
                    ${window.API && window.API.formatCurrency ? window.API.formatCurrency(pendingAmount) : '$' + pendingAmount}
                </div>
                <div class="col-span-1 w-full flex justify-between lg:justify-center lg:block text-center font-body-md text-body-md text-on-surface-variant">
                    <span class="lg:hidden font-label-sm text-label-sm text-on-surface-variant">Last Order</span>
                    ${lastOrder}
                </div>
                <div class="col-span-1 w-full flex justify-end gap-2 lg:opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <button onclick="event.stopPropagation(); window.showDeleteModal(${customer.id});" class="p-2 bg-error-container text-error rounded-lg hover:bg-error hover:text-on-error transition-colors shadow-sm" title="Delete Customer">
                        <span class="material-symbols-outlined text-[20px]" data-icon="delete">delete</span>
                    </button>
                    <button onclick="event.stopPropagation(); window.API.request('navigate_to', {page: 'customer_details', id: ${customer.id}});" class="p-2 bg-surface-container rounded-lg text-primary hover:bg-primary hover:text-on-primary transition-colors shadow-sm" title="View Customer">
                        <span class="material-symbols-outlined text-[20px]" data-icon="visibility">visibility</span>
                    </button>
                </div>
            `;
            container.appendChild(div);
        });
    } catch(err) {
        if(window.API && window.API.toast) {
            window.API.toast("Render Error: " + err.message, "error");
        }
        console.error(err);
    }
}
