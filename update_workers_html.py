import os
import re

html_path = "app/assets/www/html/workers.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# We need to add Tabs to the main content area so we can switch between:
# "Workers List", "Pending Approvals", "Garment Rates"

tabs_html = """
<div class="flex gap-4 mb-4 border-b border-surface-container-highest">
    <button id="tab-btn-workers" class="px-4 py-2 font-label-lg border-b-2 border-primary text-primary transition-colors" onclick="switchAdminTab('workers')">Workers Ledger</button>
    <button id="tab-btn-pending" class="px-4 py-2 font-label-lg border-b-2 border-transparent text-on-surface-variant hover:text-primary transition-colors" onclick="switchAdminTab('pending')">Pending Approvals</button>
    <button id="tab-btn-rates" class="px-4 py-2 font-label-lg border-b-2 border-transparent text-on-surface-variant hover:text-primary transition-colors" onclick="switchAdminTab('rates')">Garment Rates</button>
</div>

<div id="tab-workers" class="admin-tab-content block">
"""

# Close tab-workers and add tab-pending and tab-rates
tabs_end_html = """
</div> <!-- End tab-workers -->

<div id="tab-pending" class="admin-tab-content hidden">
    <div class="bg-surface-container-lowest rounded-xl shadow-sm border border-surface-container-highest overflow-hidden">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-surface/50 border-b border-surface-container-highest text-on-surface-variant font-label-sm uppercase tracking-wider">
                    <th class="px-6 py-4 font-medium">Date</th>
                    <th class="px-6 py-4 font-medium">Worker</th>
                    <th class="px-6 py-4 font-medium">Details</th>
                    <th class="px-6 py-4 font-medium">Amount</th>
                    <th class="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
            </thead>
            <tbody id="pending-list" class="divide-y divide-surface-container-highest">
                <!-- Populated by JS -->
            </tbody>
        </table>
    </div>
</div>

<div id="tab-rates" class="admin-tab-content hidden">
    <div class="flex justify-between items-center mb-4">
        <h3 class="font-headline-sm">Garment Piece Rates</h3>
        <div class="flex gap-2">
            <input type="text" id="new-garment-name" placeholder="Garment (e.g. Shirt)" class="px-3 py-2 border rounded-lg bg-surface">
            <input type="number" id="new-garment-rate" placeholder="Rate (₹)" class="px-3 py-2 border rounded-lg bg-surface w-24">
            <button class="bg-primary text-on-primary px-4 py-2 rounded-lg" onclick="saveGarmentRate()">Add/Update</button>
        </div>
    </div>
    <div class="bg-surface-container-lowest rounded-xl shadow-sm border border-surface-container-highest overflow-hidden">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-surface/50 border-b border-surface-container-highest text-on-surface-variant font-label-sm uppercase tracking-wider">
                    <th class="px-6 py-4 font-medium">Garment Type</th>
                    <th class="px-6 py-4 font-medium text-right">Rate (₹)</th>
                </tr>
            </thead>
            <tbody id="rates-list" class="divide-y divide-surface-container-highest">
                <!-- Populated by JS -->
            </tbody>
        </table>
    </div>
</div>
"""

# Replace the start of the table wrapper
content = content.replace(
    '<div class="bg-surface-container-lowest rounded-xl shadow-sm border border-surface-container-highest overflow-hidden flex-1">',
    tabs_html + '\n<div class="bg-surface-container-lowest rounded-xl shadow-sm border border-surface-container-highest overflow-hidden flex-1">'
)

# Replace the end of the table wrapper
content = content.replace(
    '</table>\n</div>\n</div>\n</main>',
    '</table>\n</div>\n</div>\n' + tabs_end_html + '\n</main>'
)

