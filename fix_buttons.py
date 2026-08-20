import os, re

HTML_DIR = "app/assets/www/html"

def inject_onclick(html, button_text, navigate_target):
    # Regex to find a button tag that contains the button_text (ignoring internal tags like spans)
    # We look for <button ...> ... text ... </button>
    # To do this safely, we find all <button> tags, check if they contain the text, and modify them.
    
    parts = re.split(r'(?i)(<button.*?>.*?</button>)', html, flags=re.DOTALL)
    for i in range(1, len(parts), 2):
        if button_text.lower() in parts[i].lower() and 'onclick' not in parts[i].lower():
            # insert onclick into the <button ...> part
            # find the end of the <button class="..." ... > tag
            match = re.match(r'(<button)([^>]*>)', parts[i], re.IGNORECASE)
            if match:
                new_tag = f'{match.group(1)} onclick="window.API.navigate(\'{navigate_target}\')"{match.group(2)}'
                parts[i] = new_tag + parts[i][match.end():]
    return "".join(parts)


for file in os.listdir(HTML_DIR):
    if not file.endswith(".html"): continue
    path = os.path.join(HTML_DIR, file)
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
        
    html = inject_onclick(html, "Add Customer", "add_customer")
    html = inject_onclick(html, "New Customer", "add_customer")
    html = inject_onclick(html, "Add your first customer", "add_customer")
    
    html = inject_onclick(html, "New Order", "new_order")
    html = inject_onclick(html, "Add Measurement", "add_measurement")
    html = inject_onclick(html, "New Measurement", "add_measurement")
    
    html = inject_onclick(html, "Add Payment", "add_payment")
    html = inject_onclick(html, "Record Payment", "add_payment")
    html = inject_onclick(html, "New Expense", "add_expense")
    html = inject_onclick(html, "Add Expense", "add_expense")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
        
print("Buttons fixed globally!")
