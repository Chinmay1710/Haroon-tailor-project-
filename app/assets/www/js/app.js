document.addEventListener("DOMContentLoaded", function() {
    if (typeof QWebChannel !== "undefined") {
        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.pyBridge = channel.objects.bridge;
            window.pyBridge.log("WebChannel connected for page: " + window.location.pathname);
            
            // Expose a global dispatch function
            window.dispatchToPython = function(action, payload) {
                if (window.pyBridge) {
                    window.pyBridge.dispatch(action, JSON.stringify(payload || {}));
                }
            };
            
            // Hook up navigation links using data-nav attributes (language-independent)
            const navLinks = document.querySelectorAll('a[href="#"]');
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const navTarget = this.getAttribute('data-nav');
                    if (navTarget) {
                        window.dispatchToPython("navigate_to", {page: navTarget});
                    } else {
                        // Fallback: try text-based matching for any untagged links
                        let text = this.innerText.toLowerCase().trim();
                        if (text.includes("dashboard") || text.includes("डैशबोर्ड")) window.dispatchToPython("navigate_to", {page: "dashboard"});
                        else if (text.includes("customer") || text.includes("ग्राहक")) window.dispatchToPython("navigate_to", {page: "customers_list"});
                        else if (text.includes("measurement") || text.includes("माप")) window.dispatchToPython("navigate_to", {page: "measurements_list"});
                        else if (text.includes("order") || text.includes("ऑर्डर")) window.dispatchToPython("navigate_to", {page: "orders_list"});
                        else if (text.includes("payment") || text.includes("भुगतान")) window.dispatchToPython("navigate_to", {page: "payments"});
                        else if (text.includes("expense") || text.includes("खर्च")) window.dispatchToPython("navigate_to", {page: "expenses_list"});
                        else if (text.includes("report") || text.includes("रिपोर्ट")) window.dispatchToPython("navigate_to", {page: "reports"});
                        else if (text.includes("worker") || text.includes("कर्मचारी")) window.dispatchToPython("navigate_to", {page: "workers"});
                        else if (text.includes("setting") || text.includes("सेटिंग")) window.dispatchToPython("navigate_to", {page: "settings"});
                        else if (text.includes("backup") || text.includes("बैकअप")) window.dispatchToPython("navigate_to", {page: "backup_restore"});
                        else if (text.includes("help") || text.includes("मदद")) window.dispatchToPython("navigate_to", {page: "help"});
                        else if (text.includes("offline") || text.includes("ऑफ़लाइन")) { /* offline mode toggle */ }
                    }
                });
            });
            
            // Apply global shop settings
            window.applyGlobalSettings = async function() {
                try {
                    // Give api.js a moment to finish its QWebChannel setup
                    if (!window.API || !window.API.request) return; 
                    
                    const settings = await window.API.request("get_settings");
                    if (settings) {
                        document.querySelectorAll('.global-shop-name').forEach(el => {
                            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.value = settings.shop_name;
                            else el.textContent = settings.shop_name;
                        });
                        document.querySelectorAll('.global-shop-phone').forEach(el => {
                            el.textContent = settings.phone || "";
                        });
                        document.querySelectorAll('.global-shop-address').forEach(el => {
                            el.textContent = settings.address || "";
                        });
                    }
                } catch (e) {
                    console.error("Failed to apply global settings:", e);
                }
            };
            
            // Small delay to ensure window.API is ready
            setTimeout(window.applyGlobalSettings, 150);
        });
    }
});
