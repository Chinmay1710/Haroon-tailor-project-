/**
 * new_order.js - Data binding and state management for New Order (Single view, multiple items, inline measurements)
 */

const MEASUREMENT_TEMPLATES = {
    "Shirt": ["Length", "Shoulder", "Chest", "Waist", "Hip", "Sleeve Length", "Bicep", "Cuff", "Collar", "Front Length", "Back Length"],
    "Pant": ["Length", "Waist", "Hip", "Thigh", "Knee", "Bottom", "Rise"],
    "Kurta": ["Length", "Shoulder", "Chest", "Waist", "Hip", "Sleeve Length", "Collar", "Side Slit"],
    "Blouse": ["Length", "Shoulder", "Bust", "Waist", "Sleeve", "Armhole", "Neck Front", "Neck Back"],
    "Suit": ["Jacket Length", "Shoulder", "Chest", "Waist", "Sleeve", "Pant Length", "Pant Waist", "Pant Hip"],
    "Custom": ["Measurement 1", "Measurement 2", "Measurement 3"]
};

let wizardState = {
    customerId: null,
    customerName: "",
    customerMobile: "",
    items: [], // { id, clothing_type, quantity, price, measurements: {}, save_profile: bool }
    deliveryDate: "",
    notes: "",
    advance: 0,
    paymentMethod: "CASH"
};

let availableCustomers = [];
let availableProfiles = []; 
let editItemId = null;
let currentImageBase64 = null;

// For tracking the modal's edit state
let itemIdCounter = 1;

let editingOrderModeId = null;

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        
        let initialCustomerId = null;
        
        // Check for edit mode or pre-selected customer
        const navParamsStr = sessionStorage.getItem('nav_params');
        if (navParamsStr) {
            try {
                const params = JSON.parse(navParamsStr);
                if (params.action === 'edit' && params.order_id) {
                    editingOrderModeId = parseInt(params.order_id);
                    document.getElementById('page-title').textContent = "Edit Order";
                    document.getElementById('btn-save-order').innerHTML = '<span class="material-symbols-outlined">save</span> Update Order';
                } else if (params.customer_id) {
                    initialCustomerId = parseInt(params.customer_id);
                }
            } catch(e) {}
            sessionStorage.removeItem('nav_params');
        }

        // Set default date to next week
        const today = new Date();
        const nextWeek = new Date(today);
        nextWeek.setDate(today.getDate() + 7);
        document.getElementById('order-date').value = nextWeek.toISOString().split('T')[0];
        
        loadCustomers(initialCustomerId);
        
        document.getElementById('order-advance').addEventListener('input', (e) => {
            wizardState.advance = parseFloat(e.target.value) || 0;
            updateTotals();
        });
    }
    init();
});

async function loadCustomers(initialCustomerId) {
    try {
        availableCustomers = await window.API.request('get_customers');
        
        if (editingOrderModeId) {
            // Load existing order details
            try {
                const data = await window.API.request('get_order_details', {id: editingOrderModeId});
                if (data.customer_id) {
                    const cust = availableCustomers.find(c => c.id === data.customer_id);
                    if (cust) selectCustomer(cust.id, cust.name, cust.mobile);
                }
                
                // Populate wizard state
                if (data.delivery_date) {
                    document.getElementById('order-date').value = data.delivery_date.split('T')[0];
                }
                document.getElementById('order-notes').value = data.special_instructions || "";
                document.getElementById('order-advance').value = data.advance_amount || 0;
                wizardState.advance = data.advance_amount || 0;
                
                // Disable advance payment field if already paid
                if (data.advance_amount > 0) {
                    document.getElementById('order-advance').disabled = true;
                    document.getElementById('order-advance').title = "Advance payment already recorded";
                }
                
                wizardState.items = data.items.map(i => ({
                    id: itemIdCounter++,
                    clothing_type: i.clothing_type,
                    quantity: i.quantity,
                    price: i.price,
                    measurements: i.measurements || {},
                    notes: i.notes || "",
                    save_profile: false
                }));
                
                renderOrderItems();
                updateTotals();
            } catch(e) {
                window.API.toast("Failed to load order for editing", "error");
            }
        } else if (initialCustomerId) {
            wizardState.customerId = initialCustomerId;
            const cust = availableCustomers.find(c => c.id === initialCustomerId);
            if (cust) {
                selectCustomer(cust.id, cust.name, cust.mobile);
            } else {
                renderCustomerSelect();
            }
        } else {
            renderCustomerSelect();
        }
    } catch (e) {
        window.API.toast("Failed to load customers", "error");
    }
}

