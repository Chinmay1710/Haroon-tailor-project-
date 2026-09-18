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
 overlay.className = 'fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4 backdrop-blur-sm ';
 
 const modal = document.createElement('div');
 modal.className = 'bg-surface rounded-xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col transform transition-transform scale-100';
 
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

 /**
 * Similar to confirm, but includes a checkbox (e.g. for sending WhatsApp).
 * Resolves with { confirmed: boolean, checked: boolean }
 */
 confirmWithCheckbox: function(title, message, checkboxLabel, defaultChecked = true) {
 return new Promise((resolve) => {
 const overlay = document.createElement('div');
 overlay.className = 'fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 backdrop-blur-sm';
 
 const modal = document.createElement('div');
 modal.className = 'bg-surface rounded-xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col transform transition-transform scale-100';
 
 const checkedAttr = defaultChecked ? 'checked' : '';
 modal.innerHTML = `
 <div class="p-6 pb-4">
 <h3 class="text-[18px] font-bold text-on-surface mb-2">${title}</h3>
 <p class="text-[14px] text-on-surface-variant leading-relaxed mb-4">${message}</p>
 <label class="flex items-center gap-3 cursor-pointer">
 <input type="checkbox" id="confirm-cb" ${checkedAttr} class="w-5 h-5 text-primary border-outline-variant rounded focus:ring-primary">
 <span class="font-label-lg text-on-surface">${checkboxLabel}</span>
 </label>
 </div>
 <div class="bg-surface-container-lowest px-6 py-4 flex justify-end gap-3 border-t border-outline-variant/30">
 <button id="confirm-cb-cancel" class="px-5 py-2 rounded-lg text-[14px] font-bold text-on-surface hover:bg-surface-container-highest transition-colors">Cancel</button>
 <button id="confirm-cb-ok" class="px-5 py-2 rounded-lg bg-primary text-[14px] font-bold text-on-primary hover:bg-primary/90 transition-colors shadow-sm">Confirm</button>
 </div>
 `;
 
 overlay.appendChild(modal);
 document.body.appendChild(overlay);
 
 document.getElementById('confirm-cb-cancel').onclick = () => {
 overlay.remove();
 resolve({ confirmed: false, checked: false });
 };
 
 document.getElementById('confirm-cb-ok').onclick = () => {
 const checked = document.getElementById('confirm-cb').checked;
 overlay.remove();
 resolve({ confirmed: true, checked: checked });
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
 
 toast.className = `px-4 py-3 rounded shadow-lg border ${bgColor} flex items-center `;
 toast.innerHTML = `<span class="font-medium">${message}</span>`;
 
 container.appendChild(toast);
 
 // Remove after 3 seconds
 

 toast.style.opacity = '0';
 setTimeout(() => toast.remove(), 300);
 
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
 },
 
 /** Attach a Mic button to a textarea or input */
 attachMic: function(textareaId) {
 const textarea = document.getElementById(textareaId);
 if (!textarea) return;
 
 let container = textarea.parentNode;
 
 // Wrap textarea in a relative container if its parent isn't already relative
 if (!container.classList.contains('relative')) {
 const wrapper = document.createElement('div');
 wrapper.className = 'relative flex-1 w-full';
 textarea.parentNode.insertBefore(wrapper, textarea);
 wrapper.appendChild(textarea);
 container = wrapper;
 }
 
 // Create Mic Button container
 const micContainer = document.createElement('div');
 micContainer.className = 'absolute right-2 bottom-2 flex items-center bg-surface rounded-full shadow-sm border border-outline-variant/30 p-1';
 
 // Create Mic Button
 const micBtn = document.createElement('button');
 micBtn.type = 'button';
 micBtn.className = 'w-8 h-8 rounded-full bg-surface-container-high hover:bg-surface-container-highest flex items-center justify-center transition-colors text-on-surface-variant';
 micBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">mic</span>';
 
 let isRecording = false;
 
 micBtn.onclick = async (e) => {
 e.preventDefault();
 if (isRecording) {
 // Stop recording
 isRecording = false;
 micBtn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">sync</span>';
 micBtn.classList.remove('bg-error', 'text-on-error', 'animate-pulse');
 
 // Store the textarea reference for the result handler
 window._activeDictationTextarea = textarea;
 
 // Get preferred language from settings, default to en-IN
 const lang = localStorage.getItem('dictationLanguage') || 'en-IN';
 await window.API.request('stop_dictation', { language: lang });
 } else {
 // Start recording
 isRecording = true;
 micBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">mic</span>';
 micBtn.classList.add('bg-error', 'text-on-error', 'animate-pulse');
 
 await window.API.request('start_dictation', { textarea_id: textareaId });
 }
 };
 
 micContainer.appendChild(micBtn);
 container.appendChild(micContainer);
 
 // Ensure element has enough padding so text doesn't hide behind mic
 if (textarea.tagName.toLowerCase() === 'textarea') {
 textarea.style.paddingBottom = '40px';
 } else {
 micContainer.classList.remove('bottom-2');
 micContainer.classList.add('top-1/2', '-translate-y-1/2');
 textarea.style.paddingRight = '50px'; // Room for mic
 }
 },
 
 /** Invoked by Python when dictation is finished */
 handleDictationResult: function(textareaId, text, error) {
 if (error) {
 window.API.toast(error, "error");
 } else if (text) {
 const textarea = document.getElementById(textareaId) || window._activeDictationTextarea;
 if (textarea) {
 const currentVal = textarea.value;
 textarea.value = currentVal ? currentVal + " " + text : text;
 // Dispatch input event to trigger any watchers
 textarea.dispatchEvent(new Event('input', { bubbles: true }));
 }
 window.API.toast("Dictation successful", "success");
 }
 
 // Reset mic button state manually or rely on attachMic's next click
 // Since we don't have direct access to the button here, we could add a class to reset it
 const wrapper = (document.getElementById(textareaId) || window._activeDictationTextarea)?.parentNode;
 if (wrapper) {
 const micBtn = wrapper.querySelector('button');
 if (micBtn) {
 micBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">mic</span>';
 micBtn.className = 'w-8 h-8 rounded-full bg-surface-container-high hover:bg-surface-container-highest flex items-center justify-center transition-colors text-on-surface-variant';
 const langSelect = wrapper.querySelector('select');
 if (langSelect) langSelect.disabled = false;
 }
 }
 },

  /**
   * Show Partial Delivery Modal to select items to deliver
   * @param {Array} items - List of order items
   * @returns Promise<Array|null> - Returns array of selected item IDs or null if cancelled
   */
  showPartialDeliveryModal: function(items) {
    return new Promise((resolve) => {
      const overlay = document.createElement('div');
      overlay.className = 'fixed inset-0 bg-black/60 z-[200] flex items-center justify-center p-4 backdrop-blur-sm';
      
      const modal = document.createElement('div');
      modal.className = 'bg-surface rounded-xl shadow-2xl w-full max-w-md flex flex-col max-h-[80vh] overflow-hidden';
      
      const header = document.createElement('div');
      header.className = 'p-6 pb-4 border-b border-outline-variant/30';
      header.innerHTML = `
        <h3 class="text-[18px] font-bold text-primary">Select Items to Deliver</h3>
        <p class="text-[14px] text-on-surface-variant mt-1">Check the items you are delivering right now.</p>
      `;
      
      const body = document.createElement('div');
      body.className = 'p-6 overflow-y-auto flex-1 flex flex-col gap-3';
      
      let pendingCount = 0;
      items.forEach(item => {
        const isDelivered = item.is_delivered === true;
        if (!isDelivered) pendingCount++;
        
        const label = document.createElement('label');
        label.className = `flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${isDelivered ? 'bg-surface-container-lowest border-outline-variant/30 opacity-60' : 'bg-surface border-outline-variant hover:border-primary'}`;
        
        const imgHtml = item.image_path ? `<img src="${item.image_path.split(',')[0]}" class="w-12 h-12 object-cover rounded-md flex-shrink-0">` : `<div class="w-12 h-12 bg-surface-container rounded-md flex items-center justify-center flex-shrink-0 text-on-surface-variant"><span class="material-symbols-outlined">apparel</span></div>`;
        
        label.innerHTML = `
          <div class="pt-1">
            <input type="checkbox" value="${item.id}" class="w-5 h-5 rounded border-outline text-primary focus:ring-primary item-checkbox" ${isDelivered ? 'checked disabled' : ''}>
          </div>
          ${imgHtml}
          <div class="flex-1">
            <p class="font-bold text-on-surface">${item.quantity}x ${item.clothing_type}</p>
            <p class="text-[12px] text-on-surface-variant">${isDelivered ? '<span class="text-[#047857] flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">check_circle</span> Already Delivered</span>' : 'Pending'}</p>
          </div>
        `;
        body.appendChild(label);
      });
      
      if (pendingCount === 0) {
        body.innerHTML = '<div class="text-center p-4 text-on-surface-variant">All items are already delivered.</div>';
      }
      
      const footer = document.createElement('div');
      footer.className = 'bg-surface-container-lowest px-6 py-4 flex justify-end gap-3 border-t border-outline-variant/30';
      footer.innerHTML = `
        <button id="pd-cancel" class="px-5 py-2 rounded-lg text-[14px] font-bold text-on-surface hover:bg-surface-container-highest transition-colors">Cancel</button>
        <button id="pd-confirm" class="px-5 py-2 rounded-lg bg-primary text-[14px] font-bold text-on-primary hover:bg-primary/90 transition-colors shadow-sm" ${pendingCount === 0 ? 'disabled' : ''}>Confirm Delivery</button>
      `;
      
      modal.appendChild(header);
      modal.appendChild(body);
      modal.appendChild(footer);
      overlay.appendChild(modal);
      document.body.appendChild(overlay);
      
      document.getElementById('pd-cancel').onclick = () => {
        overlay.remove();
        resolve(null);
      };
      
      document.getElementById('pd-confirm').onclick = () => {
        const checkboxes = body.querySelectorAll('.item-checkbox:not(:disabled)');
        const selectedIds = [];
        checkboxes.forEach(cb => {
          if (cb.checked) selectedIds.push(parseInt(cb.value));
        });
        
        if (selectedIds.length === 0 && pendingCount > 0) {
            window.API.toast("Please select at least one item to deliver.", "error");
            return;
        }
        
        overlay.remove();
        resolve(selectedIds);
      };
    });
  }
};
