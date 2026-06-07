import json
from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_KEY, MEMORY_TABLE
from datetime import datetime


class VectorDB:
    def __init__(self):
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Supabase connected successfully")
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            self.client = None

    def save_message(self, session_id: str, role: str, content: str):
        """Save a message to the chat history"""
        try:
            if not self.client:
                return False
            
            # Get existing messages
            existing = self.get_messages(session_id)
            existing.append({"type": role, "content": content})
            
            # Check if session exists
            result = self.client.table(MEMORY_TABLE)\
                .select("*")\
                .eq("session_id", session_id)\
                .execute()
            
            if result.data:
                # Update existing
                self.client.table(MEMORY_TABLE)\
                    .update({"message": json.dumps(existing)})\
                    .eq("session_id", session_id)\
                    .execute()
            else:
                # Insert new
                self.client.table(MEMORY_TABLE)\
                    .insert({
                        "session_id": session_id,
                        "message": json.dumps(existing)
                    })\
                    .execute()
            return True
        except Exception as e:
            print(f"❌ Error saving message: {e}")
            return False

    def get_messages(self, session_id: str) -> list:
        """Get chat history for a session"""
        try:
            if not self.client:
                return []
            
            result = self.client.table(MEMORY_TABLE)\
                .select("message")\
                .eq("session_id", session_id)\
                .execute()
            
            if result.data:
                data = result.data[0]["message"]
                if isinstance(data, str):
                   return json.loads(data)
                return data if isinstance(data, list) else []
            return []
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []

    def get_context(self, session_id: str, limit: int = 10) -> str:
        """Get formatted context string from chat history"""
        try:
            messages = self.get_messages(session_id)
            recent = messages[-limit:] if len(messages) > limit else messages
            
            context = ""
            for msg in recent:
                role = "User" if msg.get("type") == "human" else "Assistant"
                context += f"{role}: {msg.get('content', '')}\n"
            return context
        except Exception as e:
            print(f"❌ Error getting context: {e}")
            return ""