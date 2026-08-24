/**
 * add_customer.js - Data binding for Add Customer screen
 */

document.addEventListener("DOMContentLoaded", function() {
    const btnSave = document.getElementById('btn-save-customer');
    const btnSaveAddMeas = document.getElementById('btn-save-add-measurements');
    
    if (btnSave) {
        btnSave.addEventListener('click', () => saveCustomer('customers_list'));
    }
    if (btnSaveAddMeas) {
        btnSaveAddMeas.addEventListener('click', () => saveCustomer('new_order'));
    }
    
    // Attach Dictation Mic to large textareas
    setTimeout(() => {
        if (window.API && window.API.attachMic) {
            window.API.attachMic('customerName');
            window.API.attachMic('customerAddress');
            window.API.attachMic('customerNotes');
        }
    }, 100);
});

async function saveCustomer(targetPage) {
    const nameEl = document.getElementById('customerName');
    const mobileEl = document.getElementById('customerMobile');
    const addressEl = document.getElementById('customerAddress');
    const notesEl = document.getElementById('customerNotes');

    if (!nameEl || !mobileEl) return;

    const payload = {
        name: nameEl.value.trim(),
        mobile: mobileEl.value.trim(),
        address: addressEl ? addressEl.value.trim() : "",
        notes: notesEl ? notesEl.value.trim() : ""
    };

    if (!payload.name) {
        window.API.toast("Name is required", "error");
        return;
    }
    const nameRegex = /^[A-Za-z\s]+$/;
    if (!nameRegex.test(payload.name)) {
        window.API.toast("Name should contain only letters and spaces", "error");
        return;
    }

    if (!payload.mobile) {
        window.API.toast("Mobile is required", "error");
        return;
    }
    const mobileRegex = /^\+91 [0-9]{10}$/;
    if (!mobileRegex.test(payload.mobile)) {
        window.API.toast("Mobile number must be exactly 10 digits (e.g. +91 9876543210)", "error");
        return;
    }

    try {
        const response = await window.API.request('create_customer', payload);
        window.API.toast("Customer saved successfully!", "success");

        // Navigate to the target page
        setTimeout(() => {
            if (targetPage === 'new_order' && response.id) {
                // Pass customer_id in the navigate payload so new_order auto-selects them
                window.API.request('navigate_to', { page: 'new_order', customer_id: response.id });
            } else {
                window.API.navigate(targetPage);
            }
        }, 500);
    } catch (e) {
        window.API.toast(e.toString(), "error");
    }
}


