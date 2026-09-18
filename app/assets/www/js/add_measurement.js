/**
 * add_measurement.js - Logic for dynamic measurement schemas
 */

const TEMPLATES = [
 {
 name: 'Shirt',
 icon: 'apparel',
 fields: ['length', 'shoulder', 'chest', 'waist', 'hip', 'sleeve', 'bicep', 'cuff', 'collar', 'front_length', 'back_length']
 },
 {
 name: 'Pant',
 icon: 'styler',
 fields: ['length', 'waist', 'hip', 'inseam', 'thigh', 'knee', 'bottom', 'crotch']
 },
 {
 name: 'Kurta',
 icon: 'dry_cleaning',
 fields: ['length', 'shoulder', 'chest', 'waist', 'hip', 'sleeve', 'collar', 'slit_length']
 },
 {
 name: 'Suit',
 icon: 'checkroom',
 fields: ['length', 'shoulder', 'chest', 'waist', 'hip', 'sleeve', 'bicep', 'cuff', 'collar', 'half_back']
 },
 {
 name: 'Custom',
 icon: 'draw',
 fields: ['measurement_1', 'measurement_2', 'measurement_3', 'measurement_4', 'measurement_5', 'measurement_6']
 }
];

let activeTemplate = TEMPLATES[0];

document.addEventListener("DOMContentLoaded", function() {
 function init() {
 if (!window.pyBridge) {
 setTimeout(init, 100);
 return;
 }
 
 renderTemplateList();
 renderForm();
 
 // Attach Dictation Mic to large textareas
 

 if (window.API && window.API.attachMic) {
 window.API.attachMic('notes');
 }
 
 }
 init();
});

function renderTemplateList() {
 const list = document.getElementById('am-templates-list');
 list.innerHTML = '';
 
 TEMPLATES.forEach(t => {
 const btn = document.createElement('button');
 const isActive = (t.name === activeTemplate.name);
 
 if (isActive) {
 btn.className = "flex items-center gap-3 p-3 w-full rounded-lg bg-surface-container-high/50 border border-primary/20 text-primary font-label-lg text-label-lg text-left transition-colors";
 btn.innerHTML = `
 <span class="material-symbols-outlined text-primary" data-icon="${t.icon}">${t.icon}</span>
 ${t.name}
 <span class="material-symbols-outlined ml-auto text-primary" data-icon="check_circle" data-weight="fill">check_circle</span>
 `;
 } else {
 btn.className = "flex items-center gap-3 p-3 w-full rounded-lg bg-transparent border border-transparent hover:bg-surface-container-low text-on-surface-variant hover:text-on-surface font-body-md text-body-md text-left transition-colors";
 btn.innerHTML = `
 <span class="material-symbols-outlined text-on-surface-variant" data-icon="${t.icon}">${t.icon}</span>
 ${t.name}
 `;
 btn.onclick = () => {
 activeTemplate = t;
 renderTemplateList();
 renderForm();
 };
 }
 
 list.appendChild(btn);
 });
}

function renderForm() {
  document.getElementById('am-form-title').textContent = activeTemplate.name + ' Measurements';
  
  const grid = document.getElementById('am-form-grid');
  
  // Use 6 columns layout
  grid.className = "grid grid-cols-3 md:grid-cols-6 gap-4";
  
  let html = '';
  for (let i = 1; i <= 24; i++) {
    const id = `Box ${i}`;
    html += `
    <div class="flex flex-col gap-1">
      <div class="relative">
        <input class="am-meas-input w-full bg-surface-container-low border border-outline-variant rounded-lg px-4 py-3 font-headline-md text-headline-md text-center text-on-background focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none" id="${id}" data-idx="${i}" placeholder="" type="text" data-field="${id}"/>
      </div>
    </div>
    `;
  }
  grid.innerHTML = html;

  // Add arrow key navigation
  if (!grid.dataset.navAttached) {
    grid.addEventListener('keydown', function(e) {
      if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) return;
      
      const currentInput = e.target;
      if (!currentInput.classList.contains('am-meas-input')) return;
      
      const currentIdx = parseInt(currentInput.dataset.idx);
      const cols = 6;
      const rows = 4;
      let nextIdx = null;

      if (e.key === 'ArrowRight') {
        if (currentInput.selectionStart === currentInput.value.length) {
          if (currentIdx % cols !== 0) nextIdx = currentIdx + 1;
        }
      } else if (e.key === 'ArrowLeft') {
        if (currentInput.selectionStart === 0) {
          if (currentIdx % cols !== 1) nextIdx = currentIdx - 1;
        }
      } else if (e.key === 'ArrowUp') {
        if (currentIdx > cols) nextIdx = currentIdx - cols;
        e.preventDefault();
      } else if (e.key === 'ArrowDown') {
        if (currentIdx <= (rows - 1) * cols) nextIdx = currentIdx + cols;
        e.preventDefault();
      }

      if (nextIdx) {
        const nextInput = document.querySelector(`.am-meas-input[data-idx="${nextIdx}"]`);
        if (nextInput) nextInput.focus();
      }
    });
    grid.dataset.navAttached = "true";
  }
}

async function saveMeasurement(targetPage) {
 let customerId = null;
 const navParamsStr = sessionStorage.getItem('nav_params');
 if (navParamsStr) {
 try {
 const params = JSON.parse(navParamsStr);
 if (params.customer_id) customerId = parseInt(params.customer_id);
 if (params.id) customerId = parseInt(params.id);
 } catch (e) {}
 }
 if (!customerId) {
 const custIdStr = sessionStorage.getItem('current_customer_id') || sessionStorage.getItem('measurement_customer_id');
 customerId = custIdStr ? parseInt(custIdStr) : null;
 }
 
 if (!customerId) {
 window.API.toast("No customer selected. Please select a customer first.", "error");
 return;
 }
 
  const values = {};
  const inputs = document.querySelectorAll('.am-meas-input');
  inputs.forEach(input => {
    if (input.value) {
      values[input.dataset.field] = input.value;
    }
  });
 
 const notes = document.getElementById('notes') ? document.getElementById('notes').value : "";
 
 const payload = {
 customer_id: customerId,
 template_type: activeTemplate.name,
 name: activeTemplate.name + " Profile",
 values: values,
 notes: notes
 };
 
 try {
 await window.API.request('create_measurement', payload);
 window.API.toast("Measurement saved successfully!", "success");
 
 

 if (targetPage === 'add_measurement') {
 // Just clear the inputs to add another
 activeTemplate.fields.forEach(f => {
 const el = document.getElementById(f);
 if (el) el.value = '';
 });
 if (document.getElementById('notes')) document.getElementById('notes').value = '';
 } else {
 // If heading to new_order, ensure the customer_id is stored so it's pre-selected
 if (targetPage === 'new_order') {
 sessionStorage.setItem('nav_params', JSON.stringify({ customer_id: customerId }));
 }
 window.API.navigate(targetPage);
 }
 
 } catch (e) {
 console.error(e);
 window.API.toast("Failed to save: " + e.toString(), "error");
 }
}

window.saveMeasurement = saveMeasurement;
