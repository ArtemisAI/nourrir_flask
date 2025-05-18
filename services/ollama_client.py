import json
import logging
import requests
from config import OLLAMA_URL, OLLAMA_MODEL, REQUEST_TIMEOUT


class OllamaClient:
    """
    Client for interacting with a local Ollama chat model.
    Supports both single-response and streaming mode.
    """
    def __init__(self,
                 url: str = OLLAMA_URL,
                 model: str = OLLAMA_MODEL,
                 timeout: float = REQUEST_TIMEOUT):
        self.url = url
        self.model = model
        self.timeout = timeout
        self.system_prompt = (
            "Tu es NuRiH Ami, assistant éducatif pour le bien-être, nutrition et créativité. "
            "Sois amical, inclusif, bref et adapté à tous publics."
        )

    def ask(self, user_msg: str, stream: bool = False):
        """
        Send a user message to Ollama and return its response.

        :param user_msg: The message from the user.
        :param stream:  If True, yield chunks as they arrive; otherwise, return full response.
        :returns:      A string reply if stream is False, else a generator yielding response chunks.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_msg}
            ],
            "stream": stream
        }

        logging.info("→ Ollama request: %s", payload)

        try:
            response = requests.post(self.url,
                                     json=payload,
                                     timeout=self.timeout,
                                     stream=stream)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error("Ollama request failed: %s", e)
            raise

        if stream:
            return self._stream_response(response)
        else:
            data = response.json()
            content = data.get("message", {}).get("content", "").strip()
            logging.info("← Ollama response received (length=%d)", len(content))
            return content

    def _stream_response(self, response):
        """
        Internal helper to stream response lines from Ollama.
        Yields text chunks as they arrive.
        """
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                part = json.loads(line)
                chunk = part.get("message", {}).get("content", "")
                if chunk:
                    yield chunk
            except json.JSONDecodeError:
                logging.warning("Failed to parse stream chunk: %r", line)
                continue


# module-level convenience
_client = OllamaClient()


def ask_ollama(user_msg: str) -> str:
    """
    Simple helper: ask Ollama for a single response.
    """
    return _client.ask(user_msg, stream=False)


def stream_ollama(user_msg: str):
    """
    Simple helper: ask Ollama and get a streaming response generator.
    """
    return _client.ask(user_msg, stream=True)

__all__ = ["OllamaClient", "ask_ollama", "stream_ollama"]
