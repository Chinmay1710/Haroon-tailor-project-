import re
import os

HTML_DIR = "app/assets/www/html"

def fix_deliveries():
    with open(f"{HTML_DIR}/deliveries.html", "r", encoding="utf-8") as f:
        html = f.read()
    if '<script src="../js/deliveries.js"></script>' not in html:
        html = html.replace("</body>", '  <script src="../js/deliveries.js"></script>\n</body>')
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">12</div>', '<div id="del-due-today" class="text-3xl font-bold text-slate-800 mt-2">0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">8</div>', '<div id="del-due-tomorrow" class="text-3xl font-bold text-slate-800 mt-2">0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">24</div>', '<div id="del-upcoming" class="text-3xl font-bold text-slate-800 mt-2">0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">3</div>', '<div id="del-overdue" class="text-3xl font-bold text-red-600 mt-2">0</div>', 1)
    html = html.replace('<tbody class="divide-y divide-slate-100">', '<tbody id="deliveries-table-body" class="divide-y divide-slate-100">')
    with open(f"{HTML_DIR}/deliveries.html", "w", encoding="utf-8") as f: f.write(html)

def fix_expenses():
    with open(f"{HTML_DIR}/expenses_list.html", "r", encoding="utf-8") as f:
        html = f.read()
    if '<script src="../js/expenses.js"></script>' not in html:
        html = html.replace("</body>", '  <script src="../js/expenses.js"></script>\n</body>')
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">₹1,200</div>', '<div id="exp-today" class="text-3xl font-bold text-slate-800 mt-2">₹0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">₹8,500</div>', '<div id="exp-week" class="text-3xl font-bold text-slate-800 mt-2">₹0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">₹32,400</div>', '<div id="exp-month" class="text-3xl font-bold text-slate-800 mt-2">₹0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">4</div>', '<div id="exp-count" class="text-3xl font-bold text-slate-800 mt-2">0</div>', 1)
    html = html.replace('<tbody class="divide-y divide-slate-100">', '<tbody id="expenses-table-body" class="divide-y divide-slate-100">')
    html = html.replace('<button class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">', '<button onclick="openExpenseModal()" class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">')
    with open(f"{HTML_DIR}/expenses_list.html", "w", encoding="utf-8") as f: f.write(html)

def fix_reports():
    with open(f"{HTML_DIR}/reports.html", "r", encoding="utf-8") as f:
        html = f.read()
    if '<script src="../js/reports.js"></script>' not in html:
        html = html.replace("</body>", '  <script src="../js/reports.js"></script>\n</body>')
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">₹1,42,500</div>', '<div id="rep-total-sales" class="text-3xl font-bold text-slate-800 mt-2">₹0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">128</div>', '<div id="rep-total-orders" class="text-3xl font-bold text-slate-800 mt-2">0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-slate-800 mt-2">₹12,400</div>', '<div id="rep-total-expenses" class="text-3xl font-bold text-slate-800 mt-2">₹0</div>', 1)
    html = html.replace('<div class="text-3xl font-bold text-emerald-600 mt-2">₹1,30,100</div>', '<div id="rep-net-profit" class="text-3xl font-bold text-emerald-600 mt-2">₹0</div>', 1)
    with open(f"{HTML_DIR}/reports.html", "w", encoding="utf-8") as f: f.write(html)

def fix_settings():
    with open(f"{HTML_DIR}/settings.html", "r", encoding="utf-8") as f:
        html = f.read()
    if '<script src="../js/settings.js"></script>' not in html:
        html = html.replace("</body>", '  <script src="../js/settings.js"></script>\n</body>')
    
    html = html.replace('value="Artisan Stitch"', 'id="shop_name" value=""')
    html = html.replace('value="Arif Khan"', 'id="owner_name" value=""')
    html = html.replace('value="+91 98765 43210"', 'id="phone" value=""')
    html = html.replace('>123 Tailor Street, Fashion District, Mumbai, 400001</textarea>', ' id="address"></textarea>')
    html = html.replace('name="currency" class', 'id="currency_symbol" class')
    html = html.replace('name="unit" class', 'id="measurement_unit" class')
    html = html.replace('<button class="bg-slate-900 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors">', '<button onclick="saveSettings()" class="bg-slate-900 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors">')
    
    with open(f"{HTML_DIR}/settings.html", "w", encoding="utf-8") as f: f.write(html)

def fix_customers():
    with open(f"{HTML_DIR}/customers_list.html", "r", encoding="utf-8") as f:
        html = f.read()
    if '<script src="../js/customers.js"></script>' not in html:
        html = html.replace("</body>", '  <script src="../js/customers.js"></script>\n</body>')
    html = html.replace('<tbody class="divide-y divide-slate-100">', '<tbody id="customers-table-body" class="divide-y divide-slate-100">')
    html = html.replace('<button class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">', '<button onclick="openNewCustomerModal()" class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">')
    html = html.replace('type="text" placeholder="Search customers..."', 'id="customer-search-input" type="text" placeholder="Search customers..." oninput="searchCustomers()"')
    with open(f"{HTML_DIR}/customers_list.html", "w", encoding="utf-8") as f: f.write(html)

def fix_measurements():
    with open(f"{HTML_DIR}/measurements_list.html", "r", encoding="utf-8") as f:
        html = f.read()
    if '<script src="../js/measurements.js"></script>' not in html:
        html = html.replace("</body>", '  <script src="../js/measurements.js"></script>\n</body>')
    html = html.replace('<tbody class="divide-y divide-slate-100">', '<tbody id="measurements-table-body" class="divide-y divide-slate-100">')
    html = html.replace('<button class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">', '<button onclick="window.API.navigate(\'new_measurement\')" class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">')
    html = html.replace('type="text" placeholder="Search measurements..."', 'id="measurement-search-input" type="text" placeholder="Search measurements..." oninput="searchMeasurements()"')
    with open(f"{HTML_DIR}/measurements_list.html", "w", encoding="utf-8") as f: f.write(html)

def fix_orders():
    with open(f"{HTML_DIR}/orders_list.html", "r", encoding="utf-8") as f:
        html = f.read()
    if '<script src="../js/orders.js"></script>' not in html:
        html = html.replace("</body>", '  <script src="../js/orders.js"></script>\n</body>')
    html = html.replace('<tbody class="divide-y divide-slate-100">', '<tbody id="orders-table-body" class="divide-y divide-slate-100">')
    html = html.replace('<button class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">', '<button onclick="window.API.navigate(\'new_order\')" class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">')
    with open(f"{HTML_DIR}/orders_list.html", "w", encoding="utf-8") as f: f.write(html)

def fix_payments():
    with open(f"{HTML_DIR}/payments.html", "r", encoding="utf-8") as f:
        html = f.read()
    if '<script src="../js/payments.js"></script>' not in html:
        html = html.replace("</body>", '  <script src="../js/payments.js"></script>\n</body>')
    html = html.replace('<tbody class="divide-y divide-slate-100">', '<tbody id="payments-table-body" class="divide-y divide-slate-100">')
    html = html.replace('<button class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">', '<button onclick="openPaymentModal()" class="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">')
    with open(f"{HTML_DIR}/payments.html", "w", encoding="utf-8") as f: f.write(html)


fix_deliveries()
fix_expenses()
fix_reports()
fix_settings()
fix_customers()
fix_measurements()
fix_orders()
fix_payments()
print("All HTML IDs fixed.")
