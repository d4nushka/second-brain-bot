import requests
import base64
from config.settings import GROQ_API_KEY, TELEGRAM_BOT_TOKEN, GROQ_VISION_MODEL


class ImageService:
    def __init__(self):
        self.groq_key = GROQ_API_KEY
        self.bot_token = TELEGRAM_BOT_TOKEN

    def get_file_path(self, file_id: str) -> str:
        """Get file path from Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getFile?file_id={file_id}"
            response = requests.get(url, timeout=30)
            data = response.json()
            if data.get("ok"):
                return data["result"]["file_path"]
            return None
        except Exception as e:
            print(f"❌ Error getting file path: {e}")
            return None

    def analyze(self, file_id: str) -> str:
        """Analyze image using Groq Vision"""
        try:
            file_path = self.get_file_path(file_id)
            if not file_path:
                return None

            image_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_VISION_MODEL,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            },
                            {
                                "type": "text",
                                "text": "Describe this image in detail. What do you see?"
                            }
                        ]
                    }]
                },
                timeout=60
            )

            if response.status_code == 200:
                description = response.json()["choices"][0]["message"]["content"]
                print(f"✅ Image analyzed")
                return description
            else:
                print(f"❌ Image analysis failed: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
            return None