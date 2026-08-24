/**
 * settings.js - Data binding for Settings page
 */

document.addEventListener("DOMContentLoaded", function() {
    const btnSave = document.getElementById('btn-save-settings');
    if (btnSave) {
        btnSave.addEventListener('click', saveSettings);
    }
    
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        loadSettings();
    }
    init();
});

async function loadSettings() {
    try {
        const data = await window.API.request('get_settings');
        
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.value = val || '';
        };
        
        setVal('set-shop-name', data.shop_name);
        setVal('set-owner-name', data.owner_name);
        setVal('set-phone', data.phone);
        setVal('set-address', data.address);
        setVal('set-currency', data.currency_symbol);
        setVal('set-unit', data.measurement_unit);
        
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load settings", "error");
    }
}

async function saveSettings() {
    const getVal = (id) => {
        const el = document.getElementById(id);
        return el ? el.value : '';
    };
    
    const payload = {
        shop_name: getVal('set-shop-name'),
        owner_name: getVal('set-owner-name'),
        phone: getVal('set-phone'),
        address: getVal('set-address'),
        currency: getVal('set-currency'),
        measurement_unit: getVal('set-unit')
    };
    
    try {
        await window.API.request('update_settings', payload);
        window.API.toast("Settings saved successfully!", "success");
        
        // Update the shop name in the sidebar globally
        document.querySelectorAll('.global-shop-name').forEach(el => {
            el.textContent = payload.shop_name || 'My Tailor Shop';
        });
    } catch (e) {
        window.API.toast(e.toString(), "error");
    }
}
