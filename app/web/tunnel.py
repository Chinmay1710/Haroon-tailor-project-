import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

GLOBAL_TUNNEL_URL = None

class NgrokTunnel:
    def __init__(self, port=8000):
        self.port = port
        self.public_url = None
        self.tunnel = None

    def start(self) -> Optional[str]:
        global GLOBAL_TUNNEL_URL

        try:
            import subprocess
            import re
            import os
            import json
            
            logger.info("Starting cloudflared tunnel...")
            
            import sys
            
            # Resolve executable path correctly when frozen by PyInstaller
            if getattr(sys, 'frozen', False):
                exe_path = os.path.join(sys._MEIPASS, "cloudflared.exe")
            else:
                exe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cloudflared.exe")
                if not os.path.exists(exe_path):
                    exe_path = "cloudflared.exe" if os.path.exists("cloudflared.exe") else "cloudflared"

            # Check for Cloudflare Zero Trust Configuration (Permanent Domain) in AppData
            from app.config import APP_DATA_DIR
            cf_config_file = os.path.join(APP_DATA_DIR, "cloudflare_config.json")
            
            if os.path.exists(cf_config_file):
                try:
                    with open(cf_config_file, 'r') as f:
                        cf_config = json.load(f)
                        token = cf_config.get("token")
                        domain = cf_config.get("domain")
                        
                        if token and domain:
                            if not domain.startswith("http"):
                                domain = "https://" + domain
                                
                            logger.info(f"Starting Permanent Cloudflare Zero Trust tunnel: {domain}")
                            self.public_url = domain
                            GLOBAL_TUNNEL_URL = self.public_url
                            
                            self.lt_process = subprocess.Popen(
                                [exe_path, "tunnel", "run", "--token", token],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True
                            )
                            return self.public_url
                except Exception as e:
                    logger.error(f"Error reading cloudflare_config.json: {e}")

            # Fallback to Free Quick Tunnel (Random Domain)
            logger.info("No token found. Starting temporary Quick Tunnel...")
            self.lt_process = subprocess.Popen(
                [exe_path, "tunnel", "--url", f"http://localhost:{self.port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Wait for the trycloudflare URL in the output
            for line in iter(self.lt_process.stdout.readline, ''):
                match = re.search(r'(https?://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
                if match:
                    self.public_url = match.group(1)
                    GLOBAL_TUNNEL_URL = self.public_url
                    logger.info(f"Cloudflare tunnel established: {self.public_url}")
                    return self.public_url
                    
            raise Exception("Cloudflare tunnel did not return a URL")
        except Exception as e_lt:
            logger.error(f"Failed to start cloudflared: {e_lt}")
            
            # Fallback to local IP
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                self.public_url = f"http://{local_ip}:{self.port}"
                GLOBAL_TUNNEL_URL = self.public_url
                logger.info(f"Using local IP fallback for worker portal: {self.public_url}")
                return self.public_url
            except Exception as e2:
                logger.error(f"Failed to get local IP: {e2}")
                self.public_url = f"http://localhost:{self.port}"
                GLOBAL_TUNNEL_URL = self.public_url
                return self.public_url

    def stop(self):
        if hasattr(self, 'lt_process') and self.lt_process:
            try:
                self.lt_process.terminate()
            except:
                pass
                
        if self.tunnel:
            try:
                from pyngrok import ngrok
                ngrok.disconnect(self.public_url)
                logger.info("Ngrok tunnel disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting ngrok: {e}")
            self.tunnel = None
            self.public_url = None
