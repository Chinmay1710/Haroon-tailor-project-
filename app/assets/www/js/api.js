/**
 * api.js - Asynchronous wrapper for QWebChannel bridge.
 * 
 * Provides a Promise-based API for interacting with the Python backend.
 */

window.API = {
    /**
     * Dispatch an action to Python and wait for the response.
     * @param {string} action - The action name mapped in web_bridge.py
     * @param {object} payload - Data to send to Python
     * @returns {Promise<object>} Resolves with the data payload or rejects on error.
     */
    request: function(action, payload = {}) {
        return new Promise((resolve, reject) => {
            if (!window.pyBridge) {
                console.error("pyBridge is not initialized. Cannot dispatch action: " + action);
                reject("Database connection not ready.");
                return;
            }
            
            if (action === "navigate_to" && payload) {
                sessionStorage.setItem("nav_params", JSON.stringify(payload));
            }
            
            window.pyBridge.dispatch(action, JSON.stringify(payload), function(responseStr) {
                try {
                    const response = JSON.parse(responseStr);
                    if (response.status === "success") {
                        resolve(response.data);
                    } else {
                        console.error(`API Error [${action}]:`, response.message);
                        reject(response.message || "Unknown error occurred.");
                    }
                } catch (e) {
                    console.error("Failed to parse Python response:", responseStr);
                    reject("Invalid response from database.");
                }
            });
        });
    },

    /**
     * Helper to show notifications (Toast) in the UI
     */
    navigate: function(page) {
        window.API.request('navigate_to', {page: page});
    },

    /**
     * Show a custom confirmation dialog
     * @returns Promise<boolean>
     */
    confirm: function(title, message) {
        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4 backdrop-blur-sm transition-opacity duration-200';
            
            const modal = document.createElement('div');
            modal.className = 'bg-surface rounded-xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col transform transition-transform duration-200 scale-100';
            
            modal.innerHTML = `
                <div class="p-6 pb-4">
                    <h3 class="text-[18px] font-bold text-on-surface mb-2">${title}</h3>
                    <p class="text-[14px] text-on-surface-variant leading-relaxed">${message}</p>
                </div>
                <div class="bg-surface-container-lowest px-6 py-4 flex justify-end gap-3 border-t border-outline-variant/30">
                    <button id="confirm-cancel" class="px-5 py-2 rounded-lg text-[14px] font-bold text-on-surface hover:bg-surface-container-highest transition-colors">Cancel</button>
                    <button id="confirm-ok" class="px-5 py-2 rounded-lg bg-primary text-[14px] font-bold text-on-primary hover:bg-primary/90 transition-colors shadow-sm">Confirm</button>
                </div>
            `;
            
            overlay.appendChild(modal);
            document.body.appendChild(overlay);
            
            document.getElementById('confirm-cancel').onclick = () => {
                overlay.remove();
                resolve(false);
            };
            
            document.getElementById('confirm-ok').onclick = () => {
                overlay.remove();
                resolve(true);
            };
        });
    },

    toast: function(message, type = "info") {
        // We will implement a simple floating toast in the UI if it doesn't exist.
        // For now, if there's no toast container, we'll create one.
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed bottom-4 right-4 z-50 flex flex-col gap-2';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        const bgColors = {
            'success': 'bg-green-100 text-green-800 border-green-200',
            'error': 'bg-red-100 text-red-800 border-red-200',
            'info': 'bg-blue-100 text-blue-800 border-blue-200'
        };
        const bgColor = bgColors[type] || bgColors['info'];
        
        toast.className = `px-4 py-3 rounded shadow-lg border ${bgColor} flex items-center transition-opacity duration-300`;
        toast.innerHTML = `<span class="font-medium">${message}</span>`;
        
        container.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },
    
    /** Format currency based on Indian Rupee standard (₹) */
    formatCurrency: function(amount) {
        if (amount === undefined || amount === null) return "₹0";
        return "₹" + parseFloat(amount).toLocaleString('en-IN', { maximumFractionDigits: 2 });
    },
    
    /** Format date to standard string */
    formatDate: function(dateString) {
        if (!dateString) return "";
        const d = new Date(dateString);
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    }
};