# Update the Workers Table Header
content = content.replace(
    """<th class="px-6 py-4 font-medium">Name</th>
<th class="px-6 py-4 font-medium">Phone</th>
<th class="px-6 py-4 font-medium">Login PIN</th>
<th class="px-6 py-4 font-medium">Status</th>
<th class="px-6 py-4 font-medium text-right">Actions</th>""",
    """<th class="px-6 py-4 font-medium">Worker</th>
<th class="px-6 py-4 font-medium">Type</th>
<th class="px-6 py-4 font-medium">Total Earned</th>
<th class="px-6 py-4 font-medium">Advance Given</th>
<th class="px-6 py-4 font-medium">Balance</th>
<th class="px-6 py-4 font-medium text-right">Actions</th>"""
)

# Update Add Worker Modal inputs
add_worker_inputs = """
<div>
<label class="block font-label-md text-on-surface mb-1.5">Full Name <span class="text-error">*</span></label>
<input class="w-full px-3 py-2.5 rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-shadow bg-surface" id="w-name" placeholder="e.g. Ramesh Tailor" type="text"/>
</div>
<div>
<label class="block font-label-md text-on-surface mb-1.5">Phone Number</label>
<input class="w-full px-3 py-2.5 rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-shadow bg-surface" id="w-phone" placeholder="10-digit number" type="text"/>
</div>
<div class="flex gap-4">
    <div class="flex-1">
        <label class="block font-label-md text-on-surface mb-1.5">4-Digit PIN <span class="text-error">*</span></label>
        <input class="w-full px-3 py-2.5 rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-shadow bg-surface font-mono tracking-[0.5em] text-center" id="w-pin" maxlength="4" placeholder="1234" type="text"/>
    </div>
    <div class="flex-1">
        <label class="block font-label-md text-on-surface mb-1.5">Worker Type</label>
        <select id="w-type" class="w-full px-3 py-2.5 rounded-lg border border-outline-variant focus:border-primary focus:ring-1 bg-surface" onchange="document.getElementById('w-rate-container').style.display = this.value === 'DAILY_SALARY' ? 'block' : 'none'">
            <option value="PIECE_RATE">Piece Rate</option>
            <option value="DAILY_SALARY">Daily Salary</option>
        </select>
    </div>
</div>
<div id="w-rate-container" style="display:none;">
    <label class="block font-label-md text-on-surface mb-1.5">Daily Rate (₹)</label>
    <input class="w-full px-3 py-2.5 rounded-lg border border-outline-variant focus:border-primary focus:ring-1 bg-surface" id="w-rate" type="number" value="0"/>
</div>
"""

content = re.sub(r'<div>\s*<label class="block font-label-md text-on-surface mb-1\.5">Full Name.*?Workers will use this PIN to log into the mobile portal\.</p>\s*</div>', add_worker_inputs, content, flags=re.DOTALL)


# Add Advance Modal
advance_modal = """
<!-- Advance Modal -->
<div class="fixed inset-0 z-50 bg-on-surface/40 hidden flex items-center justify-center backdrop-blur-sm" id="advance-modal">
<div class="bg-surface-container-lowest rounded-2xl shadow-xl w-[400px] overflow-hidden flex flex-col">
<div class="px-6 py-4 border-b border-surface-container-highest flex items-center justify-between bg-surface/50">
<h3 class="font-headline-sm">Give Advance</h3>
<button class="p-1 rounded-full hover:bg-surface-container-highest/50" onclick="document.getElementById('advance-modal').classList.add('hidden')"><span class="material-symbols-outlined">close</span></button>
</div>
<div class="p-6 space-y-4">
<input type="hidden" id="adv-worker-id">
<p id="adv-worker-name" class="font-bold text-lg mb-4"></p>
<div>
<label class="block font-label-md mb-1.5">Amount (₹)</label>
<input id="adv-amount" type="number" class="w-full px-3 py-2.5 rounded-lg border bg-surface outline-none">
</div>
<div>
<label class="block font-label-md mb-1.5">Notes</label>
<input id="adv-notes" type="text" class="w-full px-3 py-2.5 rounded-lg border bg-surface outline-none">
</div>
</div>
<div class="px-6 py-4 border-t flex justify-end gap-3 bg-surface/50">
<button class="px-5 py-2 rounded-lg" onclick="document.getElementById('advance-modal').classList.add('hidden')">Cancel</button>
<button class="px-5 py-2 rounded-lg bg-primary text-on-primary" onclick="saveAdvance()">Save</button>
</div>
</div>
</div>
"""
content = content.replace('<!-- Scripts -->', advance_modal + '\n<!-- Scripts -->')


