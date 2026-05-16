import os
import sys
import time
import json
import requests
from colorama import init, Fore, Style

# Initialize colorama for beautiful terminal output
init()

VERSION = "1.0.0"
API_BASE_URL = "http://localhost:3000" # Change to production URL later

def print_banner():
    banner = f"""
{Fore.CYAN}  __     __           __   __
  \ \   / /          \ \ / /
   \ \_/ /__  _   _   \ V / 
    \   / _ \| | | |   > <  
     | | (_) | |_| |  / . \ 
     |_|\___/ \__,_| /_/ \_\ 
                            
{Fore.WHITE}   YOUX LOCAL AGENT v{VERSION}
{Fore.BLUE}   =========================
{Style.RESET_ALL}"""
    print(banner)

from services.utils import get_mac_address, hide_console

def setup():
    print(f"{Fore.YELLOW}[SETUP] Initializing YouX Local Brain...{Style.RESET_ALL}")
    
    # Check for existing config
    if os.path.exists(".env.json"):
        with open(".env.json", "r") as f:
            try:
                config = json.load(f)
                return config
            except:
                pass

    mac = get_mac_address()

    # Loop until verified
    while True:
        # Ask for Master Key (New Security Layer)
        master_key = input(f"{Fore.MAGENTA}❯ Enter Master Access Key: {Style.RESET_ALL}").strip()
        
        # Ask for Activation Token
        token = input(f"{Fore.CYAN}❯ Enter Activation Token from TitanX Dashboard: {Style.RESET_ALL}").strip()
        
        # Verify Token with Web API
        print(f"{Fore.YELLOW}[SETUP] Verifying identity...{Style.RESET_ALL}")
        try:
            resp = requests.post(f"{API_BASE_URL}/api/youx/verify", json={
                "token": token,
                "macAddress": mac,
                "masterKey": master_key
            })
            if resp.status_code == 200:
                data = resp.json()
                print(f"{Fore.GREEN}✓ Identity Verified: {data['user']['fullName']} ({data['tenant']['name']}){Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}✗ {resp.json().get('error', 'Verification Failed')}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Connection Error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Retrying in 5 seconds...{Style.RESET_ALL}")
            time.sleep(5)

    # Ask for Groq API Key
    while True:
        groq_key = input(f"{Fore.CYAN}❯ Enter your Groq API Key: {Style.RESET_ALL}").strip()
        if groq_key.startswith("gsk_") and len(groq_key) > 20:
            break
        else:
            print(f"{Fore.RED}✗ Invalid Groq Key format. It should start with 'gsk_'.{Style.RESET_ALL}")
    
    config = {
        "token": token,
        "groq_api_key": groq_key,
        "user_id": data['user']['id'],
        "tenant_id": data['tenant']['id']
    }

    with open(".env.json", "w") as f:
        json.dump(config, f)
    
    print(f"{Fore.GREEN}✓ Configuration saved successfully!{Style.RESET_ALL}")
    return config

import asyncio
from services.voice import VoiceService
from services.brain import BrainService
from services.executor import SystemExecutor
from services.logger import CloudLogger

def main_loop(config):
    voice = VoiceService()
    brain = BrainService(config["groq_api_key"])
    executor = SystemExecutor()
    logger = CloudLogger(API_BASE_URL, config["token"])

    print(f"{Fore.GREEN}[SYSTEM] YouX Agent is now active and listening...{Style.RESET_ALL}")
    logger.log("YouX Local Agent is now online and connected.", "success")
    
    last_heartbeat = 0
    is_enabled = True

    while True:
        try:
            # Heartbeat check every 10 seconds
            if time.time() - last_heartbeat > 10:
                try:
                    resp = requests.get(f"{API_BASE_URL}/api/youx/status?token={config['token']}", timeout=5)
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
                
                # Step 3: Execute Intent
                intent = decision.get("intent")
                payload = decision.get("payload", {})
                spoken_response = decision.get("spoken_response", "Done.")

                print(f"{Fore.MAGENTA}[INTENT] {intent}{Style.RESET_ALL}")

                if intent == "OPEN_APP":
                    app = payload.get("app_name")
                    if executor.open_app(app):
                        logger.log(f"Successfully opened application: {app}", "success")
                elif intent == "CLOSE_APP":
                    app = payload.get("app_name")
                    if executor.close_app(app):
                        logger.log(f"Closed application: {app}", "info")
                elif intent == "SYSTEM_CONTROL":
                    action = payload.get("action")
                    if executor.control_system(action):
                        logger.log(f"System control executed: {action}", "warning")
                elif intent == "OPEN_URL":
                    url = payload.get("url")
                    if executor.open_url(url):
                        logger.log(f"Opened URL in browser: {url}", "info")
                elif intent == "GOOGLE_SEARCH":
                    q = payload.get("query")
                    if executor.google_search(q):
                        logger.log(f"Searching Google for: {q}", "info")
                elif intent == "YOUTUBE_SEARCH":
                    q = payload.get("query")
                    if executor.youtube_search(q):
                        logger.log(f"Searching YouTube for: {q}", "info")
                elif intent == "PLAY_MUSIC":
                    q = payload.get("query")
                    if executor.play_on_youtube(q):
                        logger.log(f"Playing on YouTube: {q}", "success")

                # Step 4: Speak Response
                asyncio.run(voice.speak(spoken_response))

            time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[SYSTEM] Shutting down YouX Agent...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    print_banner()
    config = setup()
    
    # Hide console and run in background after successful setup
    if "--no-hide" not in sys.argv:
        hide_console()
        
    main_loop(config)
