/**
 * measurements.js - Data binding for Measurements List
 */

let allMeasurements = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        loadMeasurements();
        
        const searchInput = document.getElementById('meas-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => filterMeasurements(e.target.value));
        }
    }
    init();
});

async function loadMeasurements() {
    try {
        const data = await window.API.request('get_all_measurements');
        allMeasurements = data;
        renderMeasurements(allMeasurements);
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load measurements", "error");
    }
}

function filterMeasurements(query) {
    const q = query.toLowerCase();
    const filtered = allMeasurements.filter(m => 
        (m.customer_name && m.customer_name.toLowerCase().includes(q)) || 
        (m.customer_mobile && String(m.customer_mobile).toLowerCase().includes(q)) ||
        (m.name && m.name.toLowerCase().includes(q)) ||
        (m.template_type && m.template_type.toLowerCase().includes(q)) ||
        (m.id && String(m.id).toLowerCase().includes(q))
    );
    renderMeasurements(filtered);
}

function renderMeasurements(measurements) {
    const tbody = document.getElementById('table-measurements');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (measurements.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-on-surface-variant">No measurements found</td></tr>';
        return;
    }
    
    measurements.forEach(m => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-surface-container last:border-0 hover:bg-surface-container-highest/20 transition-colors cursor-pointer';
        // Assume navigate to view/edit measurement exists
        tr.onclick = () => window.API.request('navigate_to', {page: 'add_measurement', id: m.id});
        
        tr.innerHTML = `
            <td class="p-4">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-surface-container-highest flex items-center justify-center text-primary">
                        <span class="material-symbols-outlined text-[20px]">straighten</span>
                    </div>
                    <div>
                        <p class="font-label-lg text-on-surface">${m.name || 'Profile ' + m.id}</p>
                        <p class="font-label-sm text-on-surface-variant">${m.customer_name || 'No Customer Attached'}</p>
                    </div>
                </div>
            </td>
            <td class="p-4">
                <span class="px-3 py-1 bg-surface-container text-on-surface font-label-sm rounded-lg border border-outline-variant">
                    ${m.template_type}
                </span>
            </td>
            <td class="p-4 text-on-surface-variant">${m.values_count} fields</td>
            <td class="p-4 text-on-surface-variant">${window.API.formatDate(m.updated_at)}</td>
            <td class="p-4 text-right">
                <button onclick="event.stopPropagation(); window.API.request('navigate_to', {page: 'add_measurement', id: ${m.id}});" class="w-8 h-8 rounded-full hover:bg-surface-container-highest text-on-surface-variant flex items-center justify-center transition-colors">
                    <span class="material-symbols-outlined text-[20px]">edit</span>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}