# Update JavaScript to handle the new functionality
js_code = """
        function switchAdminTab(tab) {
            document.querySelectorAll('.admin-tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.admin-tab-content').forEach(el => el.classList.remove('block'));
            
            document.querySelectorAll('[id^="tab-btn-"]').forEach(btn => {
                btn.classList.remove('border-primary', 'text-primary');
                btn.classList.add('border-transparent', 'text-on-surface-variant');
            });
            
            document.getElementById('tab-' + tab).classList.remove('hidden');
            document.getElementById('tab-' + tab).classList.add('block');
            
            document.getElementById('tab-btn-' + tab).classList.remove('border-transparent', 'text-on-surface-variant');
            document.getElementById('tab-btn-' + tab).classList.add('border-primary', 'text-primary');
            
            if (tab === 'workers') loadWorkers();
            if (tab === 'pending') loadPending();
            if (tab === 'rates') loadRates();
        }

        async function initWorkers() {
            if (!window.pyBridge) { setTimeout(initWorkers, 100); return; }
            try {
                const portalRes = await window.API.request('get_worker_portal_url');
                if (portalRes && portalRes.url) document.getElementById('portal-url').value = portalRes.url;
                await loadWorkers();
            } catch(e) { console.error(e); }
        }
        
        async function loadWorkers() {
            try {
                const res = await window.API.request('get_all_workers');
                const tbody = document.getElementById('workers-list');
                tbody.innerHTML = '';
                
                if (!res.workers || res.workers.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="6" class="px-6 py-8 text-center text-on-surface-variant">No workers found.</td></tr>`;
                    return;
                }
                
                for (const w of res.workers) {
                    const l_res = await window.API.request('get_worker_ledger', {worker_id: w.id});
                    const ledger = l_res.ledger || {total_earned:0, total_advance:0, remaining_balance:0};
                    
                    const badge = w.worker_type === 'DAILY_SALARY' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800';
                    const typeStr = w.worker_type === 'DAILY_SALARY' ? `Daily (₹${w.daily_rate})` : 'Piece Rate';
                    
                    const tr = document.createElement('tr');
                    tr.className = "hover:bg-surface-container-lowest/50";
                    tr.innerHTML = `
                        <td class="px-6 py-4">
                            <div class="font-bold">${w.name}</div>
                            <div class="text-xs text-on-surface-variant">PIN: ${w.pin} | ${w.phone || ''}</div>
                        </td>
                        <td class="px-6 py-4"><span class="text-xs px-2 py-1 rounded ${badge} font-bold uppercase tracking-wider">${typeStr}</span></td>
                        <td class="px-6 py-4 font-bold text-green-700">₹${ledger.total_earned.toFixed(0)}</td>
                        <td class="px-6 py-4 font-bold text-orange-600">₹${ledger.total_advance.toFixed(0)}</td>
                        <td class="px-6 py-4 font-bold text-lg">₹${ledger.remaining_balance.toFixed(0)}</td>
                        <td class="px-6 py-4 text-right">
                            <button onclick="openAdvanceModal(${w.id}, '${w.name}')" class="text-sm bg-primary/10 text-primary px-3 py-1.5 rounded hover:bg-primary hover:text-white transition-colors">Give Advance</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                }
            } catch (e) { console.error(e); }
        }
        
        async function saveWorker() {
            const name = document.getElementById('w-name').value;
            const phone = document.getElementById('w-phone').value;
            const pin = document.getElementById('w-pin').value;
            const worker_type = document.getElementById('w-type').value;
            const daily_rate = document.getElementById('w-rate').value;
            
            if (!name || !pin) return;
            try {
                await window.API.request('add_worker', {name, phone, pin, worker_type, daily_rate});
                document.getElementById('add-worker-modal').classList.add('hidden');
                loadWorkers();
            } catch(e) { console.error(e); }
        }

        async function loadPending() {
            try {
                const res = await window.API.request('get_all_pending_entries');
                const tbody = document.getElementById('pending-list');
                tbody.innerHTML = '';
                if (!res.entries || res.entries.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-on-surface-variant">No pending entries.</td></tr>`;
                    return;
                }
                res.entries.forEach(e => {
                    const date = new Date(e.entry_date).toLocaleDateString();
                    let desc = e.garment_type ? `${e.quantity}x ${e.garment_type}` : 'Daily Salary';
                    if (e.bill_number) desc += ` (Bill: ${e.bill_number})`;
                    if (e.extra_work_description) desc += `<br><span class="text-xs text-on-surface-variant">Extra: ${e.extra_work_description}</span>`;
                    
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td class="px-6 py-4 text-sm">${date}</td>
                        <td class="px-6 py-4 font-bold">${e.worker_name}</td>
                        <td class="px-6 py-4 text-sm">${desc}</td>
                        <td class="px-6 py-4 font-bold text-lg">₹${e.total_amount}</td>
                        <td class="px-6 py-4 text-right">
                            <button onclick="approveEntry(${e.id}, 'APPROVED')" class="text-white bg-green-600 px-3 py-1 rounded text-sm hover:bg-green-700">Approve</button>
                            <button onclick="approveEntry(${e.id}, 'REJECTED')" class="text-white bg-red-600 px-3 py-1 rounded text-sm hover:bg-red-700 ml-1">Reject</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch(e) { console.error(e); }
        }

        async function approveEntry(id, status) {
            try {
                await window.API.request('approve_entry', {entry_id: id, status: status});
                loadPending();
            } catch(e) { console.error(e); }
        }

        async function loadRates() {
            try {
                const res = await window.API.request('get_garment_rates');
                const tbody = document.getElementById('rates-list');
                tbody.innerHTML = '';
                res.rates.forEach(r => {
                    tbody.innerHTML += `<tr>
                        <td class="px-6 py-4 font-bold">${r.garment_type}</td>
                        <td class="px-6 py-4 text-right font-mono text-lg">₹${r.rate}</td>
                    </tr>`;
                });
            } catch(e) { console.error(e); }
        }

        async function saveGarmentRate() {
            const garment_type = document.getElementById('new-garment-name').value;
            const rate = document.getElementById('new-garment-rate').value;
            if(!garment_type || !rate) return;
            try {
                await window.API.request('set_garment_rate', {garment_type, rate});
                document.getElementById('new-garment-name').value = '';
                document.getElementById('new-garment-rate').value = '';
                loadRates();
            } catch(e) { console.error(e); }
        }

        function openAdvanceModal(workerId, workerName) {
            document.getElementById('adv-worker-id').value = workerId;
            document.getElementById('adv-worker-name').textContent = workerName;
            document.getElementById('adv-amount').value = '';
            document.getElementById('adv-notes').value = '';
            document.getElementById('advance-modal').classList.remove('hidden');
        }

        async function saveAdvance() {
            const worker_id = document.getElementById('adv-worker-id').value;
            const amount = document.getElementById('adv-amount').value;
            const notes = document.getElementById('adv-notes').value;
            if(!worker_id || !amount) return;
            try {
                await window.API.request('record_advance', {worker_id, amount, notes});
                document.getElementById('advance-modal').classList.add('hidden');
                if(document.getElementById('tab-workers').classList.contains('block')) loadWorkers();
            } catch(e) { console.error(e); }
        }

        function copyPortalLink() {
            const link = document.getElementById('portal-url').value;
            if (link && link !== "Not Running" && link !== "Loading link...") {
                navigator.clipboard.writeText(link).then(() => {
                    alert("Link copied!");
                });
            }
        }
        
        document.addEventListener("DOMContentLoaded", initWorkers);
"""

# Replace the entire script block with our new one
content = re.sub(r'<script>\s*async function initWorkers\(\).*?</script>', '<script>\n' + js_code + '\n</script>', content, flags=re.DOTALL)


with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated workers.html successfully!")
