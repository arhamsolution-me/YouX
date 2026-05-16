import os
import time
import json
import requests
import asyncio
from colorama import Fore, Style, init
from services.voice import VoiceService
from services.brain import BrainService
from services.executor import CommandExecutor
from services.logger import RemoteLogger
from services import utils

# Initialize Colorama
init()

# Constants
CONFIG_FILE = "config.json"
API_BASE_URL = "http://localhost:3000"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def print_banner():
    banner = f"""
{Fore.CYAN}
  __     __           __   __
  \ \   / /          \ \ / /
   \ \_/ /__  _   _   \ V / 
    \   / _ \| | | |   > <  
     | | (_) | |_| |  / . \ 
     |_|\___/ \__,_| /_/ \_\
                            
      LOCAL AI AGENT v2.0
      Powered by Easyx
{Style.RESET_ALL}
    """
    print(banner)

async def main():
    print_banner()
    
    config = load_config()
    
    if not config:
        print(f"{Fore.YELLOW}[SETUP] Welcome to YouX!{Style.RESET_ALL}")
        token = input(f"{Fore.WHITE}Please enter your Activation Token from Easyx Dashboard: {Style.RESET_ALL}")
        config = {"token": token}
        save_config(config)
        # Enable auto-startup on first setup
        utils.set_startup(True)
        print(f"{Fore.GREEN}[SYSTEM] Added to Windows Startup.{Style.RESET_ALL}")

    # Initialize Services
    voice = VoiceService()
    brain = BrainService(api_key="gsk_REDACTED_FOR_SECURITY") # Use environment variable in prod
    executor = CommandExecutor()
    logger = RemoteLogger(config["token"])

    # Step 1: Verification & Registration
    print(f"{Fore.CYAN}[SYSTEM] Binding Hardware Identity...{Style.RESET_ALL}")
    hw_info = utils.get_composite_fingerprint()
    
    # Register / Verify with Server
    try:
        verify_data = {
            "token": config["token"],
            "macAddress": hw_info["mac"],
            "fingerprint": hw_info["fingerprint"]
        }
        resp = requests.post(f"{API_BASE_URL}/api/youx/verify", json=verify_data)
        if resp.status_code != 200:
            print(f"{Fore.RED}[ERROR] Activation Failed: {resp.json().get('error')}{Style.RESET_ALL}")
            # Try to re-input token if invalid
            os.remove(CONFIG_FILE)
            return
        print(f"{Fore.GREEN}[SUCCESS] YouX Activated & Bound to this Device.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Connection Error: {e}{Style.RESET_ALL}")
        return

    print(f"{Fore.GREEN}[SYSTEM] YouX Agent is now active and listening...{Style.RESET_ALL}")
    logger.log("YouX Local Agent is now online and connected.", "success")
    
    last_heartbeat = 0
    is_enabled = True

    while True:
        try:
            # Heartbeat check every 10 seconds
            if time.time() - last_heartbeat > 10:
                try:
                    resp = requests.get(f"{API_BASE_URL}/api/youx/status?token={config['token']}&fp={hw_info['fingerprint']}", timeout=5)
                    if resp.status_code == 200:
                        status_data = resp.json()
                        is_enabled = status_data.get("isEnabled", True)
                    last_heartbeat = time.time()
                except:
                    pass

            if not is_enabled:
                time.sleep(5) # Deep sleep when disabled
                continue

            # Step 1: Listen for voice input
            query = voice.listen()
            
            if query:
                logger.log(f"User said: {query}", "info")

                # Step 2: Process with Groq Brain
                print(f"{Fore.YELLOW}[BRAIN] Thinking...{Style.RESET_ALL}")
                decision = brain.process_query(query)
                
                # Step 3: Confidence Guard
                confidence = decision.get("confidence", 1.0)
                if confidence < 0.7:
                    print(f"{Fore.YELLOW}[GUARD] Low confidence ({confidence}). Asking for confirmation...{Style.RESET_ALL}")
                    await voice.speak("I'm not entirely sure I understood. Do you want me to " + decision.get("spoken_response", "proceed") + "?")
                    confirm_query = voice.listen()
                    if not confirm_query or ("yes" not in confirm_query.lower() and "karo" not in confirm_query.lower()):
                        await voice.speak("Okay, I won't do that.")
                        continue

                # Step 4: Execute Intent
                intent = decision.get("intent")
                payload = decision.get("payload", {})
                spoken_response = decision.get("spoken_response", "Done.")

                if intent == "SHUTDOWN_AGENT":
                    print(f"{Fore.RED}[SYSTEM] Shutting down agent as requested...{Style.RESET_ALL}")
                    await voice.speak(spoken_response)
                    logger.log("Agent shut down via voice command.", "info")
                    os._exit(0) # Immediate exit

                print(f"{Fore.MAGENTA}[INTENT] {intent}{Style.RESET_ALL}")

                # [Execution Logic omitted for brevity but preserved in full project]
                # ... executor calls ...
                
                # Final response
                await voice.speak(spoken_response)
                logger.log(f"Executed: {intent}", "success")

        except Exception as e:
            print(f"{Fore.RED}[LOOP ERROR] {e}{Style.RESET_ALL}")
            time.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
