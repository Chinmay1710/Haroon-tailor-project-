/**
 * reports.js - Data binding for Reports page
 */

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        
        const filterSelect = document.getElementById('report-filter');
        if (filterSelect) {
            // Default to 'This Month' which matches the UI default typically
            filterSelect.value = "This Month";
            filterSelect.addEventListener('change', (e) => loadReport(e.target.value));
        }
        loadReport("This Month");
    }
    init();
});

async function loadReport(period) {
    try {
        const data = await window.API.request('get_report_data', {period: period});
        
        document.getElementById('rep-total-sales').innerText = window.API.formatCurrency(data.total_sales);
        document.getElementById('rep-completed-orders').innerText = data.completed_orders;
        document.getElementById('rep-pending-payments').innerText = window.API.formatCurrency(data.pending_payments);
        document.getElementById('rep-total-expenses').innerText = window.API.formatCurrency(data.total_expenses);
        
        const profitEl = document.getElementById('rep-estimated-profit');
        if(profitEl) {
            profitEl.innerText = window.API.formatCurrency(data.estimated_profit);
            if (data.estimated_profit < 0) {
                profitEl.classList.remove('text-primary');
                profitEl.classList.add('text-error');
            } else {
                profitEl.classList.remove('text-error');
                profitEl.classList.add('text-primary');
            }
        }
        
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load report", "error");
    }
}
