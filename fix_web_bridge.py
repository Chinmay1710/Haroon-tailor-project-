import re

with open("app/ui/web_bridge.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove everything after the first update_settings (around line 380) to clear the buggy duplicates
# We know the duplicate get_all_measurements starts at line 391.
# Let's just find the second occurrence of get_all_measurements and truncate before it.
parts = content.split('            elif action == "get_all_measurements":')
if len(parts) > 2:
    # It appeared twice. 
    # Truncate string at the start of the second one
    content = parts[0] + '            elif action == "get_all_measurements":' + parts[1]
    # Wait, parts[1] goes up to the third duplicate if there are more, but there's only 2.
    # Actually, let's just find the duplicated section:
    # It started after update_settings
    # We can just cut off anything after "# MEASUREMENTS" that appears a second time.
    meas_header = "# MEASUREMENTS"
    header_parts = content.split(meas_header)
    if len(header_parts) > 2:
        # Rejoin up to the second header, and strip trailing whitespace
        content = meas_header.join(header_parts[:2]).rstrip()

# Now fix the real get_all_measurements (at the top)
content = re.sub(
    r'(elif action == "get_all_measurements":.*?measurements = meas_srv\.get_all_profiles\(\)\s+data = \[\]\s+for m in measurements:).*?response = \{"status": "success", "data": data\}',
    r'''\1
                    data.append({
                        "id": m.id,
                        "name": m.name,
                        "customer_name": m.customer.name if m.customer else "Unknown",
                        "template_type": m.template_type,
                        "values_count": len(m.values),
                        "updated_at": m.updated_at.isoformat()
                    })
                response = {"status": "success", "data": data}''',
    content,
    flags=re.DOTALL
)

# Fix get_measurements_for_customer
content = re.sub(
    r'(elif action == "get_measurements_for_customer":.*?measurements = meas_srv\.get_customer_measurements\(cust_id\)\s+data = \[\]\s+for m in measurements:).*?response = \{"status": "success", "data": data\}',
    r'''\1
                    vals = {}
                    for v in m.values:
                        vals[v.field_name] = v.field_value
                    data.append({
                        "id": m.id,
                        "template_type": m.template_type,
                        "values": vals,
                        "updated_at": m.updated_at.isoformat()
                    })
                response = {"status": "success", "data": data}''',
    content,
    flags=re.DOTALL
)

with open("app/ui/web_bridge.py", "w", encoding="utf-8") as f:
    f.write(content)

print("web_bridge.py cleaned and fixed!")
