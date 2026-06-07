import requests
from config.settings import TELEGRAM_BOT_TOKEN


class TelegramService:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id: int, text: str) -> bool:
        """Send text message"""
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                },
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False

    def send_typing(self, chat_id: int):
        """Send typing indicator"""
        try:
            requests.post(
                f"{self.base_url}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
                timeout=10
            )
        except Exception as e:
            print(f"❌ Error sending typing: {e}")

    def set_webhook(self, webhook_url: str) -> bool:
        """Set webhook URL"""
        try:
            response = requests.post(
                f"{self.base_url}/setWebhook",
                json={"url": webhook_url},
                timeout=30
            )
            data = response.json()
            if data.get("ok"):
                print(f"✅ Webhook set to {webhook_url}")
                return True
            print(f"❌ Webhook failed: {data}")
            return False
        except Exception as e:
            print(f"❌ Error setting webhook: {e}")
            return False

    def delete_webhook(self):
        """Delete webhook"""
        try:
            requests.post(
                f"{self.base_url}/deleteWebhook",
                timeout=30
            )
        except Exception as e:
            print(f"❌ Error deleting webhook: {e}")