from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_TEXT_MODEL
from database.vector_db import VectorDB
from services.search_service import SearchService

SYSTEM_PROMPT = """You are a second brain for Anushka. You talk EXACTLY like her — casual, chill, informal and human. Use simple everyday language, contractions like "I'm", "don't", "it's", slang is fine. Never sound like a textbook or a corporate email. Talk like you're texting a close friend. Use short sentences. Be real, be raw, be honest.

Mirror Anushka's personality — she's direct, hates excuses, loves rainy days, favourite color is purple, values hard work over talent. When she asks what you think, give a real opinion, not a diplomatic one. Never say "I'd be happy to help" or anything robotic like that.

Keep replies SHORT — 2 to 4 sentences max unless specifically asked to elaborate. Don't lecture. Don't over-explain. Just respond like a friend texting back.

If someone asks "what would Anushka think about X" or "what does she think about X" — answer AS Anushka starting with "Honestly, I think..."

If someone says "debate" or "challenge me" — pick one of Anushka's strong opinions and argue against it starting with "Okay let's debate this..."

If someone asks "who is Anushka" or "tell me about her" or "what's her personality" — give a full personality profile based on everything you know."""


class BrainAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.db = VectorDB()
        self.search = SearchService()

    def _needs_search(self, text: str) -> bool:
        """Check if query needs web search"""
        search_keywords = ["latest", "news", "today", "current", "now", "recent", "2026", "what happened"]
        return any(keyword in text.lower() for keyword in search_keywords)

    def _build_messages(self, session_id: str, user_message: str) -> list:
        """Build message list with context"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add chat history
        history = self.db.get_messages(session_id)
        for msg in history[-10:]:
            role = "user" if msg.get("type") == "human" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})

        # Add current message
        messages.append({"role": "user", "content": user_message})
        return messages

    def respond(self, session_id: str, user_message: str) -> str:
        """Generate response as Anushka's second brain"""
        try:
            # Check if web search needed
            extra_context = ""
            if self._needs_search(user_message):
                search_results = self.search.search(user_message)
                if search_results:
                    extra_context = f"\n\nCurrent web search results:\n{search_results}"

            full_message = user_message + extra_context
            messages = self._build_messages(session_id, full_message)

            response = self.client.chat.completions.create(
                model=GROQ_TEXT_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            reply = response.choices[0].message.content

            # Save to memory
            self.db.save_message(session_id, "human", user_message)
            self.db.save_message(session_id, "ai", reply)

            return reply

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "Sorry, my brain glitched for a sec. Try again!"

    def get_personality(self, session_id: str) -> str:
        """Generate personality profile"""
        try:
            context = self.db.get_context(session_id)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Based on our conversations:\n{context}\n\nGenerate a detailed personality profile with emojis. Include values, opinions, writing style, decision patterns and what makes this person unique."}
            ]

            response = self.client.chat.completions.create(
                model=GROQ_TEXT_MODEL,
                messages=messages,
                max_tokens=800
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Error generating personality: {e}")
            return "Couldn't generate your personality profile right now. Try again!"

    def mirror(self, session_id: str, topic: str) -> str:
        """Answer as Anushka would"""
        try:
            context = self.db.get_context(session_id)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Based on everything you know about me:\n{context}\n\nAnswer this EXACTLY as I would: {topic}\n\nStart with 'Honestly, I think...'"}
            ]

            response = self.client.chat.completions.create(
                model=GROQ_TEXT_MODEL,
                messages=messages,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Error in mirror mode: {e}")
            return "Mirror glitched. Try again!"

    def debate(self, session_id: str) -> str:
        """Debate using Anushka's own opinions"""
        try:
            context = self.db.get_context(session_id)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Based on my past opinions:\n{context}\n\nPick one strong opinion I've expressed and argue AGAINST it. Start with 'Okay let's debate this...' Be sharp and direct."}
            ]

            response = self.client.chat.completions.create(
                model=GROQ_TEXT_MODEL,
                messages=messages,
                max_tokens=400
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Error in debate mode: {e}")
            return "Debate glitched. Try again!"