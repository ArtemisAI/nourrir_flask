# nourrir_flask/config.py
import os

# Primary LLM (Ollama)
OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://192.168.2.10:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:latest")

# Fallback LLM (Gemini)
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCm3-_I6KU3kfB3AwWK2YQ9FyG0lxQRQ5Y")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_KEY}"

# Networking
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "8"))  # seconds
LOG_FILE = os.getenv("LOG_FILE", "nurih_app.log")
