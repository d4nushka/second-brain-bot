import asyncio
import json
import logging
from aiohttp import web
from config.settings import TELEGRAM_BOT_TOKEN
from agents.brain import BrainAgent
from services.telegram_service import TelegramService
from services.audio_service import AudioService
from services.image_service import ImageService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
brain = BrainAgent()
telegram = TelegramService()
audio = AudioService()
image = ImageService()

START_MESSAGE = """🧬 Hey! I'm your Second Brain Mirror Bot.

I'm going to learn to think EXACTLY like you. Let's start!

Tell me:
👤 What's your name?
💼 What do you do?
❤️ What are you passionate about?
😤 What drives you crazy?
🌧️ What makes you happy?

Just reply naturally — the more real you are, the better I'll mirror you! 🧠

Commands:
/mirror [topic] — What would YOU think about X?
/debate — I'll challenge you with your own opinions
/personality — See your personality profile"""


async def handle_update(request):
    """Handle incoming Telegram webhook"""
    try:
        data = await request.json()
        message = data.get("message", {})

        if not message:
            return web.Response(text="ok")

        chat_id = message.get("chat", {}).get("id")
        user_text = message.get("text", "")
        voice = message.get("voice")
        photo = message.get("photo")
        session_id = str(chat_id)

        if not chat_id:
            return web.Response(text="ok")

        # Send typing indicator
        telegram.send_typing(chat_id)

        # Handle commands
        if user_text.startswith("/start"):
            telegram.send_message(chat_id, START_MESSAGE)

        elif user_text.startswith("/mirror"):
            topic = user_text.replace("/mirror", "").strip()
            if not topic:
                telegram.send_message(chat_id, "Tell me what topic! e.g. /mirror social media")
            else:
                reply = brain.mirror(session_id, topic)
                telegram.send_message(chat_id, reply)

        elif user_text.startswith("/debate"):
            reply = brain.debate(session_id)
            telegram.send_message(chat_id, reply)

        elif user_text.startswith("/personality"):
            reply = brain.get_personality(session_id)
            telegram.send_message(chat_id, reply)

        # Handle voice notes
        elif voice:
            file_id = voice.get("file_id")
            telegram.send_message(chat_id, "🎙️ Transcribing your voice note...")
            transcribed = audio.transcribe(file_id)
            if transcribed:
                reply = brain.respond(session_id, transcribed)
                telegram.send_message(chat_id, reply)
            else:
                telegram.send_message(chat_id, "Couldn't transcribe that. Try again!")

        # Handle images
        elif photo:
            file_id = photo[-1].get("file_id")
            telegram.send_message(chat_id, "🖼️ Analyzing your image...")
            description = image.analyze(file_id)
            if description:
                reply = brain.respond(session_id, f"I sent you an image. Here's what's in it: {description}")
                telegram.send_message(chat_id, reply)
            else:
                telegram.send_message(chat_id, "Couldn't analyze that image. Try again!")

        # Handle text messages
        elif user_text:
            reply = brain.respond(session_id, user_text)
            telegram.send_message(chat_id, reply)

        return web.Response(text="ok")

    except Exception as e:
        logger.error(f"Error handling update: {e}")
        return web.Response(text="ok")


async def health_check(request):
    return web.Response(text="Second Brain Bot is running! 🧠")


async def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_update)
    app.router.add_get("/", health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("🚀 Second Brain Bot is running on port 8080!")
    print("📡 Waiting for messages...")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())