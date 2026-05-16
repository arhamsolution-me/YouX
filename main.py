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

def setup():
    print(f"{Fore.YELLOW}[SETUP] Initializing YouX Local Brain...{Style.RESET_ALL}")
    
    # Check for existing config
    if os.path.exists(".env.json"):
        with open(".env.json", "r") as f:
            config = json.load(f)
            return config

    # Ask for Activation Token
    token = input(f"{Fore.CYAN}❯ Enter Activation Token from TitanX Dashboard: {Style.RESET_ALL}").strip()
    
    # Verify Token with Web API
    print(f"{Fore.YELLOW}[SETUP] Verifying identity...{Style.RESET_ALL}")
    try:
        resp = requests.post(f"{API_BASE_URL}/api/youx/verify", json={"token": token})
        if resp.status_code == 200:
            data = resp.json()
            print(f"{Fore.GREEN}✓ Identity Verified: {data['user']['fullName']} ({data['tenant']['name']}){Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Verification Failed: {resp.json().get('error', 'Unknown error')}{Style.RESET_ALL}")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}✗ Connection Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # Ask for Groq API Key
    groq_key = input(f"{Fore.CYAN}❯ Enter your Groq API Key: {Style.RESET_ALL}").strip()
    
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

def main_loop(config):
    voice = VoiceService()
    brain = BrainService(config["groq_api_key"])
    executor = SystemExecutor()

    print(f"{Fore.GREEN}[SYSTEM] YouX Agent is now active and listening...{Style.RESET_ALL}")
    
    while True:
        try:
            # Step 1: Listen for voice input
            query = voice.listen()
            
            if query:
                # Step 2: Process with Groq Brain
                print(f"{Fore.YELLOW}[BRAIN] Thinking...{Style.RESET_ALL}")
                decision = brain.process_query(query)
                
                # Step 3: Execute Intent
                intent = decision.get("intent")
                payload = decision.get("payload", {})
                spoken_response = decision.get("spoken_response", "Done.")

                print(f"{Fore.MAGENTA}[INTENT] {intent}{Style.RESET_ALL}")

                if intent == "OPEN_APP":
                    executor.open_app(payload.get("app_name"))
                elif intent == "CLOSE_APP":
                    executor.close_app(payload.get("app_name"))
                elif intent == "SYSTEM_CONTROL":
                    executor.control_system(payload.get("action"))
                elif intent == "OPEN_URL":
                    executor.open_url(payload.get("url"))

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
    main_loop(config)
