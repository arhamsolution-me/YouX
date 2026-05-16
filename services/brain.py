import json
import os
from groq import Groq
from services.memory import MemoryService

class BrainService:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.memory = MemoryService()
        self.model = "llama-3.3-70b-versatile"

    def process_query(self, query):
        # Get context from local memory
        history = self.memory.get_recent_history(limit=5)
        
        # Build contextual prompt
        system_prompt = """
        You are YouX, an advanced AI Assistant powered by Easyx. 
        You control the user's computer based on their voice commands.
        
        Analyze the query and history, then return ONLY a JSON object with:
        - intent: (OPEN_APP, CLOSE_APP, SEARCH_WEB, SYSTEM_CONTROL, MUSIC_CONTROL, CHAT, SCREENSHOT, RECYCLE_BIN, BATTERY_STATUS, SHUTDOWN_AGENT)
        - payload: dict containing needed data (e.g., app_name, search_query, action)
        - spoken_response: what to say to the user
        - confidence: (0.0 to 1.0) - How sure you are about this intent.
        
        Example: {"intent": "OPEN_APP", "payload": {"app_name": "chrome"}, "spoken_response": "Opening Chrome for you.", "confidence": 0.95}
        """

        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
        
        messages.append({"role": "user", "content": query})

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                response_format={"type": "json_object"}
            )
            
            response_json = json.loads(chat_completion.choices[0].message.content)
            
            # Save user query and AI response to memory
            self.memory.add_chat("user", query)
            self.memory.add_chat("assistant", response_json.get("spoken_response", ""))
            
            return response_json
        except Exception as e:
            print(f"[BRAIN ERROR] {e}")
            # Basic fallback
            return {
                "intent": "CHAT", 
                "payload": {}, 
                "spoken_response": "I'm having trouble thinking right now. Please try again.",
                "confidence": 0.1
            }
