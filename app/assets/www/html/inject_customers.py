import re

with open("app/assets/www/html/customers_list.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add ID to search input
content = re.sub(
    r"(<input type=\"text\" placeholder=\"Search customers.*?class=\"[^\"]+\")>",
    r"\1 id=\"customer-search\">",
    content
)

# Add ID to table body
content = content.replace("<tbody>", "<tbody id=\"table-customers\">", 1)

# Inject customers.js script
if "customers.js" not in content:
    content = content.replace("</body>", "<script src=\"../js/customers.js\"></script>\n</body>")

with open("app/assets/www/html/customers_list.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Customers List HTML updated with IDs.")
