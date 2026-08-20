import re

with open("app/assets/www/html/dashboard.html", "r") as f:
    content = f.read()

content = re.sub(
    r"(ORDERS TODAY.*?<h3 class=\"[^\"]+\")>(\d+)",
    r"\1 id=\"stat-orders-today\">\2",
    content, flags=re.DOTALL
)
content = re.sub(
    r"(TODAY'S SALES.*?<h3 class=\"[^\"]+\")>(₹[0-9,]+)",
    r"\1 id=\"stat-sales-today\">\2",
    content, flags=re.DOTALL
)
content = re.sub(
    r"(PENDING PAYMENTS.*?<h3 class=\"[^\"]+\")>(₹[0-9,]+)",
    r"\1 id=\"stat-pending-payments\">\2",
    content, flags=re.DOTALL
)
content = re.sub(
    r"(DELIVERIES TODAY.*?<h3 class=\"[^\"]+\")>(\d+)",
    r"\1 id=\"stat-deliveries-today\">\2",
    content, flags=re.DOTALL
)

content = re.sub(r"(<h3 class=\"text-headline-lg[^\"]+\")>(24)(</h3>\s*<p class=\"[^\"]+\">New)", r"\1 id=\"pipe-new\">\2\3", content)
content = re.sub(r"(<h3 class=\"text-headline-lg[^\"]+\")>(18)(</h3>\s*<p class=\"[^\"]+\">Stitching)", r"\1 id=\"pipe-stitching\">\2\3", content)
content = re.sub(r"(<h3 class=\"text-headline-lg[^\"]+\")>(12)(</h3>\s*<p class=\"[^\"]+\">Ready)", r"\1 id=\"pipe-ready\">\2\3", content)
content = re.sub(r"(<h3 class=\"text-headline-lg[^\"]+\")>(45)(</h3>\s*<p class=\"[^\"]+\">Delivered)", r"\1 id=\"pipe-delivered\">\2\3", content)
content = re.sub(r"(<h3 class=\"text-headline-lg[^\"]+\")>(3)(</h3>\s*<p class=\"[^\"]+\">Overdue)", r"\1 id=\"pipe-overdue\">\2\3", content)

content = content.replace("<tbody>", "<tbody id=\"table-deliveries-today\">", 1)
content = re.sub(r"(<h2 class=\"text-headline-md.*?Recent Orders.*?<div class=\"flex flex-col gap-3\")>", r"\1 id=\"recent-orders-list\">", content, flags=re.DOTALL)

if "dashboard.js" not in content:
    content = content.replace("</body>", "<script src=\"../js/dashboard.js\"></script>\n</body>")

with open("app/assets/www/html/dashboard.html", "w") as f:
    f.write(content)

print("Dashboard HTML updated with IDs.")
