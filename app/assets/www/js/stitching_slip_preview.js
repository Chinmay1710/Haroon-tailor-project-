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
  ${item.clothing_type || 'Item'} - ${o.order_number || ''}
  </div>
  `;
 
  const values = item.measurements;
  
  const gridContainer = document.createElement('div');
  gridContainer.style.display = 'grid';
  gridContainer.style.gridTemplateColumns = 'repeat(4, 1fr)';
  gridContainer.style.gap = '0px'; 
  gridContainer.style.marginTop = '8px';
  
  const new_cols = 4;
  const new_rows = 6;
  
  for (let r = 0; r < new_rows; r++) {
    for (let c = 0; c < new_cols; c++) {
        const sideways_row = 3 - c;
        const sideways_col = r;
        const box_number = sideways_row * 6 + sideways_col + 1;
        
        const key = `Box ${box_number}`;
        const val = values[key] || '';
        const mItem = document.createElement('div');
        
        mItem.style.border = '1px solid #94a3b8'; // Slate 400
        mItem.style.padding = '8px 4px';
        mItem.style.textAlign = 'center';
        mItem.style.backgroundColor = '#ffffff';
        mItem.style.minHeight = '48px'; 
        mItem.style.display = 'flex';
        mItem.style.alignItems = 'center';
        mItem.style.justifyContent = 'center';
        
        if (String(val).trim() !== '') {
            mItem.innerHTML = `<div style="font-weight: normal; font-size: 1.4em; color: #000000; writing-mode: vertical-rl; text-orientation: mixed;">${val}</div>`;
        }
        gridContainer.appendChild(mItem);
    }
  }
  section.appendChild(gridContainer);
 
 if (item.notes && item.notes.trim() !== '') {
 const notesItem = document.createElement('div');
 notesItem.style.marginTop = '6px';
 notesItem.style.paddingTop = '4px';
 notesItem.style.borderTop = '1px dashed #ccc';
 notesItem.style.fontSize = '0.9em';
 notesItem.innerHTML = `<strong>Item Note:</strong> ${item.notes}`;
 section.appendChild(notesItem);
 }
 
 mContainer.appendChild(section);
 }
 });
 }
 
 if (!hasMeasurements) {
 mContainer.innerHTML = '<div style="text-align:center; font-style:italic;">No measurements</div>';
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

window.printSlip = async function() {
 let navParamsStr = sessionStorage.getItem("nav_params");
 let navParams = navParamsStr ? JSON.parse(navParamsStr) : null;
 if (!navParams || !navParams.order_id) {
 window.API.toast("Unable to find order ID for printing.", "error");
 return;
 }
 
 try {
 await window.API.request('print_pos_document', {type: 'stitching_slip', order_id: navParams.order_id});
 } catch (e) {
 console.error(e);
 window.API.toast(e, "error");
 }
};
