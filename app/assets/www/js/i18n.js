/**
 * i18n.js - Translation and Localization engine
 */

(function() {
    const TRANSLATIONS = {
        en: {
            "common": {
                "cancel": "Cancel",
                "save": "Save",
                "save_changes": "Save Changes",
                "delete": "Delete",
                "edit": "Edit",
                "add": "Add",
                "optional": "Optional",
                "print": "Print",
                "close": "Close",
                "back": "Back",
                "actions": "Actions",
                "status": "Status",
                "active": "Active",
                "inactive": "Inactive",
                "loading": "Loading..."
            },
            "sidebar": {
                "offline_mode": "Offline Mode",
                "backup_restore": "Backup & Restore",
                "dashboard": "Dashboard",
                "customers": "Customers",
                "measurements": "Measurements",
                "orders": "Orders",
                "payments": "Payments",
                "deliveries": "Deliveries",
                "expenses": "Expenses",
                "reports": "Reports",
                "settings": "Settings",
                "help": "Help",
                "workers": "Workers",
                "premium_tailoring": "Premium Tailoring"
            },
            "dashboard": {
                "title": "Tailor Manager",
                "welcome": "Good Morning, Artisan!",
                "today_is": "Today is",
                "orders_today": "Orders Today",
                "sales_today": "Today's Sales",
                "pending_payments": "Pending Payments",
                "deliveries_today": "Deliveries Today",
                "recent_orders": "Recent Orders",
                "view_all": "View All",
                "order_no": "Order No.",
                "customer": "Customer",
                "status": "Status",
                "actions": "Actions",
                "today_deliveries": "Today's Deliveries",
                "remaining": "Remaining",
                "items": "Items",
                "no_orders": "No orders for today.",
                "no_deliveries": "No deliveries scheduled for today.",
                "order_pipeline": "Order Pipeline",
                "urgent_alert_title": "⚠️ Urgent: Work Not Started!",
                "urgent_alert_subtitle": "These orders have delivery deadlines within 3 days but stitching hasn't begun yet."
            },
            "customers": {
                "id": "Customer ID",
                "name": "Customer Name",
                "total_orders": "Total Orders",
                "pending_amount": "Pending Amount",
                "last_order": "Last Order",
                "title": "Customer Management",
                "subtitle": "View and manage your tailor shop client profiles",
                "add_customer": "Add Customer",
                "search_ph": "Search customers by name or phone...",
                "name": "Customer Name",
                "mobile": "Mobile",
                "address": "Address",
                "notes": "Client Notes",
                "status": "Status",
                "no_customers": "No customers found."
            },
            "customer_details": {
                "contact_details": "Contact Details",
                "mobile_phone": "Mobile Phone",
                "email_address": "Email Address",
                "shipping_address": "Shipping Address",
                "notes": "Notes",
                "master_profile": "Master Profile",
                "view_all_measurements": "View All Measurements",
                "edit_customer": "Edit Customer",
                "delete_customer": "Delete Customer"
            },
            "add_customer": {
                "title": "Add New Customer",
                "title_edit": "Edit Customer Details",
                "subtitle": "Create a new client profile with contact and notes",
                "subtitle_edit": "Modify the customer's profile, contact, and notes",
                "full_name": "Full Name",
                "name_ph": "e.g. John Doe",
                "mobile": "Mobile Number",
                "mobile_ph": "10-digit mobile number",
                "address": "Address",
                "address_ph": "Street address, City, ZIP",
                "client_notes": "Client Notes",
                "notes_ph": "Preferences, fitting quirks, preferred fabrics...",
                "save_new_order": "Save & New Order",
                "save_customer": "Save Customer"
            },
            "measurements": {
                "title": "Measurements Book",
                "subtitle": "Access and update client fitting parameters",
                "add_measurement": "Add Measurement",
                "search_ph": "Search measurements by customer name...",
                "customer": "Customer",
                "last_updated": "Last Updated",
                "neck": "Neck",
                "chest": "Chest",
                "waist": "Waist",
                "hip": "Hip",
                "shoulder": "Shoulder",
                "sleeve": "Sleeve Length",
                "inseam": "Inseam",
                "outseam": "Outseam",
                "no_measurements": "No measurements recorded."
            },
            "add_measurement": {
                "title": "Add Measurement Ticket",
                "title_edit": "Edit Measurement Ticket",
                "subtitle": "Log fit details for customer styling and tailoring",
                "select_cust": "Select Customer",
                "cust_ph": "Choose customer...",
                "neck": "Neck (inches)",
                "chest": "Chest (inches)",
                "waist": "Waist (inches)",
                "hip": "Hip (inches)",
                "shoulder": "Shoulder (inches)",
                "sleeve": "Sleeve Length (inches)",
                "inseam": "Inseam (inches)",
                "outseam": "Outseam (inches)",
                "notes": "Fitting Notes / Styling Preferences",
                "notes_ph": "Loose fit, tight cuffs, high waist, etc.",
                "save_ticket": "Save Measurement"
            },
            "orders": {
                "order_info": "Order Info",
                "customer_item": "Customer & Item",
                "dates": "Dates",
                "financials": "Financials",
                "title": "Orders Tracker",
                "subtitle": "Monitor and update shop active order pipeline",
                "add_order": "New Order",
                "search_ph": "Search orders by ID or customer...",
                "order_id": "Order ID",
                "customer": "Customer",
                "date": "Order Date",
                "delivery_date": "Delivery Date",
                "items": "Items",
                "total": "Total Amount",
                "paid": "Paid",
                "remaining": "Remaining Balance",
                "status": "Status",
                "no_orders": "No orders found."
            },
            "new_order": {
                "title": "Create New Order",
                "title_edit": "Edit Order Details",
                "select_cust": "Select Customer",
                "search_cust": "Search customers...",
                "selected_cust": "Selected Customer",
                "change_cust": "Change",
                "items_list": "Order Items",
                "add_item": "Add Item",
                "delivery_date": "Delivery Date",
                "special_instr": "Special Instructions",
                "notes_ph": "Rush order, special requirements, etc.",
                "payment_details": "Payment Details",
                "order_total": "Order Total",
                "advance_paid": "Advance Paid",
                "payment_method": "Payment Method",
                "payment_cash": "Cash",
                "payment_card": "Card",
                "payment_upi": "UPI",
                "remaining_bal": "Remaining Balance",
                "save_order": "Save Order"
            },
            "payments": {
                "title": "Payments & Receipts",
                "subtitle": "Track revenue collections, advances, and settle balances",
                "add_payment": "Record Payment",
                "search_ph": "Search payments by customer or order...",
                "order_id": "Order ID",
                "customer": "Customer",
                "amount": "Amount Settle",
                "method": "Payment Method",
                "date": "Payment Date",
                "no_payments": "No payments recorded yet."
            },
            "add_payment": {
                "title": "Record Invoice Payment",
                "subtitle": "Settle outstanding balances or log advance deposits",
                "select_order": "Select Active Order",
                "amount": "Settle Amount",
                "method": "Payment Method",
                "notes": "Transaction Remarks",
                "notes_ph": "Cleared via UPI, partial deposit, etc.",
                "save_payment": "Confirm Payment"
            },
            "deliveries": {
                "title": "Delivery Operations",
                "subtitle": "Dispatch orders and manage customer handovers",
                "search_ph": "Search deliveries by customer or order...",
                "pending": "Pending Deliveries",
                "delivered": "Successfully Delivered",
                "mark_delivered": "Mark Delivered",
                "no_deliveries": "No deliveries scheduled."
            },
            "expenses": {
                "title": "Expense Register",
                "subtitle": "Track tailoring raw materials, threads, rent, and wages",
                "add_expense": "Log Expense",
                "search_ph": "Search expenses by description...",
                "category": "Expense Category",
                "amount": "Amount",
                "date": "Date",
                "description": "Description",
                "no_expenses": "No expenses logged."
            },
            "settings": {
                "title": "System Settings",
                "subtitle": "Configure shop rules, local currency, printer, and backups",
                "shop_details": "Shop Details",
                "shop_name": "Shop Name",
                "owner_name": "Owner Name",
                "contact_phone": "Contact Phone",
                "address": "Physical Address",
                "preferences": "Application Preferences",
                "currency": "Currency Symbol",
                "units": "Measurement Units",
                "printer": "Active Thermal Printer",
                "paper_size": "Paper Size",
                "save_changes": "Save Config Settings"
            },
            "workers": {
                "title": "Worker Management",
                "subtitle": "Manage tailoring staff, specialties, and wages",
                "add_worker": "Add Worker",
                "search_ph": "Search workers by name or skill...",
                "name": "Worker Name",
                "mobile": "Mobile Number",
                "skills": "Specialty / Skills",
                "status": "Active Status",
                "no_workers": "No workers recorded."
            }
        },
        hi: {
            "common": {
                "cancel": "रद्द करें",
                "save": "सहेजें",
                "save_changes": "बदलाव सहेजें",
                "delete": "हटाएं",
                "edit": "संपादित करें",
                "add": "जोड़ें",
                "optional": "वैकल्पिक",
                "print": "प्रिंट",
                "close": "बंद करें",
                "back": "वापस",
                "actions": "कार्रवाई",
                "status": "स्थिति",
                "active": "सक्रिय (Active)",
                "inactive": "निष्क्रिय (Inactive)",
                "loading": "लोड हो रहा है..."
            },
            "sidebar": {
                "offline_mode": "ऑफ़लाइन मोड",
                "backup_restore": "बैकअप और रीस्टोर",
                "offline_mode": "Offline Mode",
                "backup_restore": "Backup & Restore",
                "dashboard": "डैशबोर्ड",
                "customers": "ग्राहक सूची",
                "measurements": "माप पुस्तिका",
                "orders": "ऑर्डर ट्रैकर",
                "payments": "भुगतान रिकॉर्ड",
                "deliveries": "डिलीवरी सूची",
                "expenses": "खर्चा रजिस्टर",
                "reports": "दुकान रिपोर्ट",
                "settings": "सिस्टम सेटिंग्स",
                "help": "मदद",
                "workers": "कर्मचारी (Workers)",
                "premium_tailoring": "प्रीमियम सिलाई"
            },
            "dashboard": {
                "title": "दर्जी प्रबंधक",
                "welcome": "सुप्रभात, कारीगर!",
                "today_is": "आज है",
                "orders_today": "आज के ऑर्डर",
                "sales_today": "आज की बिक्री",
                "pending_payments": "लंबित भुगतान",
                "deliveries_today": "आज की डिलीवरी",
                "recent_orders": "हाल के ऑर्डर",
                "view_all": "सभी देखें",
                "order_no": "ऑर्डर नंबर",
                "customer": "ग्राहक",
                "status": "स्थिति",
                "actions": "कार्रवाई",
                "today_deliveries": "आज की डिलीवरी सूची",
                "remaining": "शेष",
                "items": "सामान",
                "no_orders": "आज के लिए कोई ऑर्डर नहीं है।",
                "no_deliveries": "आज के लिए कोई डिलीवरी निर्धारित नहीं है।",
                "order_pipeline": "ऑर्डर पाइपलाइन",
                "urgent_alert_title": "⚠️ जरूरी: काम शुरू नहीं हुआ!",
                "urgent_alert_subtitle": "इन ऑर्डरों की डिलीवरी 3 दिनों के अंदर है लेकिन सिलाई अभी तक शुरू नहीं हुई है।"
            },
            "customers": {
                "id": "ग्राहक आईडी",
                "name": "ग्राहक का नाम",
                "total_orders": "कुल ऑर्डर",
                "pending_amount": "बकाया राशि",
                "last_order": "पिछला ऑर्डर",
                "id": "Customer ID",
                "name": "Customer Name",
                "total_orders": "Total Orders",
                "pending_amount": "Pending Amount",
                "last_order": "Last Order",
                "title": "ग्राहक प्रबंधन",
                "subtitle": "अपने दर्जी की दुकान के ग्राहक प्रोफाइल देखें और प्रबंधित करें",
                "add_customer": "ग्राहक जोड़ें",
                "search_ph": "नाम या फोन द्वारा ग्राहक खोजें...",
                "name": "ग्राहक का नाम",
                "mobile": "मोबाइल नंबर",
                "address": "पता",
                "notes": "ग्राहक नोट्स",
                "status": "स्थिति",
                "no_customers": "कोई ग्राहक नहीं मिला।"
            },
            "customer_details": {
                "contact_details": "संपर्क विवरण",
                "mobile_phone": "मोबाइल फोन",
                "email_address": "ईमेल पता",
                "shipping_address": "शिपिंग का पता",
                "notes": "नोट्स",
                "master_profile": "मास्टर प्रोफ़ाइल",
                "view_all_measurements": "सभी माप देखें",
                "edit_customer": "ग्राहक संपादित करें",
                "delete_customer": "ग्राहक हटाएं"
            },
            "add_customer": {
                "title": "नया ग्राहक जोड़ें",
                "title_edit": "ग्राहक विवरण संपादित करें",
                "subtitle": "संपर्क और नोट्स के साथ नया ग्राहक प्रोफ़ाइल बनाएं",
                "subtitle_edit": "ग्राहक की प्रोफ़ाइल, संपर्क और नोट्स बदलें",
                "full_name": "पूरा नाम",
                "name_ph": "जैसे: राजेश कुमार",
                "mobile": "मोबाइल नंबर",
                "mobile_ph": "10-अंकीय मोबाइल नंबर",
                "address": "पता",
                "address_ph": "गली का पता, शहर, पिनकोड",
                "client_notes": "ग्राहक नोट्स",
                "notes_ph": "पसंद, फिटिंग की आदतें, पसंदीदा कपड़े...",
                "save_new_order": "सहेजें और नया ऑर्डर",
                "save_customer": "ग्राहक सहेजें"
            },
            "measurements": {
                "title": "माप पुस्तिका",
                "subtitle": "ग्राहक फिटिंग मानकों को देखें और अपडेट करें",
                "add_measurement": "नया माप लें",
                "search_ph": "ग्राहक के नाम से माप खोजें...",
                "customer": "ग्राहक",
                "last_updated": "आखिरी अपडेट",
                "neck": "गला (Neck)",
                "chest": "छाती (Chest)",
                "waist": "कमर (Waist)",
                "hip": "हिप (Hip)",
                "shoulder": "कंधा (Shoulder)",
                "sleeve": "आस्तीन (Sleeve)",
                "inseam": "इनसीम (Inseam)",
                "outseam": "आउटसीम (Outseam)",
                "no_measurements": "कोई माप रिकॉर्ड नहीं मिला।"
            },
            "add_measurement": {
                "title": "माप टिकट जोड़ें",
                "title_edit": "माप टिकट संपादित करें",
                "subtitle": "ग्राहक की फिटिंग और स्टाइलिंग विवरण दर्ज करें",
                "select_cust": "ग्राहक चुनें",
                "cust_ph": "ग्राहक का चयन करें...",
                "neck": "गला (इंच)",
                "chest": "छाती (इंच)",
                "waist": "कमर (इंच)",
                "hip": "हिप (इंच)",
                "shoulder": "कंधा (इंच)",
                "sleeve": "आस्तीन की लंबाई (इंच)",
                "inseam": "इनसीम (इंच)",
                "outseam": "आउटसीम (इंच)",
                "notes": "फिटिंग नोट्स / स्टाइलिंग प्राथमिकताएं",
                "notes_ph": "ढीला फिट, तंग कफ, ऊंची कमर, आदि।",
                "save_ticket": "माप सहेजें"
            },
            "orders": {
                "order_info": "ऑर्डर जानकारी",
                "customer_item": "ग्राहक और कपड़े",
                "dates": "तारीख",
                "financials": "वित्तीय विवरण",
                "order_info": "Order Info",
                "customer_item": "Customer & Item",
                "dates": "Dates",
                "financials": "Financials",
                "title": "ऑर्डर ट्रैकर",
                "subtitle": "दुकान की सक्रिय ऑर्डर स्थिति पर नज़र रखें",
                "add_order": "नया ऑर्डर",
                "search_ph": "आईडी या ग्राहक द्वारा ऑर्डर खोजें...",
                "order_id": "ऑर्डर आईडी",
                "customer": "ग्राहक",
                "date": "ऑर्डर की तारीख",
                "delivery_date": "डिलीवरी की तारीख",
                "items": "सामान",
                "total": "कुल राशि",
                "paid": "भुगतान किया",
                "remaining": "शेष राशि",
                "status": "स्थिति",
                "no_orders": "कोई ऑर्डर नहीं मिला।"
            },
            "new_order": {
                "title": "नया ऑर्डर बनाएं",
                "title_edit": "ऑर्डर संपादित करें",
                "select_cust": "ग्राहक चुनें",
                "search_cust": "ग्राहक खोजें...",
                "selected_cust": "चयनित ग्राहक",
                "change_cust": "बदलें",
                "items_list": "ऑर्डर की चीजें",
                "add_item": "चीज जोड़ें",
                "delivery_date": "डिलीवरी की तारीख",
                "special_instr": "विशेष निर्देश",
                "notes_ph": "जल्दी ऑर्डर, विशेष आवश्यकताएं, आदि।",
                "payment_details": "भुगतान का विवरण",
                "order_total": "कुल ऑर्डर राशि",
                "advance_paid": "अग्रिम भुगतान",
                "payment_method": "भुगतान का तरीका",
                "payment_cash": "नकद (Cash)",
                "payment_card": "कार्ड (Card)",
                "payment_upi": "यूपीआई (UPI)",
                "remaining_bal": "शेष राशि",
                "save_order": "ऑर्डर सहेजें"
            },
            "payments": {
                "title": "भुगतान और रसीदें",
                "subtitle": "राजस्व संग्रह, अग्रिम राशि को ट्रैक करें और शेष राशि का निपटान करें",
                "add_payment": "भुगतान दर्ज करें",
                "search_ph": "ग्राहक या ऑर्डर द्वारा भुगतान खोजें...",
                "order_id": "ऑर्डर आईडी",
                "customer": "ग्राहक",
                "amount": "भुगतान राशि",
                "method": "भुगतान का तरीका",
                "date": "भुगतान की तारीख",
                "no_payments": "अभी तक कोई भुगतान दर्ज नहीं है।"
            },
            "add_payment": {
                "title": "चालान भुगतान दर्ज करें",
                "subtitle": "बकाया राशि का निपटान करें या अग्रिम जमा राशि दर्ज करें",
                "select_order": "सक्रिय ऑर्डर चुनें",
                "amount": "भुगतान राशि",
                "method": "भुगतान विधि",
                "notes": "लेनदेन विवरण",
                "notes_ph": "UPI द्वारा भुगतान किया गया, आंशिक भुगतान, आदि।",
                "save_payment": "भुगतान की पुष्टि करें"
            },
            "deliveries": {
                "title": "डिलीवरी ऑपरेशंस",
                "subtitle": "ऑर्डर प्रेषित करें और ग्राहक हैंडओवर प्रबंधित करें",
                "search_ph": "ग्राहक या ऑर्डर द्वारा डिलीवरी खोजें...",
                "pending": "लंबित डिलीवरी",
                "delivered": "सफलतापूर्वक वितरित",
                "mark_delivered": "डिलीवरी पूरी करें",
                "no_deliveries": "कोई डिलीवरी निर्धारित नहीं है।"
            },
            "expenses": {
                "title": "खर्चा रजिस्टर",
                "subtitle": "कच्चा माल, धागे, किराया, और मजदूरी को ट्रैक करें",
                "add_expense": "खर्च दर्ज करें",
                "search_ph": "विवरण द्वारा खर्च खोजें...",
                "category": "खर्च की श्रेणी",
                "amount": "राशि",
                "date": "तारीख",
                "description": "विवरण",
                "no_expenses": "कोई खर्च दर्ज नहीं किया गया।"
            },
            "settings": {
                "title": "सिस्टम सेटिंग्स",
                "subtitle": "दुकान के नियम, स्थानीय मुद्रा, प्रिंटर और बैकअप कॉन्फ़िगर करें",
                "shop_details": "दुकान का विवरण",
                "shop_name": "दुकान का नाम",
                "owner_name": "मालिक का नाम",
                "contact_phone": "संपर्क फोन",
                "address": "दुकान का पता",
                "preferences": "एप्लिकेशन प्राथमिकताएं",
                "currency": "मुद्रा चिन्ह (Currency)",
                "units": "माप की इकाई",
                "printer": "सक्रिय थर्मल प्रिंटर",
                "paper_size": "कागज का आकार",
                "save_changes": "सेटिंग्स सहेजें"
            },
            "workers": {
                "title": "कर्मचारी प्रबंधन",
                "subtitle": "सिलाई स्टाफ, विशिष्टताओं और वेतन का प्रबंधन करें",
                "add_worker": "कर्मचारी जोड़ें",
                "search_ph": "नाम या कौशल द्वारा कर्मचारी खोजें...",
                "name": "कर्मचारी का नाम",
                "mobile": "मोबाइल नंबर",
                "skills": "कौशल / विशेषता",
                "status": "सक्रिय स्थिति",
                "no_workers": "कोई कर्मचारी दर्ज नहीं है।"
            }
        }
    };

    let currentLang = localStorage.getItem('selected_language') || 'en';

    window.I18n = {
        getLang: () => currentLang,
        setLang: (lang) => {
            if (TRANSLATIONS[lang]) {
                currentLang = lang;
                localStorage.setItem('selected_language', lang);
                window.I18n.apply();
                
                const btnEn = document.getElementById('lang-btn-en');
                const btnHi = document.getElementById('lang-btn-hi');
                if (btnEn && btnHi) {
                    if (lang === 'en') {
                        btnEn.className = "flex-1 py-2.5 rounded-lg font-bold border transition-colors bg-primary-container text-on-primary-container border-primary-container";
                        btnHi.className = "flex-1 py-2.5 rounded-lg font-bold border transition-colors bg-transparent text-on-surface-variant border-outline-variant hover:text-on-surface";
                    } else {
                        btnHi.className = "flex-1 py-2.5 rounded-lg font-bold border transition-colors bg-primary-container text-on-primary-container border-primary-container";
                        btnEn.className = "flex-1 py-2.5 rounded-lg font-bold border transition-colors bg-transparent text-on-surface-variant border-outline-variant hover:text-on-surface";
                    }
                }
            }
        },
        t: (keyPath) => {
            const keys = keyPath.split('.');
            let obj = TRANSLATIONS[currentLang];
            for (let key of keys) {
                if (obj && obj[key] !== undefined) {
                    obj = obj[key];
                } else {
                    let fallbackObj = TRANSLATIONS['en'];
                    for (let fallbackKey of keys) {
                        if (fallbackObj && fallbackObj[fallbackKey] !== undefined) {
                            fallbackObj = fallbackObj[fallbackKey];
                        } else {
                            return keyPath;
                        }
                    }
                    return fallbackObj;
                }
            }
            return obj;
        },
        apply: () => {
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                el.textContent = window.I18n.t(key);
            });

            document.querySelectorAll('[data-i18n-ph]').forEach(el => {
                const key = el.getAttribute('data-i18n-ph');
                el.setAttribute('placeholder', window.I18n.t(key));
            });

            document.documentElement.setAttribute('lang', currentLang);
        },
        init: () => {
            window.I18n.setLang(currentLang);
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        window.I18n.init();
    });
})();
