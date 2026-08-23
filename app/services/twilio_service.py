from __future__ import annotations
import os
from twilio.rest import Client
from app.utils.logger import get_logger
from app.database.engine import get_session
from app.repositories.settings_repo import SettingsRepository

logger = get_logger(__name__)

class TwilioService:
    def __init__(self):
        self.session = get_session()
        try:
            self.settings = SettingsRepository(self.session).get_settings()
        finally:
            self.session.close()

    def get_client(self) -> Client | None:
        sid = self.settings.twilio_account_sid
        token = self.settings.twilio_auth_token
        if not sid or not token:
            return None
        try:
            return Client(sid, token)
        except Exception as e:
            logger.error(f"Failed to initialize Twilio Client: {e}")
            return None

    def _format_phone(self, number: str) -> str:
        """Format number for Twilio WhatsApp (adds whatsapp: prefix)."""
        # If it doesn't have a country code, you might want to default to +91 or similar,
        # but usually it's best to expect a properly formatted number.
        if not number.startswith('+'):
            number = '+91' + number.lstrip('0')
        return f"whatsapp:{number}"

    def send_message(self, to_number: str, message: str, media_url: str = None) -> bool:
        """
        Send a WhatsApp message using Twilio.
        Note: For media_url to work with local PDFs, you either need to host the PDF publicly,
        or if using WhatsApp's API directly, it expects a public URL. 
        Since this is a local app, we might need a workaround for media, but we can send text.
        """
        client = self.get_client()
        sender_num = self.settings.twilio_sender_number

        if not client or not sender_num:
            logger.warning("Twilio not configured. Cannot send message.")
            return False

        if not to_number:
            logger.warning("No recipient number provided for Twilio message.")
            return False

        from_str = self._format_phone(sender_num)
        to_str = self._format_phone(to_number)

        try:
            kwargs = {
                'from_': from_str,
                'body': message,
                'to': to_str
            }
            if media_url:
                kwargs['media_url'] = [media_url]

            msg = client.messages.create(**kwargs)
            logger.info(f"Twilio message sent to {to_str} (SID: {msg.sid})")
            return True
        except Exception as e:
            logger.error(f"Failed to send Twilio message to {to_str}: {e}")
            return False
