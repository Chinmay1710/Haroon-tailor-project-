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
        setTimeout(() => {
            if (window.API && window.API.attachMic) {
                window.API.attachMic('notes');
            }
        }, 100);
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
    grid.innerHTML = '';
    
    activeTemplate.fields.forEach(f => {
        const id = f;
        const label = f.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        const div = document.createElement('div');
        div.className = "flex flex-col gap-1";
        div.innerHTML = `
            <label class="font-label-lg text-label-lg text-on-surface" for="${id}">${label}</label>
            <div class="relative">
                <input class="w-full bg-surface-container-low border border-outline-variant rounded-lg px-4 py-3 font-headline-md text-headline-md text-center text-on-background focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none" id="${id}" placeholder="00.0" type="number" step="0.1"/>
                <span class="absolute right-3 top-1/2 -translate-y-1/2 font-label-sm text-label-sm text-on-surface-variant">in</span>
            </div>
        `;
        grid.appendChild(div);
    });
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
    activeTemplate.fields.forEach(f => {
        const el = document.getElementById(f);
        if (el) {
            const key = f.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            values[key] = el.value || "0";
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
        
        setTimeout(() => {
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
        }, 1000);
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to save: " + e.toString(), "error");
    }
}

window.saveMeasurement = saveMeasurement;
