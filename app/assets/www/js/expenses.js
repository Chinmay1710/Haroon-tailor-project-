/**
 * expenses.js - Data binding for Expenses List
 */

let allExpenses = [];

document.addEventListener("DOMContentLoaded", function() {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        loadExpenses();
        
        const searchInput = document.getElementById('expense-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => filterExpenses(e.target.value));
        }
    }
    init();
});

async function loadExpenses() {
    try {
        const data = await window.API.request('get_expenses_dashboard');
        
        document.getElementById('exp-today').innerText = window.API.formatCurrency(data.stats.today);
        document.getElementById('exp-this-week').innerText = window.API.formatCurrency(data.stats.week);
        document.getElementById('exp-this-month').innerText = window.API.formatCurrency(data.stats.month);
        
        allExpenses = data.expenses;
        renderExpenses(allExpenses);
    } catch (e) {
        console.error(e);
        window.API.toast("Failed to load expenses", "error");
    }
}

function filterExpenses(query) {
    const q = query.toLowerCase();
    const filtered = allExpenses.filter(e => 
        (e.name && e.name.toLowerCase().includes(q)) || 
        (e.category && e.category.toLowerCase().includes(q))
    );
    renderExpenses(filtered);
}

function renderExpenses(expenses) {
    const container = document.getElementById('table-expenses');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (expenses.length === 0) {
        container.innerHTML = '<div class="p-4 text-center text-on-surface-variant w-full">No expenses found</div>';
        return;
    }
    
    expenses.forEach(exp => {
        const div = document.createElement('div');
        div.className = 'bg-surface-container-lowest rounded-xl p-6 shadow-[0px_4px_20px_rgba(0,0,0,0.05)] border border-transparent hover:border-outline-variant/30 transition-colors grid grid-cols-12 gap-4 items-center';
        
        const catIcons = {
            'Material': { icon: 'category', bg: 'bg-[#dce9ff]/40', text: 'text-[#545f73]', border: 'border-[#dce9ff]' },
            'Utility': { icon: 'bolt', bg: 'bg-[#ffdcbd]/40', text: 'text-[#623f18]', border: 'border-[#ffdcbd]' },
            'Maintenance': { icon: 'build', bg: 'bg-[#e0e0db]/40', text: 'text-[#454744]', border: 'border-[#e0e0db]' },
            'Rent': { icon: 'storefront', bg: 'bg-[#d8e3fb]/40', text: 'text-[#111c2d]', border: 'border-[#d8e3fb]' },
            'Salary': { icon: 'payments', bg: 'bg-[#dce9ff]/40', text: 'text-[#545f73]', border: 'border-[#dce9ff]' }
        };
        const catStyle = catIcons[exp.category] || { icon: 'receipt_long', bg: 'bg-surface-container/40', text: 'text-on-surface-variant', border: 'border-outline-variant' };
        
        const dateFormatted = window.API.formatDate ? window.API.formatDate(exp.date) : exp.date;
        const amountFormatted = window.API.formatCurrency ? window.API.formatCurrency(exp.amount) : `$${exp.amount}`;
        
        div.innerHTML = `
            <div class="col-span-2 font-body-md text-body-md text-on-surface-variant">${dateFormatted}</div>
            <div class="col-span-3 font-label-lg text-label-lg text-on-surface">${exp.name}</div>
            <div class="col-span-2">
                <span class="px-3 py-1 ${catStyle.bg} ${catStyle.text} rounded-full font-label-sm text-label-sm inline-flex items-center gap-1 border ${catStyle.border}">
                    <span class="material-symbols-outlined text-[14px]">${catStyle.icon}</span>
                    ${exp.category}
                </span>
            </div>
            <div class="col-span-3 font-body-md text-body-md text-on-surface-variant truncate">${exp.note}</div>
            <div class="col-span-2 text-right font-headline-md text-headline-md text-on-surface flex items-center justify-end gap-3">
                ${amountFormatted}
                <button onclick="event.stopPropagation(); window.API.request('delete_expense', {id: ${exp.id}}).then(()=>loadExpenses());" class="w-8 h-8 rounded-full hover:bg-error-container hover:text-error text-on-surface-variant flex items-center justify-center transition-colors">
                    <span class="material-symbols-outlined text-[20px]">delete</span>
                </button>
            </div>
        `;
        container.appendChild(div);
    });
}
