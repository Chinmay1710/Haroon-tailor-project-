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
            from pyngrok import ngrok
            logger.info(f"Starting ngrok tunnel for port {self.port}")
            self.tunnel = ngrok.connect(self.port)
            self.public_url = self.tunnel.public_url
            GLOBAL_TUNNEL_URL = self.public_url
            logger.info(f"Ngrok tunnel established: {self.public_url}")
            return self.public_url
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
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
        if self.tunnel:
            try:
                from pyngrok import ngrok
                ngrok.disconnect(self.public_url)
                logger.info("Ngrok tunnel disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting ngrok: {e}")
            self.tunnel = None
            self.public_url = None
