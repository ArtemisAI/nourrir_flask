import logging
import requests
from config import GEMINI_URL, REQUEST_TIMEOUT

def ask_gemini(user_msg: str) -> str:
    """
    Send a user message to Google's Gemini API and return the first candidate's output.
    """
    payload = {
        "prompt": {
            "text": user_msg
        }
    }
    logging.info("→ Gemini request: %s", payload)
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No response candidates from Gemini API")
        content = candidates[0].get("output", "").strip()
        logging.info("← Gemini response received (length=%d)", len(content))
        return content
    except requests.RequestException as e:
        logging.error("Gemini request failed: %s", e)
        raise

__all__ = ["ask_gemini"]