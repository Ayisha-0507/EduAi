import requests
import json
import os
from datetime import datetime
import random

# --- CONFIGURATION ---
KEYS_FILE = "gemini_keys.json"
DAILY_LIMIT_PER_KEY = 1500
# ---------------------

class GeminiRotator:
    def __init__(self, keys_file=KEYS_FILE, daily_limit=DAILY_LIMIT_PER_KEY):
        self.keys_file = keys_file
        self.daily_limit = daily_limit
        self.keys_data = self._load_keys()
        self._check_for_keys()

    def _load_keys(self):
        if not os.path.exists(self.keys_file):
            return {"keys": []}
        with open(self.keys_file, "r") as f:
            return json.load(f)

    def _save_keys(self):
        with open(self.keys_file, "w") as f:
            json.dump(self.keys_data, f, indent=2)

    def _check_for_keys(self):
        if not self.keys_data.get("keys"):
            raise FileNotFoundError(
                f"No API keys found in '{self.keys_file}'. "
                "Please add your Google AI Studio keys to this file."
            )

    def _reset_daily_usage(self):
        today_str = datetime.now().strftime('%Y-%m-%d')
        last_reset = self.keys_data.get("last_global_reset_date")
        if last_reset != today_str:
            print(f"New day detected! Resetting usage for all keys.")
            for key_info in self.keys_data["keys"]:
                key_info["requests_today"] = 0
            self.keys_data["last_global_reset_date"] = today_str
            self._save_keys()

    def _get_next_available_key(self):
        self._reset_daily_usage()
        available_keys = [
            key_info for key_info in self.keys_data["keys"] 
            if key_info.get("requests_today", 0) < self.daily_limit
        ]
        if not available_keys:
            raise Exception(
                f"All {len(self.keys_data['keys'])} Gemini keys have reached their daily limit of {self.daily_limit} requests."
            )
        chosen_key_info = random.choice(available_keys)
        return chosen_key_info

    def generate_content(self, model_name, prompt):
        key_info = self._get_next_available_key()
        api_key = key_info["key"]
        
        # Using the official OpenAI-compatible endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/openai/chat/completions?key={api_key}"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        # --- IMPROVED PAYLOAD ---
        # Explicitly define the message structure. This is more robust.
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        print(f"Making request with key ...{api_key[-10:]} to model '{model_name}'")
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            # --- IMPROVED ERROR LOGGING ---
            # This will print the exact error from Google's API
            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                print(f"Response Body: {response.text}") # This is the key to debugging
            
            response.raise_for_status() # This will raise an exception if the status code is 4xx or 5xx
            
            # On success, increment the usage for the key
            key_info["requests_today"] += 1
            self._save_keys()
            
            return response.json()

        except requests.exceptions.RequestException as e:
            # The improved logging above will likely give you the details before this point
            print(f"API request failed: {e}")
            return None