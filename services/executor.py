import os
import subprocess
import platform
import webbrowser
import logging
import keyboard
from AppOpener import open as appopen, close as appclose

logger = logging.getLogger("YouX-Executor")

class SystemExecutor:
    def __init__(self):
        pass

    def open_app(self, app_name: str):
        try:
            print(f"[EXECUTOR] Opening {app_name}...")
            appopen(app_name, match_closest=True, output=False)
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error opening app: {e}")
            return False

    def close_app(self, app_name: str):
        try:
            print(f"[EXECUTOR] Closing {app_name}...")
            appclose(app_name, match_closest=True, output=False)
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error closing app: {e}")
            return False

    def control_system(self, action: str):
        try:
            if "mute" in action.lower():
                keyboard.press_and_release("volume mute")
            elif "volume up" in action.lower():
                keyboard.press_and_release("volume up")
            elif "volume down" in action.lower():
                keyboard.press_and_release("volume down")
            elif "lock" in action.lower():
                if platform.system() == "Windows":
                    os.system("rundll32.exe user32.dll,LockWorkStation")
            return True
        except Exception as e:
            print(f"[EXECUTOR] System command failed: {e}")
            return False

    def open_url(self, url: str):
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[EXECUTOR] Browser error: {e}")
            return False