function renderCustomerSelect() {
    const selectView = document.getElementById('customer-select-view');
    const selectedView = document.getElementById('customer-selected-view');
    const changeBtn = document.getElementById('btn-change-customer');
    const addItemBtn = document.getElementById('btn-add-item');
    const addItemHint = document.getElementById('add-item-hint');
    
    if (selectView) selectView.classList.remove('hidden');
    if (selectedView) selectedView.classList.add('hidden');
    if (changeBtn) changeBtn.classList.add('hidden');
    if (addItemBtn) addItemBtn.classList.add('opacity-50', 'pointer-events-none');
    if (addItemHint) addItemHint.classList.remove('hidden');

    const listDiv = document.getElementById('cust-list');
    let html = '';
    
    availableCustomers.forEach(c => {
        const name = c.name || 'Unknown';
        const mobile = c.mobile || '';
        const initials = name.substring(0, 2).toUpperCase() || 'CU';
        
        // Use standard html escaping for safe insertion
        const safeName = name.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        const safeMobile = mobile.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        
        html += `
            <div data-id="${c.id}" data-name="${safeName}" data-mobile="${safeMobile}" class="customer-card bg-surface-container-lowest rounded-lg p-3 border border-outline-variant hover:border-primary flex items-center cursor-pointer transition-colors shadow-sm">
                <div class="w-10 h-10 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-label-md mr-3 pointer-events-none">
                    ${initials}
                </div>
                <div class="flex-1 overflow-hidden pointer-events-none">
                    <h3 class="font-label-md text-primary truncate">${safeName}</h3>
                    <p class="font-body-sm text-on-surface-variant truncate">${safeMobile}</p>
                </div>
            </div>
        `;
    });
    
    listDiv.innerHTML = html;
    
    // Use event delegation for clicks
    listDiv.onclick = function(e) {
        const card = e.target.closest('.customer-card');
        if (card) {
            const id = parseInt(card.dataset.id);
            const name = card.dataset.name;
            const mobile = card.dataset.mobile;
            selectCustomer(id, name, mobile);
        }
    };
    
    document.getElementById('search-cust').addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        const cards = listDiv.querySelectorAll('.customer-card');
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(q) ? 'flex' : 'none';
        });
    });
}

async function selectCustomer(id, name, mobile) {
    wizardState.customerId = id;
    wizardState.customerName = name;
    wizardState.customerMobile = mobile;
    
    const selectView = document.getElementById('customer-select-view');
    const selectedView = document.getElementById('customer-selected-view');
    const changeBtn = document.getElementById('btn-change-customer');
    const addItemBtn = document.getElementById('btn-add-item');
    const addItemHint = document.getElementById('add-item-hint');
    const nameEl = document.getElementById('customer-name');
    const mobileEl = document.getElementById('customer-mobile');
    const initialsEl = document.getElementById('customer-initials');
    
    if (selectView) selectView.classList.add('hidden');
    if (selectedView) {
        selectedView.classList.remove('hidden');
        selectedView.classList.add('flex');
    }
    if (changeBtn) changeBtn.classList.remove('hidden');
    if (addItemBtn) addItemBtn.classList.remove('opacity-50', 'pointer-events-none');
    if (addItemHint) addItemHint.classList.add('hidden');
    if (nameEl) nameEl.textContent = name;
    if (mobileEl) mobileEl.textContent = mobile;
    if (initialsEl) initialsEl.textContent = name.substring(0, 2).toUpperCase();

    // Load their profiles
    try {
        availableProfiles = await window.API.request('get_measurements_for_customer', {customer_id: id});
    } catch(e) {
        availableProfiles = [];
    }
}

window.openCustomerSelect = function() {
    wizardState.customerId = null;
    wizardState.items = []; // Clear items since measurements might be specific
    renderOrderItems();
    renderCustomerSelect();
}

// --- ITEM MODAL ---

