import requests
import json

class RemoteLogger:
    def __init__(self, token: str):
        self.api_url = "http://localhost:3000/api/youx/logs"
        self.token = token

    def log(self, message: str, level: str = "info"):
        try:
            payload = {
                "token": self.token,
                "message": message,
                "level": level
            }
            requests.post(self.api_url, json=payload, timeout=5)
            print(f"[CLOUD-LOG] Sent: {message}")
        except Exception as e:
            print(f"[CLOUD-LOG] Failed to send: {e}")
