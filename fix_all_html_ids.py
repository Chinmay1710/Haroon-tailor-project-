import os
import re

HTML_DIR = "app/assets/www/html"

def fix_file(filename, replacements):
    path = os.path.join(HTML_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    
    for old, new in replacements:
        if old in html:
            html = html.replace(old, new)
        else:
            print(f"Warning: '{old}' not found in {filename}")
            
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

print("Fixing Dashboard...")
fix_file("dashboard.html", [
    ('<button class="bg-surface-container-lowest hover:bg-surface-container transition-colors p-4 rounded-xl shadow-[0px_4px_20px_rgba(0,0,0,0.05)] border border-surface-container-low flex flex-col items-center justify-center gap-2 h-24">\n<span class="material-symbols-outlined text-primary">person_add</span>',
     '<button onclick="window.API.navigate(\'customers_list\')" class="bg-surface-container-lowest hover:bg-surface-container transition-colors p-4 rounded-xl shadow-[0px_4px_20px_rgba(0,0,0,0.05)] border border-surface-container-low flex flex-col items-center justify-center gap-2 h-24">\n<span class="material-symbols-outlined text-primary">person_add</span>'),
    
    ('<button class="bg-primary hover:bg-primary/90 transition-colors p-4 rounded-xl shadow-[0px_4px_20px_rgba(0,0,0,0.1)] border border-transparent flex flex-col items-center justify-center gap-2 h-24 text-on-primary">\n<span class="material-symbols-outlined">add_circle</span>',
     '<button onclick="window.API.navigate(\'new_order\')" class="bg-primary hover:bg-primary/90 transition-colors p-4 rounded-xl shadow-[0px_4px_20px_rgba(0,0,0,0.1)] border border-transparent flex flex-col items-center justify-center gap-2 h-24 text-on-primary">\n<span class="material-symbols-outlined">add_circle</span>'),
     
    ('<button class="bg-surface-container-lowest hover:bg-surface-container transition-colors p-4 rounded-xl shadow-[0px_4px_20px_rgba(0,0,0,0.05)] border border-surface-container-low flex flex-col items-center justify-center gap-2 h-24">\n<span class="material-symbols-outlined text-[#8B4513]">payments</span>',
     '<button onclick="window.API.navigate(\'payments\')" class="bg-surface-container-lowest hover:bg-surface-container transition-colors p-4 rounded-xl shadow-[0px_4px_20px_rgba(0,0,0,0.05)] border border-surface-container-low flex flex-col items-center justify-center gap-2 h-24">\n<span class="material-symbols-outlined text-[#8B4513]">payments</span>'),
     
    ('<button class="bg-surface-container-lowest hover:bg-surface-container transition-colors p-4 rounded-xl shadow-[0px_4px_20px_rgba(0,0,0,0.05)] border border-surface-container-low flex flex-col items-center justify-center gap-2 h-24">\n<span class="material-symbols-outlined text-[#dc2626]">receipt_long</span>',
     '<button onclick="window.API.navigate(\'expenses_list\')" class="bg-surface-container-lowest hover:bg-surface-container transition-colors p-4 rounded-xl shadow-[0px_4px_20px_rgba(0,0,0,0.05)] border border-surface-container-low flex flex-col items-center justify-center gap-2 h-24">\n<span class="material-symbols-outlined text-[#dc2626]">receipt_long</span>'),
     
    ('<div class="space-y-4">', '<div id="recent-orders-list" class="space-y-4">')
])

print("Fixing Customers...")
with open(os.path.join(HTML_DIR, "customers_list.html"), "r", encoding="utf-8") as f: html = f.read()
html = re.sub(r'<tbody class="divide-y divide-surface-variant[^>]*>', '<tbody id="customers-table-body" class="divide-y divide-surface-variant">', html)
html = re.sub(r'<button class="bg-primary[^>]*>\s*<span class="material-symbols-outlined text-\[18px\]">add</span>\s*<span>New Customer</span>\s*</button>', '<button onclick="openNewCustomerModal()" class="bg-primary text-on-primary px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors flex items-center gap-2">\n<span class="material-symbols-outlined text-[18px]">add</span>\n<span>New Customer</span>\n</button>', html)
html = re.sub(r'<input type="text" placeholder="Search customers..."', '<input id="customer-search-input" type="text" placeholder="Search customers..." oninput="searchCustomers()"', html)
with open(os.path.join(HTML_DIR, "customers_list.html"), "w", encoding="utf-8") as f: f.write(html)

print("Fixing Measurements...")
with open(os.path.join(HTML_DIR, "measurements_list.html"), "r", encoding="utf-8") as f: html = f.read()
html = re.sub(r'<tbody class="divide-y divide-surface-variant[^>]*>', '<tbody id="measurements-table-body" class="divide-y divide-surface-variant">', html)
html = re.sub(r'<button class="bg-primary[^>]*>\s*<span class="material-symbols-outlined text-\[18px\]">add</span>\s*<span>New Measurement</span>\s*</button>', '<button onclick="window.API.navigate(\'new_measurement\')" class="bg-primary text-on-primary px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors flex items-center gap-2">\n<span class="material-symbols-outlined text-[18px]">add</span>\n<span>New Measurement</span>\n</button>', html)
html = re.sub(r'<input type="text" placeholder="Search measurements..."', '<input id="measurement-search-input" type="text" placeholder="Search measurements..." oninput="searchMeasurements()"', html)
with open(os.path.join(HTML_DIR, "measurements_list.html"), "w", encoding="utf-8") as f: f.write(html)

print("Fixing Orders...")
with open(os.path.join(HTML_DIR, "orders_list.html"), "r", encoding="utf-8") as f: html = f.read()
html = re.sub(r'<tbody class="divide-y divide-surface-variant[^>]*>', '<tbody id="orders-table-body" class="divide-y divide-surface-variant">', html)
html = re.sub(r'<button class="bg-primary[^>]*>\s*<span class="material-symbols-outlined text-\[18px\]">add</span>\s*<span>New Order</span>\s*</button>', '<button onclick="window.API.navigate(\'new_order\')" class="bg-primary text-on-primary px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors flex items-center gap-2">\n<span class="material-symbols-outlined text-[18px]">add</span>\n<span>New Order</span>\n</button>', html)
html = re.sub(r'<input type="text" placeholder="Search orders..."', '<input id="order-search-input" type="text" placeholder="Search orders..." oninput="searchOrders()"', html)
with open(os.path.join(HTML_DIR, "orders_list.html"), "w", encoding="utf-8") as f: f.write(html)

print("Fixing Deliveries...")
with open(os.path.join(HTML_DIR, "deliveries.html"), "r", encoding="utf-8") as f: html = f.read()
html = re.sub(r'<tbody class="divide-y divide-surface-variant[^>]*>', '<tbody id="deliveries-table-body" class="divide-y divide-surface-variant">', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">12</p>', '<p id="del-due-today" class="font-headline-lg text-headline-lg text-on-surface mt-1">12</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">8</p>', '<p id="del-due-tomorrow" class="font-headline-lg text-headline-lg text-on-surface mt-1">8</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">24</p>', '<p id="del-upcoming" class="font-headline-lg text-headline-lg text-on-surface mt-1">24</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">3</p>', '<p id="del-overdue" class="font-headline-lg text-headline-lg text-error mt-1">3</p>', html)
with open(os.path.join(HTML_DIR, "deliveries.html"), "w", encoding="utf-8") as f: f.write(html)

print("Fixing Expenses...")
with open(os.path.join(HTML_DIR, "expenses_list.html"), "r", encoding="utf-8") as f: html = f.read()
html = re.sub(r'<tbody class="divide-y divide-surface-variant[^>]*>', '<tbody id="expenses-table-body" class="divide-y divide-surface-variant">', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">₹1,200</p>', '<p id="exp-today" class="font-headline-lg text-headline-lg text-on-surface mt-1">₹1,200</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">₹8,500</p>', '<p id="exp-week" class="font-headline-lg text-headline-lg text-on-surface mt-1">₹8,500</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">₹32,400</p>', '<p id="exp-month" class="font-headline-lg text-headline-lg text-on-surface mt-1">₹32,400</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">4</p>', '<p id="exp-count" class="font-headline-lg text-headline-lg text-on-surface mt-1">4</p>', html)
html = re.sub(r'<button class="bg-primary[^>]*>\s*<span class="material-symbols-outlined text-\[18px\]">add</span>\s*<span>New Expense</span>\s*</button>', '<button onclick="openExpenseModal()" class="bg-primary text-on-primary px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors flex items-center gap-2">\n<span class="material-symbols-outlined text-[18px]">add</span>\n<span>New Expense</span>\n</button>', html)
with open(os.path.join(HTML_DIR, "expenses_list.html"), "w", encoding="utf-8") as f: f.write(html)

print("Fixing Reports...")
with open(os.path.join(HTML_DIR, "reports.html"), "r", encoding="utf-8") as f: html = f.read()
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">₹1,42,500</p>', '<p id="rep-total-sales" class="font-headline-lg text-headline-lg text-on-surface mt-1">₹1,42,500</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">128</p>', '<p id="rep-total-orders" class="font-headline-lg text-headline-lg text-on-surface mt-1">128</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-on-surface mt-1">₹12,400</p>', '<p id="rep-total-expenses" class="font-headline-lg text-headline-lg text-on-surface mt-1">₹12,400</p>', html)
html = re.sub(r'<p class="font-headline-lg text-headline-lg text-\[#10b981\] mt-1">₹1,30,100</p>', '<p id="rep-net-profit" class="font-headline-lg text-headline-lg text-emerald-600 mt-1">₹1,30,100</p>', html)
with open(os.path.join(HTML_DIR, "reports.html"), "w", encoding="utf-8") as f: f.write(html)

print("Fixing Payments...")
with open(os.path.join(HTML_DIR, "payments.html"), "r", encoding="utf-8") as f: html = f.read()
html = re.sub(r'<tbody class="divide-y divide-surface-variant[^>]*>', '<tbody id="payments-table-body" class="divide-y divide-surface-variant">', html)
html = re.sub(r'<button class="bg-primary[^>]*>\s*<span class="material-symbols-outlined text-\[18px\]">add</span>\s*<span>Record Payment</span>\s*</button>', '<button onclick="openPaymentModal()" class="bg-primary text-on-primary px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors flex items-center gap-2">\n<span class="material-symbols-outlined text-[18px]">add</span>\n<span>Record Payment</span>\n</button>', html)
html = re.sub(r'<input type="text" placeholder="Search payments..."', '<input id="payment-search-input" type="text" placeholder="Search payments..." oninput="searchPayments()"', html)
with open(os.path.join(HTML_DIR, "payments.html"), "w", encoding="utf-8") as f: f.write(html)

print("Fixing Settings...")
with open(os.path.join(HTML_DIR, "settings.html"), "r", encoding="utf-8") as f: html = f.read()
html = re.sub(r'value="Artisan Stitch"', 'id="shop_name" value=""', html)
html = re.sub(r'value="Arif Khan"', 'id="owner_name" value=""', html)
html = re.sub(r'value="\+91 98765 43210"', 'id="phone" value=""', html)
html = re.sub(r'>123 Tailor Street, Fashion District, Mumbai, 400001</textarea>', ' id="address"></textarea>', html)
html = re.sub(r'name="currency" class="([^"]*)"', r'id="currency_symbol" class="\1"', html)
html = re.sub(r'name="unit" class="([^"]*)"', r'id="measurement_unit" class="\1"', html)
html = re.sub(r'<button class="bg-primary[^>]*>\s*Save Changes\s*</button>', '<button onclick="saveSettings()" class="bg-primary text-on-primary px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">Save Changes</button>', html)
with open(os.path.join(HTML_DIR, "settings.html"), "w", encoding="utf-8") as f: f.write(html)

print("Done.")
