/**
 * stock.js - Stock management logic
 */

let allStockItems = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge || !window.API) {
            setTimeout(init, 100);
            return;
        }
        loadStockData();
        setupSearch();
    }
    init();
});

async function loadStockData() {
    try {
        const response = await window.API.request('get_all_stock');
        allStockItems = response || [];
        renderStockTable(allStockItems);
        updateDashboardStats(allStockItems);
    } catch (e) {
        console.error("Failed to load stock data:", e);
        window.API.toast("Failed to load stock data", "error");
    }
}

function updateDashboardStats(items) {
    document.getElementById('total-items-count').textContent = items.length;
    
    let lowStockCount = items.filter(i => i.quantity <= i.min_quantity).length;
    document.getElementById('low-stock-count').textContent = lowStockCount;
}

function renderStockTable(items) {
    const tbody = document.getElementById('stock-tbody');
    tbody.innerHTML = '';
    
    if (items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-on-surface-variant font-label-lg">No stock items found. Click 'New Item' to add one.</td></tr>`;
        return;
    }
    
    items.forEach(item => {
        const isLowStock = item.quantity <= item.min_quantity;
        const statusBadge = isLowStock 
            ? `<span class="px-2 py-1 bg-error-container text-on-error-container text-xs rounded font-bold">LOW STOCK</span>`
            : `<span class="px-2 py-1 bg-[#d3e4fe] text-[#0b1c30] text-xs rounded font-bold">OK</span>`;
        
        const qtyColor = isLowStock ? 'text-error font-bold' : 'text-on-surface';

        const tr = document.createElement('tr');
        tr.className = 'border-b border-outline-variant/30 hover:bg-surface-container/30 transition-colors';
        tr.innerHTML = `
            <td class="py-4 px-6 font-body-md text-on-surface">
                <div class="font-bold">${item.name}</div>
            </td>
            <td class="py-4 px-6 font-body-md text-on-surface-variant">${item.category}</td>
            <td class="py-4 px-6 font-body-md ${qtyColor} text-right">
                ${item.quantity} ${item.unit}
            </td>
            <td class="py-4 px-6 font-body-md text-on-surface-variant text-right">${item.min_quantity}</td>
            <td class="py-4 px-6 text-center">${statusBadge}</td>
            <td class="py-4 px-6 text-right">
                <div class="flex items-center justify-end gap-2">
                    <button onclick="openAdjustModal(${item.id})" class="p-2 text-primary hover:bg-primary/10 rounded-full transition-colors flex items-center justify-center" title="Adjust Stock">
                        <span class="material-symbols-outlined text-sm">swap_vert</span>
                    </button>
                    <button onclick="openStockModal(${item.id})" class="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high rounded-full transition-colors flex items-center justify-center" title="Edit Item">
                        <span class="material-symbols-outlined text-sm">edit</span>
                    </button>
                    <button onclick="deleteStockItem(${item.id})" class="p-2 text-on-surface-variant hover:text-error hover:bg-error/10 rounded-full transition-colors flex items-center justify-center" title="Delete Item">
                        <span class="material-symbols-outlined text-sm">delete</span>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function setupSearch() {
    const searchInput = document.getElementById('stock-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allStockItems.filter(item => 
            (item.name || '').toLowerCase().includes(query) ||
            (item.category || '').toLowerCase().includes(query)
        );
        renderStockTable(filtered);
    });
}

/* Modals Logic */

function openStockModal(itemId = null) {
    const modal = document.getElementById('stock-modal');
    
    // Reset fields
    document.getElementById('stock-id').value = '';
    document.getElementById('stock-name').value = '';
    document.getElementById('stock-category').value = 'Fabric';
    document.getElementById('stock-quantity').value = '';
    document.getElementById('stock-unit').value = 'meters';
    document.getElementById('stock-min-quantity').value = '';
    
    if (itemId) {
        document.getElementById('modal-title').textContent = 'Edit Stock Item';
        const item = allStockItems.find(i => i.id === itemId);
        if (item) {
            document.getElementById('stock-id').value = item.id;
            document.getElementById('stock-name').value = item.name;
            document.getElementById('stock-category').value = item.category;
            
            const qtyInput = document.getElementById('stock-quantity');
            qtyInput.value = item.quantity;
            qtyInput.disabled = true; // Cannot edit quantity directly in edit mode, must use adjust
            
            document.getElementById('stock-unit').value = item.unit;
            document.getElementById('stock-min-quantity').value = item.min_quantity;
        }
    } else {
        document.getElementById('modal-title').textContent = 'Add Stock Item';
        document.getElementById('stock-quantity').disabled = false;
    }
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        modal.children[0].classList.remove('scale-95');
    }, 10);
}

function closeStockModal() {
    const modal = document.getElementById('stock-modal');
    modal.classList.add('opacity-0');
    modal.children[0].classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }, 200);
}

async function saveStockItem() {
    const id = document.getElementById('stock-id').value;
    const name = document.getElementById('stock-name').value.trim();
    const category = document.getElementById('stock-category').value;
    const unit = document.getElementById('stock-unit').value;
    const min_quantity = document.getElementById('stock-min-quantity').value;
    
    if (!name) {
        window.API.toast("Item Name is required", "error");
        return;
    }

    try {
        if (id) {
            await window.API.request('update_stock_item', {
                id: parseInt(id),
                name: name,
                category: category,
                unit: unit,
                min_quantity: min_quantity
            });
            window.API.toast("Stock item updated successfully", "success");
        } else {
            const quantity = document.getElementById('stock-quantity').value;
            await window.API.request('add_stock_item', {
                name: name,
                category: category,
                quantity: quantity || 0,
                unit: unit,
                min_quantity: min_quantity || 0
            });
            window.API.toast("Stock item added successfully", "success");
        }
        
        closeStockModal();
        loadStockData();
    } catch (e) {
        window.API.toast("Failed to save: " + e, "error");
    }
}

async function deleteStockItem(id) {
    if (confirm("Are you sure you want to delete this stock item? This cannot be undone.")) {
        try {
            await window.API.request('delete_stock_item', {id: id});
            window.API.toast("Item deleted", "success");
            loadStockData();
        } catch (e) {
            window.API.toast("Failed to delete item", "error");
        }
    }
}

/* Adjust Stock Logic */

function openAdjustModal(itemId) {
    const item = allStockItems.find(i => i.id === itemId);
    if (!item) return;
    
    document.getElementById('adj-stock-id').value = item.id;
    document.getElementById('adj-item-name').textContent = item.name;
    document.getElementById('adj-current-qty').textContent = item.quantity;
    document.getElementById('adj-unit').textContent = item.unit;
    
    document.getElementById('adj-amount').value = '';
    
    // Default to consume if we have stock, else add
    const consumeRadio = document.querySelector('input[name="adj-action"][value="consume"]');
    const addRadio = document.querySelector('input[name="adj-action"][value="add"]');
    
    if (item.quantity > 0) consumeRadio.checked = true;
    else addRadio.checked = true;
    
    const modal = document.getElementById('adjust-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        modal.children[0].classList.remove('scale-95');
    }, 10);
}

function closeAdjustModal() {
    const modal = document.getElementById('adjust-modal');
    modal.classList.add('opacity-0');
    modal.children[0].classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }, 200);
}

async function saveAdjustment() {
    const id = document.getElementById('adj-stock-id').value;
    const amount = parseFloat(document.getElementById('adj-amount').value);
    const operation = document.querySelector('input[name="adj-action"]:checked').value;
    
    if (isNaN(amount) || amount <= 0) {
        window.API.toast("Please enter a valid amount greater than 0", "error");
        return;
    }
    
    try {
        await window.API.request('adjust_stock', {
            id: parseInt(id),
            amount: amount,
            operation: operation
        });
        
        window.API.toast(`Stock ${operation === 'add' ? 'restocked' : 'consumed'} successfully`, "success");
        closeAdjustModal();
        loadStockData();
    } catch (e) {
        window.API.toast(e, "error");
    }
}
