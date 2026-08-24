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
        
        document.getElementById('set-shop-name').value = data.shop_name || '';
        document.getElementById('set-owner-name').value = data.owner_name || '';
        document.getElementById('set-phone').value = data.phone || '';
        document.getElementById('set-address').value = data.address || '';
        document.getElementById('set-currency').value = data.currency_symbol || '₹';
        document.getElementById('set-unit').value = data.measurement_unit || 'inches';
        
        const dictationSelect = document.getElementById('dictationLanguageSelect');
        if (dictationSelect) {
            dictationSelect.value = localStorage.getItem('dictationLanguage') || 'en-IN';
        }
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load settings", "error");
    }
}

async function saveSettings() {
    const payload = {
        shop_name: document.getElementById('set-shop-name').value,
        owner_name: document.getElementById('set-owner-name').value,
        phone: document.getElementById('set-phone').value,
        address: document.getElementById('set-address').value,
        currency_symbol: document.getElementById('set-currency').value,
        measurement_unit: document.getElementById('set-unit').value
    };
    
    const dictationSelect = document.getElementById('dictationLanguageSelect');
    if (dictationSelect) {
        localStorage.setItem('dictationLanguage', dictationSelect.value);
    }
    
    try {
        await window.API.request('update_settings', payload);
        window.API.toast("Settings saved successfully!", "success");
    } catch (e) {
        window.API.toast(e.toString(), "error");
    }
}