window.openAddItemModal = function(itemId = null) {
    if (!wizardState.customerId) return;
    
    currentImageBase64 = null;
    clearPhotoCapture();
    
    editItemId = itemId;
    const modal = document.getElementById('add-item-modal');
    
    // Reset modal
    document.getElementById('modal-save-profile').checked = true;
    
    if (itemId) {
        document.getElementById('modal-title').textContent = "Edit Item";
        document.getElementById('btn-save-modal-item').textContent = "Update Item";
        
        const item = wizardState.items.find(i => i.id === itemId);
        document.getElementById('modal-item-type').value = item.clothing_type;
        document.getElementById('modal-item-qty').value = item.quantity;
        document.getElementById('modal-item-price').value = item.price;
        
        if (item.image_base64) {
            currentImageBase64 = item.image_base64;
            document.getElementById('modal-photo-preview').src = currentImageBase64;
            document.getElementById('modal-photo-preview-container').classList.remove('hidden');
        }
        
        populateSavedProfilesDropdown(item.clothing_type);
        renderMeasurementFields(item.clothing_type, item.measurements);
    } else {
        document.getElementById('modal-title').textContent = "Add New Item";
        document.getElementById('btn-save-modal-item').textContent = "Add Item";
        
        document.getElementById('modal-item-qty').value = 1;
        document.getElementById('modal-item-price').value = "";
        
        const type = document.getElementById('modal-item-type').value;
        populateSavedProfilesDropdown(type);
        renderMeasurementFields(type, {});
    }
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.remove('opacity-0');
    }
    var content = document.getElementById('add-item-modal-content');
    if (content) content.classList.remove('scale-95');
}

window.closeAddItemModal = function() {
    const modal = document.getElementById('add-item-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.add('opacity-0');
    }
    var content = document.getElementById('add-item-modal-content');
    if (content) content.classList.add('scale-95');
}

window.handleClothingTypeChange = function() {
    const type = document.getElementById('modal-item-type').value;
    // Keep the current profile if it matches the new type, otherwise reset
    const profileId = document.getElementById('modal-saved-profile').value;
    if (profileId) {
        const profile = availableProfiles.find(p => p.id == profileId);
        if (profile && profile.template_type !== type) {
            document.getElementById('modal-saved-profile').value = "";
        }
    }
    renderMeasurementFields(type, {});
}

window.handleSavedProfileChange = function() {
    const profileId = document.getElementById('modal-saved-profile').value;
    
    if (!profileId) {
        const type = document.getElementById('modal-item-type').value;
        renderMeasurementFields(type, {});
        return;
    }
    
    const profile = availableProfiles.find(p => p.id == profileId);
    if (profile) {
        // Auto-switch clothing type
        document.getElementById('modal-item-type').value = profile.template_type;
        renderMeasurementFields(profile.template_type, profile.values);
    }
}

function populateSavedProfilesDropdown(type) {
    const select = document.getElementById('modal-saved-profile');
    let html = `<option value="">-- Start Fresh --</option>`;
    
    // Show all profiles, but indicate their type
    availableProfiles.forEach(p => {
        const name = p.name || `${p.template_type} Profile`;
        html += `<option value="${p.id}">${name} (${p.template_type})</option>`;
    });
    
    select.innerHTML = html;
    
    // Select a profile if it matches the current type and there's only one? No, just leave as Start Fresh.
}

