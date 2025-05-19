# nourrir_flask/services/chat_service.py
import logging
from .n8n_client import ask_n8n
from .ollama_client import ask_ollama
from .gemini_client import ask_gemini

def get_reply(user_msg: str) -> str:
    """Try n8n; fallback to Ollama; fallback to Gemini; final fallback message."""
    try:
        return ask_n8n(user_msg)
    except Exception as e:
        logging.error(f"n8n error → {e}")
    try:
        return ask_ollama(user_msg)
    except Exception as e:
        logging.error(f"Ollama error → {e}")
        try:
            return ask_gemini(user_msg)
        except Exception as e2:
            logging.critical(f"Gemini error → {e2}")
            return "Désolé, je rencontre des difficultés techniques. Merci de réessayer plus tard."
