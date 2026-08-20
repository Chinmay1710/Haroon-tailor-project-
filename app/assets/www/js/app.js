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
            
            // Example: hook up navigation links (assuming href="#" is used for nav)
            const navLinks = document.querySelectorAll('a[href="#"]');
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    let text = this.innerText.toLowerCase().trim();
                    if (text.includes("dashboard")) window.dispatchToPython("navigate_to", {page: "dashboard"});
                    else if (text.includes("customer")) window.dispatchToPython("navigate_to", {page: "customers_list"});
                    else if (text.includes("measurement")) window.dispatchToPython("navigate_to", {page: "measurements_list"});
                    else if (text.includes("order")) window.dispatchToPython("navigate_to", {page: "orders_list"});
                    else if (text.includes("payment")) window.dispatchToPython("navigate_to", {page: "payments"});
                    else if (text.includes("deliver")) window.dispatchToPython("navigate_to", {page: "deliveries"});
                    else if (text.includes("expense")) window.dispatchToPython("navigate_to", {page: "expenses_list"});
                    else if (text.includes("report")) window.dispatchToPython("navigate_to", {page: "reports"});
                    else if (text.includes("setting")) window.dispatchToPython("navigate_to", {page: "settings"});
                    else if (text.includes("backup")) window.dispatchToPython("navigate_to", {page: "backup_restore"});
                });
            });
        });
    }
});
