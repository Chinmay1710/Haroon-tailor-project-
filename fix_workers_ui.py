import os

html_dir = "app/assets/www/html"
customers_path = os.path.join(html_dir, "customers_list.html")
workers_path = os.path.join(html_dir, "workers.html")

# Read customers_list.html to extract its <head> and sidebar
with open(customers_path, "r", encoding="utf-8") as f:
    customers_content = f.read()

# Extract head
head_start = customers_content.find("<head>")
head_end = customers_content.find("</head>") + len("</head>")
customers_head = customers_content[head_start:head_end]

# Read workers.html
with open(workers_path, "r", encoding="utf-8") as f:
    workers_content = f.read()

# Replace head
workers_head_start = workers_content.find("<head>")
workers_head_end = workers_content.find("</head>") + len("</head>")
new_workers_content = workers_content[:workers_head_start] + customers_head + workers_content[workers_head_end:]

# Replace sidebar nav
nav_start = new_workers_content.find("<nav")
nav_end = new_workers_content.find("</nav>") + len("</nav>")

cust_nav_start = customers_content.find("<nav")
cust_nav_end = customers_content.find("</nav>") + len("</nav>")
cust_nav = customers_content[cust_nav_start:cust_nav_end]

# Set active state on Workers tab instead of Customers tab
# In cust_nav, Customers has: class="flex items-center gap-3 px-4 py-3 rounded-lg bg-surface-container-highest/10 text-on-primary font-bold border-l-4 border-surface-container-highest opacity-90 transition-all"
# We need to swap this with the Workers tab.
# Actually, since inject_workers_bs4.py runs dynamically, let's just use the exact nav from customers, and rely on the UI to maybe not highlight it, or we can manually swap the classes.

inactive_class = 'class="flex items-center gap-3 px-4 py-3 rounded-lg text-on-primary/70 font-body-md hover:text-on-primary hover:bg-primary-container/20 transition-colors duration-200"'
active_class = 'class="flex items-center gap-3 px-4 py-3 rounded-lg bg-surface-container-highest/10 text-on-primary font-bold border-l-4 border-surface-container-highest opacity-90 transition-all"'

# Make Customers inactive
cust_nav = cust_nav.replace(active_class, inactive_class)
cust_nav = cust_nav.replace('data-icon="person">person', 'data-icon="person">person')

# Make Workers active
# Find workers tab
import re
workers_pattern = re.compile(r'(<a[^>]+href="#"[^>]*>\s*<span[^>]*>engineering</span>\s*<span[^>]*>Workers</span>\s*</a>)')
workers_match = workers_pattern.search(cust_nav)
if workers_match:
    w_tab = workers_match.group(1)
    new_w_tab = w_tab.replace(inactive_class, active_class)
    cust_nav = cust_nav.replace(w_tab, new_w_tab)

new_workers_content = new_workers_content[:nav_start] + cust_nav + new_workers_content[nav_end:]

# Also replace TopAppBar to match
topbar_start = new_workers_content.find("<header")
topbar_end = new_workers_content.find("</header>") + len("</header>")
cust_topbar_start = customers_content.find("<header")
cust_topbar_end = customers_content.find("</header>") + len("</header>")
new_workers_content = new_workers_content[:topbar_start] + customers_content[cust_topbar_start:cust_topbar_end] + new_workers_content[topbar_end:]

with open(workers_path, "w", encoding="utf-8") as f:
    f.write(new_workers_content)

print("workers.html updated with correct head, sidebar, and topbar from customers_list.html")
