import os
import subprocess
import webbrowser
from urllib.parse import quote

class SystemExecutor:
    def __init__(self):
        self.apps = {
            "chrome": "chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "spotify": "spotify.exe"
        }

    def open_app(self, app_name: str) -> bool:
        try:
            app_exe = self.apps.get(app_name.lower(), app_name.lower())
            subprocess.Popen(app_exe, shell=True)
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error opening app: {e}")
            return False

    def close_app(self, app_name: str) -> bool:
        try:
            app_exe = self.apps.get(app_name.lower(), app_name.lower())
            if not app_exe.endswith(".exe"):
                app_exe += ".exe"
            os.system(f"taskkill /f /im {app_exe}")
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error closing app: {e}")
            return False

    def open_url(self, url: str) -> bool:
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error opening URL: {e}")
            return False

    def google_search(self, query: str) -> bool:
        try:
            url = f"https://www.google.com/search?q={quote(query)}"
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error searching Google: {e}")
            return False

    def youtube_search(self, query: str) -> bool:
        try:
            url = f"https://www.youtube.com/results?search_query={quote(query)}"
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error searching YouTube: {e}")
            return False

    def play_on_youtube(self, query: str) -> bool:
        try:
            # First try with pywhatkit if available, fallback to search results
            try:
                import pywhatkit
                pywhatkit.playonyt(query)
            except ImportError:
                url = f"https://www.youtube.com/results?search_query={quote(query)}"
                webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error playing on YouTube: {e}")
            return False

    def control_system(self, action: str) -> bool:
        try:
            import keyboard
            import os
            import pyautogui
            import psutil
            
            action = action.lower()
            if "mute" in action:
                keyboard.press_and_release("volume mute")
            elif "up" in action or "increase" in action:
                keyboard.press_and_release("volume up")
            elif "down" in action or "decrease" in action:
                keyboard.press_and_release("volume down")
            elif "lock" in action:
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif "screenshot" in action:
                os.makedirs("screenshots", exist_ok=True)
                path = f"screenshots/screenshot.png"
                pyautogui.screenshot(path)
                return f"Screenshot saved at {path}"
            elif "recycle" in action or "clean bin" in action:
                os.system("rd /s /q %systemdrive%\\$Recycle.Bin")
                return "Recycle bin emptied."
            elif "battery" in action:
                battery = psutil.sensors_battery()
                return f"Your battery is at {battery.percent}%"
            
            return True
        except Exception as e:
            print(f"[EXECUTOR] Error controlling system: {e}")
            return False
