/**
 * stitching_slip_preview.js - Render dynamic stitching slip data before printing
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
            document.getElementById('ss-order-number').textContent = "Error: Order ID Missing";
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
        document.getElementById('ss-due-date').textContent = "Due: " + window.API.formatDate(o.delivery_date);
        
        document.getElementById('ss-customer-name').textContent = o.customer_name || 'Walk-in Customer';
        document.getElementById('ss-customer-mobile').innerHTML = `<span class="material-symbols-outlined text-[18px]" data-icon="phone">phone</span> ${o.customer_mobile || 'No Mobile'}`;
        
        const garmentText = o.items && o.items.length > 0 
            ? o.items.map(i => `${i.clothing_type || 'Custom Item'} (x${i.quantity || 1})`).join(", ")
            : "Custom Item (x1)";
        document.getElementById('ss-garment-type').textContent = garmentText;
        
        document.getElementById('ss-special-instructions').textContent = o.special_instructions || "None";
        
        const now = new Date();
        document.getElementById('ss-generated-date').textContent = `Generated: ${window.API.formatDate(now)} - ${now.toLocaleTimeString()}`;
        
        // Measurements
        const mContainer = document.getElementById('ss-measurements-container');
        mContainer.innerHTML = '';
        
        let hasMeasurements = false;
        
        if (o.items && o.items.length > 0) {
            o.items.forEach(item => {
                if (item.measurements && Object.keys(item.measurements).length > 0) {
                    hasMeasurements = true;
                    const section = document.createElement('section');
                    section.className = "flex flex-col gap-stack_sm mt-4";
                    
                    section.innerHTML = `
                        <h3 class="font-headline-md text-headline-md text-primary flex items-center gap-2 border-b border-outline-variant/50 pb-2">
                            <span class="material-symbols-outlined" data-icon="straighten">straighten</span>
                            ${item.clothing_type || 'Item'} Measurements
                        </h3>
                    `;
                    
                    const grid = document.createElement('div');
                    grid.className = "grid grid-cols-2 md:grid-cols-4 gap-4 mt-2";
                    
                    const values = item.measurements;
                    for (const key of Object.keys(values)) {
                        const mItem = document.createElement('div');
                        mItem.className = "flex flex-col items-center justify-center p-4 bg-surface rounded-lg border border-outline-variant shadow-sm relative overflow-hidden";
                        mItem.innerHTML = `
                            <div class="absolute top-0 left-0 w-full h-1 bg-primary/20"></div>
                            <span class="font-label-lg text-label-lg text-on-surface-variant mb-2 truncate max-w-full" title="${key}">${key.replace('_', ' ')}</span>
                            <span class="font-display text-display text-primary">${values[key]}<span class="text-headline-md text-on-surface-variant ml-1">"</span></span>
                        `;
                        grid.appendChild(mItem);
                    }
                    
                    section.appendChild(grid);
                    mContainer.appendChild(section);
                }
            });
        }
        
        if (!hasMeasurements) {
            mContainer.innerHTML = '<div class="p-4 bg-surface-container-low text-center text-on-surface-variant rounded-lg">No measurement profile attached to this order.</div>';
        }

        if (o.scan_url) {
            document.getElementById('ss-qrcode').innerHTML = '';
            new QRCode(document.getElementById("ss-qrcode"), {
                text: o.scan_url,
                width: 75,
                height: 75,
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

