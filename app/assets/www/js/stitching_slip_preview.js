/**
 * stitching_slip_preview.js - Render dynamic stitching slip data before printing (58mm POS format)
 */

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        
        let navParamsStr = sessionStorage.getItem("nav_params");
        let navParams = navParamsStr ? JSON.parse(navParamsStr) : null;
        
        if (!navParams || !navParams.order_id) {
            window.API.toast("No order ID provided.", "error");
            document.getElementById('ss-order-number').textContent = "Error";
            return;
        }
        
        loadSlipData(navParams.order_id);
    }
    init();
});

async function loadSlipData(orderId) {
    try {
        const o = await window.API.request('get_order_details', {id: orderId});
        
        document.getElementById('ss-order-number').textContent = o.order_number;
        document.getElementById('ss-due-date').textContent = window.API.formatDate(o.delivery_date);
        
        document.getElementById('ss-customer-name').textContent = o.customer_name || 'Walk-in';
        
        const garmentText = o.items && o.items.length > 0 
            ? o.items.map(i => `${i.clothing_type || 'Custom Item'} (x${i.quantity || 1})`).join(", ")
            : "Custom Item (x1)";
        document.getElementById('ss-garment-type').textContent = garmentText;
        
        const now = new Date();
        document.getElementById('ss-generated-date').textContent = `Generated: ${window.API.formatDate(now)} - ${now.toLocaleTimeString()}`;
        
        // Measurements
        const mContainer = document.getElementById('ss-measurements-container');
        mContainer.innerHTML = '';
        
        let hasMeasurements = false;
        
        if (o.items && o.items.length > 0) {
            o.items.forEach((item, index) => {
                if (item.measurements && Object.keys(item.measurements).length > 0) {
                    hasMeasurements = true;
                    const section = document.createElement('div');
                    section.style.marginBottom = '10px';
                    
                    section.innerHTML = `
                        <div style="font-weight: bold; margin-bottom: 2px; text-decoration: underline;">
                            ${item.clothing_type || 'Item'}
                        </div>
                    `;
                    
                    const values = item.measurements;
                    // Format compactly: Name: Value" 
                    for (const key of Object.keys(values)) {
                        const mItem = document.createElement('div');
                        mItem.style.display = 'flex';
                        mItem.style.justifyContent = 'space-between';
                        mItem.innerHTML = `
                            <span>${key.replace('_', ' ')}:</span>
                            <span style="font-weight:bold;">${values[key]}"</span>
                        `;
                        section.appendChild(mItem);
                    }
                    
                    if (item.notes && item.notes.trim() !== '') {
                        const notesItem = document.createElement('div');
                        notesItem.style.marginTop = '6px';
                        notesItem.style.paddingTop = '4px';
                        notesItem.style.borderTop = '1px dashed #ccc';
                        notesItem.style.fontSize = '0.9em';
                        notesItem.innerHTML = `<strong>Note:</strong> ${item.notes}`;
                        section.appendChild(notesItem);
                    }
                    
                    mContainer.appendChild(section);
                }
            });
        }
        
        if (!hasMeasurements) {
            mContainer.innerHTML = '<div style="text-align:center; font-style:italic;">No measurements</div>';
        }

        if (o.id) {
            document.getElementById('ss-qrcode').innerHTML = '';
            new QRCode(document.getElementById("ss-qrcode"), {
                text: "ORDER:" + o.id,
                width: 60,
                height: 60,
                colorDark : "#000000",
                colorLight : "#ffffff",
                correctLevel : QRCode.CorrectLevel.L
            });
        }
        
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load stitching slip: " + e, "error");
    }
}

window.savePdf = async function() {
    let navParamsStr = sessionStorage.getItem("nav_params");
    let navParams = navParamsStr ? JSON.parse(navParamsStr) : null;
    if (!navParams || !navParams.order_id) return;
    
    try {
        const res = await window.API.request('save_pdf', {type: 'slip', order_id: navParams.order_id});
        window.API.toast(res?.message || "Saved successfully!", "success");
    } catch (e) {
        if (e !== "Save cancelled") {
            console.error(e);
            window.API.toast(e, "error");
        }
    }
};
