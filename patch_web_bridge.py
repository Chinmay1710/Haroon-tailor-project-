import re

with open("app/ui/web_bridge.py", "r") as f:
    content = f.read()

# Add get_worker_portal_url action
action_str = """
            # ────────────────────────────────────────────────────────────
            # WORKER PORTAL
            # ────────────────────────────────────────────────────────────
            elif action == "get_worker_portal_url":
                tunnel_url = getattr(self.parent(), "tunnel_url", None)
                if tunnel_url:
                    response = {"status": "success", "url": tunnel_url}
                else:
                    response = {"status": "error", "message": "Portal is not running"}

            elif action == "get_all_workers":
                worker_srv = self.services["worker"]
                workers = worker_srv.get_all_workers()
                response = {"status": "success", "workers": workers}

            elif action == "add_worker":
                worker_srv = self.services["worker"]
                w = worker_srv.add_worker(payload.get("name"), payload.get("phone"), payload.get("pin"))
                response = {"status": "success", "worker": w}

            elif action == "assign_task":
                worker_srv = self.services["worker"]
                t = worker_srv.assign_task(payload.get("worker_id"), payload.get("order_item_id"), payload.get("payout_amount"))
                response = {"status": "success", "task": t}
                
            elif action == "get_worker_tasks":
                worker_srv = self.services["worker"]
                t = worker_srv.get_worker_tasks(payload.get("worker_id"))
                response = {"status": "success", "tasks": t}
"""

if "get_worker_portal_url" not in content:
    content = content.replace('if action == "navigate_to":', action_str + '\n            if action == "navigate_to":')

with open("app/ui/web_bridge.py", "w") as f:
    f.write(content)
