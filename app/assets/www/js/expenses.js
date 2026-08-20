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
        
        document.getElementById('exp-this-month').innerText = window.API.formatCurrency(data.summary.total_this_month);
        document.getElementById('exp-count').innerText = data.summary.count_this_month;
        document.getElementById('exp-top-cat').innerText = data.summary.top_category || 'None';
        
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
        (e.title && e.title.toLowerCase().includes(q)) || 
        (e.category && e.category.toLowerCase().includes(q))
    );
    renderExpenses(filtered);
}

function renderExpenses(expenses) {
    const tbody = document.getElementById('table-expenses');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (expenses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-on-surface-variant">No expenses found</td></tr>';
        return;
    }
    
    expenses.forEach(exp => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-surface-container last:border-0 hover:bg-surface-container-highest/20 transition-colors cursor-pointer';
        
        const catIcons = {
            'Materials': 'inventory_2',
            'Utilities': 'bolt',
            'Rent': 'home_work',
            'Salary': 'payments',
            'Maintenance': 'build',
            'Other': 'receipt_long'
        };
        const icon = catIcons[exp.category] || 'receipt_long';
        
        tr.innerHTML = `
            <td class="p-4">
                <p class="font-label-lg text-on-surface">${exp.title}</p>
                <p class="font-label-sm text-on-surface-variant">${window.API.formatDate(exp.expense_date)}</p>
            </td>
            <td class="p-4">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-outline text-[18px]">${icon}</span>
                    <span class="text-on-surface-variant">${exp.category}</span>
                </div>
            </td>
            <td class="p-4 font-medium">${window.API.formatCurrency(exp.amount)}</td>
            <td class="p-4 text-right">
                <button onclick="event.stopPropagation(); window.API.request('delete_expense', {id: ${exp.id}}).then(()=>loadExpenses());" class="w-8 h-8 rounded-full hover:bg-error-container hover:text-on-error-container text-on-surface-variant flex items-center justify-center transition-colors">
                    <span class="material-symbols-outlined text-[20px]">delete</span>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}