function renderMeasurementFields(type, values) {
    const container = document.getElementById('modal-measurements-grid');
    const fields = MEASUREMENT_TEMPLATES[type] || MEASUREMENT_TEMPLATES["Custom"];
    
    let html = '';
    fields.forEach((field, i) => {
        // Convert field to a safe id string
        const safeId = "meas_" + field.replace(/\\s+/g, '_').toLowerCase();
        const val = values[field] || "";
        
        html += `
            <div>
                <label class="block font-label-sm text-on-surface-variant mb-1 truncate" title="${field}">${field}</label>
                <div class="relative">
                    <input type="number" step="0.25" id="${safeId}" data-field="${field}" value="${val}" class="meas-input w-full p-2.5 bg-surface-container-lowest border border-outline-variant rounded focus:border-primary outline-none font-body-lg">
                    <span class="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant font-label-sm opacity-50">"</span>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

window.saveModalItem = function() {
    const type = document.getElementById('modal-item-type').value;
    const qty = parseInt(document.getElementById('modal-item-qty').value) || 1;
    const price = parseFloat(document.getElementById('modal-item-price').value) || 0;
    const saveProfile = document.getElementById('modal-save-profile').checked;
    
    if (price <= 0) {
        window.API.toast("Please enter a valid price", "error");
        return;
    }
    
    const measurements = {};
    const inputs = document.querySelectorAll('.meas-input');
    inputs.forEach(input => {
        if (input.value) {
            measurements[input.dataset.field] = input.value;
        }
    });
    
    if (Object.keys(measurements).length === 0) {
        window.API.toast("Please enter at least one measurement", "error");
        return;
    }
    
    if (editItemId) {
        // Update existing
        const idx = wizardState.items.findIndex(i => i.id === editItemId);
        if (idx !== -1) {
            wizardState.items[idx] = {
                id: editItemId,
                clothing_type: type,
                quantity: qty,
                price: price,
                measurements: measurements,
                save_profile: saveProfile,
                image_base64: currentImageBase64
            };
        }
    } else {
        // Add new
        wizardState.items.push({
            id: itemIdCounter++,
            clothing_type: type,
            quantity: qty,
            price: price,
            measurements: measurements,
            save_profile: saveProfile,
            image_base64: currentImageBase64
        });
    }
    
    closeAddItemModal();
    renderOrderItems();
    updateTotals();
}

window.handleFileUpload = function(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        currentImageBase64 = e.target.result;
        document.getElementById('modal-photo-preview').src = currentImageBase64;
        document.getElementById('modal-photo-preview-container').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
};

let currentCameraStream = null;

window.startCamera = async function() {
    try {
        currentCameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        const video = document.getElementById('live-camera-feed');
        video.srcObject = currentCameraStream;
        document.getElementById('live-camera-container').classList.remove('hidden');
        document.getElementById('modal-photo-preview-container').classList.add('hidden');
        document.getElementById('btn-start-camera').classList.add('hidden');
    } catch (err) {
        console.error("Error accessing camera: ", err);
        window.API.toast("Could not access camera. Please check permissions.", "error");
    }
};

window.stopCamera = function() {
    if (currentCameraStream) {
        currentCameraStream.getTracks().forEach(track => track.stop());
        currentCameraStream = null;
    }
    const video = document.getElementById('live-camera-feed');
    video.srcObject = null;
    document.getElementById('live-camera-container').classList.add('hidden');
    document.getElementById('btn-start-camera').classList.remove('hidden');
};

window.capturePhoto = function() {
    const video = document.getElementById('live-camera-feed');
    const canvas = document.getElementById('live-camera-canvas');
    if (!currentCameraStream || !video.videoWidth) return;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to base64 jpeg
    currentImageBase64 = canvas.toDataURL('image/jpeg', 0.8);
    
    // Stop camera and show preview
    stopCamera();
    document.getElementById('modal-photo-preview').src = currentImageBase64;
    document.getElementById('modal-photo-preview-container').classList.remove('hidden');
};

window.clearPhotoCapture = function() {
    currentImageBase64 = null;
    document.getElementById('modal-item-photo').value = '';
    const container = document.getElementById('modal-photo-preview-container');
    if(container) {
        container.classList.add('hidden');
        document.getElementById('modal-photo-preview').src = '';
    }
    stopCamera();
};

// --- ITEMS LIST ---

function renderOrderItems() {
    const container = document.getElementById('order-items-container');
    const msg = document.getElementById('empty-items-msg');
    
    if (wizardState.items.length === 0) {
        if (container) {
            container.innerHTML = '';
            if (msg) container.appendChild(msg);
        }
        if (msg) msg.classList.remove('hidden');
        return;
    }
    
    if (msg) msg.classList.add('hidden');
    let html = '';
    
    wizardState.items.forEach(item => {
        const itemTotal = item.quantity * item.price;
        
        let measHtml = '';
        Object.entries(item.measurements).slice(0, 6).forEach(([k, v]) => {
            measHtml += `<span class="bg-surface-container px-2 py-0.5 rounded text-xs text-on-surface-variant border border-outline-variant/30">${k} ${v}"</span>`;
        });
        if (Object.keys(item.measurements).length > 6) {
            measHtml += `<span class="px-2 py-0.5 text-xs text-on-surface-variant">...</span>`;
        }
        
        let photoHtml = '';
        if (item.image_base64 || item.image_path) {
            const imgSrc = item.image_base64 || item.image_path;
            photoHtml = `<div class="w-12 h-12 rounded overflow-hidden flex-shrink-0 border border-outline"><img src="${imgSrc}" class="w-full h-full object-cover"></div>`;
        }
        
        html += `
            <div class="bg-surface-container-lowest border border-outline-variant rounded-lg p-4 flex flex-col md:flex-row justify-between gap-4">
                <div class="flex-1 flex gap-4">
                    ${photoHtml}
                    <div>
                        <div class="flex items-baseline gap-3 mb-2">
                            <h3 class="font-title-md text-primary">${item.clothing_type}</h3>
                            <span class="text-body-sm text-on-surface-variant">Qty: ${item.quantity} × ${window.API.formatCurrency(item.price)}</span>
                            ${item.save_profile ? '<span class="bg-primary/10 text-primary text-[10px] px-2 py-0.5 rounded-full font-label-sm ml-2 border border-primary/20">Will Save Profile</span>' : ''}
                        </div>
                        <div class="flex flex-wrap gap-1 mt-2">
                            ${measHtml}
                        </div>
                    </div>
                </div>
                
                <div class="flex items-center justify-between md:flex-col md:items-end gap-2 md:border-l md:border-outline-variant md:pl-4">
                    <div class="font-title-lg text-on-surface">${window.API.formatCurrency(itemTotal)}</div>
                    <div class="flex gap-1">
                        <button onclick="openAddItemModal(${item.id})" class="p-2 text-on-surface-variant hover:text-primary hover:bg-primary/10 rounded transition-colors material-symbols-outlined text-[20px]" title="Edit">edit</button>
                        <button onclick="duplicateItem(${item.id})" class="p-2 text-on-surface-variant hover:text-primary hover:bg-primary/10 rounded transition-colors material-symbols-outlined text-[20px]" title="Duplicate">content_copy</button>
                        <button onclick="removeItem(${item.id})" class="p-2 text-error hover:bg-error/10 rounded transition-colors material-symbols-outlined text-[20px]" title="Remove">delete</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

window.removeItem = function(id) {
    wizardState.items = wizardState.items.filter(i => i.id !== id);
    renderOrderItems();
    updateTotals();
}

window.duplicateItem = function(id) {
    const item = wizardState.items.find(i => i.id === id);
    if (item) {
        wizardState.items.push({
            ...item,
            id: itemIdCounter++,
            save_profile: false // Don't duplicate the save profile flag
        });
        renderOrderItems();
        updateTotals();
    }
}

function updateTotals() {
    const total = wizardState.items.reduce((sum, item) => sum + (item.quantity * item.price), 0);
    const rem = Math.max(0, total - wizardState.advance);
    
    document.getElementById('order-total').textContent = window.API.formatCurrency(total);
    document.getElementById('order-remaining').textContent = window.API.formatCurrency(rem);
    
    const advanceInput = document.getElementById('order-advance');
    advanceInput.max = total;
    if (wizardState.advance > total) {
        wizardState.advance = total;
        advanceInput.value = total;
    }
}

window.saveOrder = async function() {
    if (!wizardState.customerId) {
        window.API.toast("Please select a customer first", "error");
        return;
    }
    
    if (wizardState.items.length === 0) {
        window.API.toast("Please add at least one item to the order", "error");
        return;
    }
    
    const date = document.getElementById('order-date').value;
    if (!date) {
        window.API.toast("Please select a delivery date", "error");
        return;
    }
    
    const notes = document.getElementById('order-notes').value;
    const method = document.getElementById('order-payment-method').value;
    
    const payloadItems = wizardState.items.map(i => ({
        clothing_type: i.clothing_type,
        quantity: i.quantity,
        price: i.price,
        measurements: i.measurements,
        save_profile: i.save_profile,
        image_base64: i.image_base64 || null
    }));
    
    const payload = {
        customerId: wizardState.customerId,
        items: payloadItems,
        deliveryDate: date,
        notes: notes,
        advance: wizardState.advance,
        paymentMethod: method
    };
    
    try {
        if (editingOrderModeId) {
            payload.orderId = editingOrderModeId;
            const response = await window.API.request('update_order', payload);
            window.API.toast(`Order ${response.order_number} updated successfully!`, "success");
            setTimeout(() => {
                window.API.request('navigate_to', {page: 'order_details', id: response.id});
            }, 1000);
        } else {
            const response = await window.API.request('create_order', payload);
            window.API.toast(`Order ${response.order_number} created successfully!`, "success");
            setTimeout(() => {
                window.API.request('navigate_to', {page: 'order_details', id: response.id});
            }, 1000);
        }
    } catch (e) {
        window.API.toast(e.toString(), "error");
    }
}
