# nourrir_flask/services/chat_service.py
import logging
from .ollama_client import ask_ollama
from .gemini_client import ask_gemini

def get_reply(user_msg: str) -> str:
    """Try Ollama; fallback to Gemini; final fallback message if both fail."""
    try:
        return ask_ollama(user_msg)
    except Exception as e:
        logging.error(f"Ollama error → {e}")
        try:
            return ask_gemini(user_msg)
        except Exception as e2:
            logging.critical(f"Gemini error → {e2}")
            return "Désolé, je rencontre des difficultés techniques. Merci de réessayer plus tard."
