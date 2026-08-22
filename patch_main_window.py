import re

with open("app/ui/main_window.py", "r") as f:
    content = f.read()

# Add worker_service import
if "from app.services.worker_service import worker_service" not in content:
    content = content.replace("from app.services.backup_service import BackupService", "from app.services.backup_service import BackupService\nfrom app.services.worker_service import worker_service")

# Add worker to services
services_str = """        self.services = {
            'customer': CustomerService(),
            'order': OrderService(),
            'payment': PaymentService(),
            'measurement': MeasurementService(),
            'expense': ExpenseService(),
            'report': ReportService(),
            'backup': BackupService(),
            'worker': worker_service
        }"""
content = re.sub(r'self\.services = \{[^\}]+\}', services_str, content)

# Start server and tunnel
init_str = """
        self.web_bridge = WebBridge(self.services, self)
        
        # Start Worker Portal Server
        try:
            from app.web.server import WebServerThread
            self.web_server = WebServerThread()
            self.web_server.start()
            
            from app.web.tunnel import NgrokTunnel
            self.tunnel = NgrokTunnel()
            self.tunnel_url = self.tunnel.start()
        except Exception as e:
            logger.error(f"Failed to start web server/tunnel: {e}")
            self.tunnel_url = None
"""
content = re.sub(r'self\.web_bridge = WebBridge\(self\.services, self\)', init_str, content)

# Expose tunnel_url to frontend via web_bridge. We will need to update web_bridge.py for this.
# But for now, let's save main_window.py
with open("app/ui/main_window.py", "w") as f:
    f.write(content)

