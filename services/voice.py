import os
import asyncio
import edge_tts
import speech_recognition as sr
import pygame
import time

class VoiceService:
    def __init__(self, voice="en-US-AriaNeural"):
        self.voice = voice
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        pygame.mixer.init()
        self._setup_done = False

    async def speak(self, text: str):
        print(f"[VOICE] YouX: {text}")
        output_file = "response.mp3"
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)
        
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        pygame.mixer.music.unload()
        if os.path.exists(output_file):
            os.remove(output_file)

    def listen(self):
        with sr.Microphone() as source:
            if not self._setup_done:
                print("[VOICE] Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self._setup_done = True
            
            print("[VOICE] Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                text = self.recognizer.recognize_google(audio)
                print(f"[VOICE] You: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                print(f"[VOICE] Error: {e}")
                return None

    def play_wake_sound(self):
        # Optional: play a small beep when listening starts
        pass
