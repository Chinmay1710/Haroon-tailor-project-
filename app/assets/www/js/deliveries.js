/**
 * deliveries.js - Data binding for Deliveries page
 */

let allDeliveries = [];
let activeFilter = 'All';

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        setupFilters();
        loadDeliveries();
    }
    init();
});

function setupFilters() {
    const filterButtons = document.querySelectorAll('#delivery-filter-buttons button');
    if (!filterButtons.length) return;
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update UI
            filterButtons.forEach(b => {
                b.className = "whitespace-nowrap px-4 py-2 rounded-full bg-surface-container-lowest border border-outline-variant text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors font-label-lg text-label-lg";
            });
            btn.className = "whitespace-nowrap px-4 py-2 rounded-full bg-primary text-on-primary font-label-lg text-label-lg shadow-sm";
            
            // Set filter and re-render
            activeFilter = btn.getAttribute('data-filter');
            renderDeliveries(allDeliveries);
        });
    });
}

async function loadDeliveries() {
    try {
        const data = await window.API.request('get_deliveries_dashboard');
        allDeliveries = data.deliveries;
        renderDeliveries(allDeliveries);
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load deliveries", "error");
    }
}

function createCard(d, isCompact = false) {
    const today = new Date();
    today.setHours(0,0,0,0);
    const dDate = new Date(d.delivery_date);
    dDate.setHours(0,0,0,0);
    const isOverdue = dDate < today;
    
    const totalAmount = parseFloat(d.total_amount) || 0;
    const advancePaid = parseFloat(d.advance_paid) || 0;
    const pendingAmount = totalAmount - advancePaid;
    const hasPendingPayment = pendingAmount > 0;
    
    const paymentBadge = hasPendingPayment 
        ? `<span class="px-2 py-1 bg-error/10 text-error rounded-full font-label-sm text-[11px] uppercase tracking-wider" title="Pending Payment">Due: ₹${pendingAmount}</span>`
        : `<span class="px-2 py-1 bg-primary/10 text-primary rounded-full font-label-sm text-[11px] uppercase tracking-wider" title="Fully Paid">Paid</span>`;
    
    const statusBadge = `<span class="px-2 py-1 bg-[#10b981]/10 text-[#047857] rounded-full font-label-sm text-[11px] uppercase tracking-wider">${d.status}</span>`;
    
    const card = document.createElement('div');
    card.onclick = () => window.API.request('navigate_to', {page: 'order_details', id: d.id});
    
    if (isCompact) {
        card.className = "cursor-pointer bg-surface-container-lowest rounded-lg p-3 border border-outline-variant/50 hover:border-primary-fixed transition-colors";
        card.innerHTML = `
            <div class="flex justify-between items-start mb-2">
                <div>
                    <p class="font-label-lg text-label-lg text-primary">${d.customer_name || 'Unknown'}</p>
                    <p class="font-label-sm text-label-sm text-on-surface-variant">${d.order_number} • ${d.items}</p>
                </div>
                <div class="flex flex-col gap-1 items-end">
                    ${statusBadge}
                    ${paymentBadge}
                </div>
            </div>
            <div class="flex items-center justify-end mt-2 pt-2 border-t border-outline-variant/30">
                <button onclick="event.stopPropagation(); updateStatus(${d.id}, 'DELIVERED');" class="text-primary hover:underline font-label-sm text-[12px]">Deliver</button>
            </div>
        `;
        return card;
    }
    
    card.className = "cursor-pointer transition-transform hover:-translate-y-1 group bg-surface-container-lowest rounded-xl p-4 card-shadow" + (isOverdue ? " border-l-4 border-error" : "");
    const dateText = isOverdue ? `${window.API.formatDate(d.delivery_date)} (Overdue)` : window.API.formatDate(d.delivery_date);
    
    card.innerHTML = `
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div class="flex flex-col sm:flex-row gap-4 sm:gap-8 flex-1">
                <div class="w-24">
                    <p class="font-label-sm text-label-sm text-on-surface-variant mb-1">${d.order_number}</p>
                    <p class="font-label-lg text-label-lg text-primary">${d.customer_name || 'Unknown'}</p>
                </div>
                <div class="w-40">
                    <p class="font-label-sm text-label-sm text-on-surface-variant mb-1">Item</p>
                    <p class="font-body-md text-body-md text-on-surface">${d.items}</p>
                </div>
                <div>
                    <p class="font-label-sm text-label-sm text-on-surface-variant mb-1">Due Date</p>
                    <p class="font-label-lg text-label-lg ${isOverdue ? 'text-error' : 'text-primary'}">${dateText}</p>
                </div>
                <div class="flex gap-2 items-center sm:ml-auto flex-wrap">
                    ${statusBadge}
                    ${paymentBadge}
                </div>
            </div>
            <div class="flex gap-2 border-t sm:border-t-0 sm:border-l border-outline-variant pt-3 sm:pt-0 sm:pl-4 opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity">
                <button onclick="event.stopPropagation(); updateStatus(${d.id}, 'DELIVERED');" class="flex-1 sm:flex-none justify-center flex items-center gap-2 bg-primary text-on-primary px-3 py-2 rounded-lg hover:bg-primary/90 transition-colors font-label-sm text-label-sm whitespace-nowrap">
                    <span class="material-symbols-outlined text-[18px]">local_shipping</span> Deliver
                </button>
            </div>
        </div>
    `;
    return card;
}

function renderDeliveries(deliveries) {
    const readyC = document.getElementById('ready-container');
    if(readyC) readyC.innerHTML = '';
    
    // Filter first
    const filtered = deliveries.filter(d => {
        if (activeFilter === 'All') return true;
        
        const totalAmount = parseFloat(d.total_amount) || 0;
        const advancePaid = parseFloat(d.advance_paid) || 0;
        const pendingAmount = totalAmount - advancePaid;
        
        if (activeFilter === 'Pending Payment') return pendingAmount > 0;
        if (activeFilter === 'Paid') return pendingAmount <= 0;
        return true;
    });
    
    if (readyC) {
        if (filtered.length === 0) {
            readyC.innerHTML = '<div class="text-center p-8 text-on-surface-variant bg-surface-container-lowest rounded-xl border border-outline-variant/30">No ready deliveries found</div>';
        } else {
            filtered.forEach(d => {
                readyC.appendChild(createCard(d, false)); // full size cards for all
            });
        }
    }
    
    // Update count dynamically
    const elTotal = document.getElementById('del-total-count');
    if (elTotal) elTotal.innerText = filtered.length;
}

window.updateStatus = async function(orderId, newStatus) {
    try {
        await window.API.request('update_order_status', {id: orderId, status: newStatus});
        window.API.toast(`Order marked as ${newStatus}`, "success");
        loadDeliveries();
    } catch (e) {
        window.API.toast(e.toString(), "error");
    }
}
