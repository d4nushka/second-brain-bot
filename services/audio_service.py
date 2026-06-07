import requests
import tempfile
import os
from config.settings import GROQ_API_KEY, TELEGRAM_BOT_TOKEN, GROQ_WHISPER_MODEL


class AudioService:
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

    def download_file(self, file_path: str) -> bytes:
        """Download file from Telegram"""
        try:
            url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            response = requests.get(url, timeout=30)
            return response.content
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
            return None

    def transcribe(self, file_id: str) -> str:
        """Transcribe voice note using Groq Whisper"""
        try:
            # Get file path
            file_path = self.get_file_path(file_id)
            if not file_path:
                return None

            # Download file
            audio_data = self.download_file(file_path)
            if not audio_data:
                return None

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            # Transcribe with Groq
            with open(tmp_path, "rb") as audio_file:
                response = requests.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.groq_key}"},
                    files={"file": ("voice.ogg", audio_file, "audio/ogg")},
                    data={"model": GROQ_WHISPER_MODEL},
                    timeout=60
                )

            # Cleanup temp file
            os.unlink(tmp_path)

            if response.status_code == 200:
                text = response.json().get("text", "")
                print(f"✅ Transcribed: {text}")
                return text
            else:
                print(f"❌ Transcription failed: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            return None