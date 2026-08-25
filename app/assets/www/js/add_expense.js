document.addEventListener('DOMContentLoaded', () => {
    function init() {
        if (!window.pyBridge) {
            setTimeout(init, 100);
            return;
        }
        
        // Set default date to today
        const dateInput = document.getElementById('expenseDate');
        if (dateInput) {
            dateInput.valueAsDate = new Date();
        }

        const form = document.getElementById('add-expense-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await saveExpense();
            });
        }
    }
    
    init();
});

async function saveExpense() {
    const name = document.getElementById('expenseName').value.trim();
    const amountStr = document.getElementById('expenseAmount').value;
    const amount = parseFloat(amountStr.replace(/[₹, ]/g, ''));
    const category = document.getElementById('expenseCategory').value;
    const date = document.getElementById('expenseDate').value;
    const notes = document.getElementById('expenseNotes').value.trim();
    
    if (!name || isNaN(amount) || !category || !date) {
        window.API.toast("Please fill all required fields", "error");
        return;
    }
    
    const payload = {
        name: name,
        amount: amount,
        category: category,
        expense_date: date,
        note: notes
    };
    
    try {
        const response = await window.API.request('create_expense', payload);
        if (response && response.status === 'success') {
            const successMsg = document.getElementById('success-message');
            if (successMsg) {
                successMsg.classList.remove('hidden', 'opacity-0', 'translate-y-[-10px]');
                successMsg.classList.add('opacity-100', 'translate-y-0');
                document.getElementById('add-expense-form').reset();
                document.getElementById('expenseDate').valueAsDate = new Date();
                
                setTimeout(() => {
                    successMsg.classList.add('hidden', 'opacity-0', 'translate-y-[-10px]');
                    successMsg.classList.remove('opacity-100', 'translate-y-0');
                    window.API.navigate('expenses_list');
                }, 1500);
            } else {
                window.API.navigate('expenses_list');
            }
        } else {
            window.API.toast("Failed to save expense", "error");
        }
    } catch (e) {
        console.error(e);
        window.API.toast("Error saving expense", "error");
    }
}
