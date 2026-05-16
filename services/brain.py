import json
from groq import Groq

class BrainService:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.system_prompt = """
        You are YouX, a powerful local system agent. 
        You can control the user's computer.
        Your goal is to parse user intent and return a JSON response.
        
        SUPPORTED INTENTS:
        - OPEN_APP (payload: {app_name: str})
        - CLOSE_APP (payload: {app_name: str})
        - SYSTEM_CONTROL (payload: {action: "mute" | "volume up" | "volume down" | "lock"})
        - OPEN_URL (payload: {url: str})
        - CHAT (payload: {answer: str})
        
        RESPONSE FORMAT:
        Return ONLY a JSON object:
        {
            "intent": "INTENT_NAME",
            "payload": { ... },
            "spoken_response": "What you will say to the user"
        }
        """

    def process_query(self, query: str):
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(f"[BRAIN] Error: {e}")
            return {
                "intent": "CHAT",
                "payload": {"answer": "I'm having trouble thinking right now."},
                "spoken_response": "Sorry, I encountered an error in my brain."
            }
