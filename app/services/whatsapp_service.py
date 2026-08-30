from __future__ import annotations
import os
import subprocess
import platform
from app.utils.logger import get_logger

logger = get_logger(__name__)

class WhatsAppService:
    """Service to handle cross-platform WhatsApp automation via Node.js + whatsapp-web.js."""
    
    @staticmethod
    def _get_node_executable() -> str:
        """Returns the bundled node.exe path if packaged, else 'node'."""
        import sys
        if getattr(sys, 'frozen', False):
            bundled_node = os.path.join(sys._MEIPASS, "node.exe")
            if os.path.exists(bundled_node):
                return bundled_node
        return "node"
        
    @staticmethod
    def _get_script_path(script_name: str) -> str:
        """Returns the absolute path to the node script depending on freeze state."""
        import sys
        if getattr(sys, 'frozen', False):
            # In PyInstaller, the datas=[('app/services/whatsapp', 'app/services/whatsapp')] copies it perfectly
            return os.path.join(sys._MEIPASS, "app", "services", "whatsapp", script_name)
        else:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), "whatsapp", script_name))
    
    @staticmethod
    def _format_phone(number: str) -> str:
        """Format number for WhatsApp (must have country code)."""
        if not number:
            return ""
        # Remove all non-numeric characters
        clean_num = ''.join(filter(str.isdigit, number))
        if len(clean_num) == 10:
            clean_num = "91" + clean_num
        return clean_num

    @staticmethod
    def _get_node_env() -> dict:
        """Returns environment variables with bundled Puppeteer cache dir if frozen."""
        import os, sys
        env = os.environ.copy()
        if getattr(sys, 'frozen', False):
            env["PUPPETEER_CACHE_DIR"] = os.path.join(sys._MEIPASS, ".puppeteer_cache")
        return env

    def connect_whatsapp(self):
        """Pops open a terminal running the login script, works on Mac & Windows."""
        try:
            logger.info("Opening terminal for WhatsApp connection...")
            login_script_path = self._get_script_path("login.js")
            node_exe = self._get_node_executable()
            
            if platform.system() == "Darwin": # macOS
                script = f'''
                tell application "Terminal"
                    activate
                    do script "{node_exe} \\"{login_script_path}\\""
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=True)
            elif platform.system() == "Windows":
                # Start a new cmd window on Windows
                subprocess.run(f'start cmd /k "{node_exe}" "{login_script_path}"', shell=True, check=True, env=self._get_node_env())
            else:
                # Linux fallback
                subprocess.run(["gnome-terminal", "--", "bash", "-c", f'"{node_exe}" "{login_script_path}"; exec bash'], check=True, env=self._get_node_env())
                
            return True
        except Exception as e:
            logger.error(f"Failed to open terminal for WhatsApp connection: {e}")
            return False

    def send_whatsapp_message(self, phone_number: str, message: str, pdf_path: str = None) -> bool:
        """
        Sends a WhatsApp message natively via the background Node script.
        """
        formatted_phone = self._format_phone(phone_number)
        if not formatted_phone:
            logger.warning("No valid phone number provided for WhatsApp.")
            return False
            
        try:
            logger.info(f"Sending WhatsApp message via wweb.js to {formatted_phone}...")
            send_script_path = self._get_script_path("send.js")
            node_exe = self._get_node_executable()
            
            command = [node_exe, send_script_path, formatted_phone, message]
            if pdf_path and os.path.exists(pdf_path):
                command.append(pdf_path)
                
            # Run the command silently
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                env=self._get_node_env()
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully sent WhatsApp message to {formatted_phone}.")
                return True
            else:
                logger.error(f"wweb.js failed to send message: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message via wweb.js: {e}")
            return False
