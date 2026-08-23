from __future__ import annotations
import os
import subprocess
import platform
from app.utils.logger import get_logger

logger = get_logger(__name__)

class WhatsAppService:
    """Service to handle cross-platform WhatsApp automation via Node.js + whatsapp-web.js."""
    
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

    def connect_whatsapp(self):
        """Pops open a terminal running the login script, works on Mac & Windows."""
        try:
            logger.info("Opening terminal for WhatsApp connection...")
            login_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "whatsapp", "login.js"))
            
            if platform.system() == "Darwin": # macOS
                script = f'''
                tell application "Terminal"
                    activate
                    do script "node \\"{login_script_path}\\""
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=True)
            elif platform.system() == "Windows":
                # Start a new cmd window on Windows
                subprocess.run(f'start cmd /k "node "{login_script_path}""', shell=True, check=True)
            else:
                # Linux fallback
                subprocess.run(["gnome-terminal", "--", "bash", "-c", f'node "{login_script_path}"; exec bash'], check=True)
                
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
            send_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "whatsapp", "send.js"))
            
            command = ["node", send_script_path, formatted_phone, message]
            if pdf_path and os.path.exists(pdf_path):
                command.append(pdf_path)
                
            # Run the command silently
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=False
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
