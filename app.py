"""
NourrIR Flask Application
=========================

This Flask application serves as the backend for the NourrIR project,
providing routes for static pages, chatbot interactions via Ollama,
and other API endpoints.

It includes:
- Basic HTML page rendering.
- A proxy for Ollama chat completions (`/nurih-ami`).
- An endpoint to list available Ollama models (`/models`).
- Specific chatbot UIs for HR and testing n8n webhooks.
- Comprehensive logging and error handling.
"""
# nourrir_flask/app.py

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import requests
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # Log to console
        # You could add logging.FileHandler("app.log") here as well
    ]
)
logger = logging.getLogger(__name__)

## Configuration for Ollama chat API endpoints
# For OpenAI-compatible API (v1): default to Artemis AI hosted Ollama instance.
# Can override via environment variables.
OLLAMA_CHAT_URL = os.getenv(
    "OLLAMA_CHAT_URL",
    os.getenv("OLLAMA_URL", "https://ollama.artemis-ai.ca/v1/chat/completions")
)
OLLAMA_MODELS_URL = os.getenv(
    "OLLAMA_MODELS_URL",
    os.getenv("MODELS_URL", "https://ollama.artemis-ai.ca/v1/models")
)
# Primary model to use; fallback to smaller or next available models on failure.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

# Log the final determined Ollama configuration
logger.info(f"Using Ollama Chat URL: {OLLAMA_CHAT_URL}")
logger.info(f"Using Ollama Models URL: {OLLAMA_MODELS_URL}")
logger.info(f"Using Default Ollama Model: {OLLAMA_MODEL}")

# --- n8n Configuration ---
# Primary n8n webhook for the HR assistant (raw webhook). Can be overridden via env var.
N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "https://n8n.artemis-ai.ca:8443/webhook/3856912a-4b68-441b-ba1a-beb4e64356e0"
)

# Secondary n8n webhook: Chat Trigger endpoint (with /chat suffix). Fallback if primary fails.
N8N_WEBHOOK_FALLBACK = os.getenv(
    "N8N_WEBHOOK_FALLBACK",
    "https://n8n.artemis-ai.ca:8443/webhook/865ac76c-55df-47c0-8277-7fafe74400ab/chat"
)

logger.info(f"Using n8n primary webhook: {N8N_WEBHOOK_URL}")
logger.info(f"Using n8n fallback webhook: {N8N_WEBHOOK_FALLBACK}")

# Default system prompt for NuRiH Ami
SYSTEM_PROMPT = (
    "Tu es NurrIA, une intelligence artificielle bienveillante et experte en bien-être, nutrition et créativité chez NourrIR. "
    "Sois amicale, inclusive, brève et adaptée à tous publics."
)

def query_ollama(messages: list, model: str = OLLAMA_MODEL, chat_url: str = OLLAMA_CHAT_URL, timeout: int = 60) -> str | None:
    """
    Sends messages to the Ollama chat API and returns the assistant's content.

    Args:
        messages: A list of message objects to send to Ollama.
        model: The Ollama model to use for the chat completion.
        chat_url: The URL of the Ollama chat API.
        timeout: The timeout in seconds for the request.

    Returns:
        The content of the assistant's response as a string, or None if an error occurs
        or the response structure is unexpected.
    
    Raises:
        requests.exceptions.HTTPError: If Ollama returns an HTTP error status.
        requests.exceptions.RequestException: For other network-related issues.
    """
    payload = {"model": model, "messages": messages, "stream": False}
    # Redact or summarize sensitive parts of messages if necessary before logging
    # For now, logging the full message content for debug purposes.
    logger.debug(f"Sending to Ollama ({chat_url}) with model {model}: {messages}")
    
    try:
        resp = requests.post(chat_url, json=payload, timeout=timeout)
        resp.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
        data = resp.json()
        logger.debug(f"Ollama raw response status: {resp.status_code}")
        # Log first 500 chars of response to avoid flooding logs with huge responses
        logger.debug(f"Ollama raw response data (first 500 chars): {str(data)[:500]}")

        # OpenAI-compatible response parsing
        if isinstance(data, dict) and "choices" in data:
            choices = data.get("choices", [])
            if choices and isinstance(choices[0], dict):
                msg = choices[0].get("message", {})
                content = msg.get("content")
                if content is not None:
                    logger.debug(f"Extracted content (OpenAI format): {content[:100]}...")
                    return content
        # Fallback to legacy Ollama API format
        if isinstance(data, dict) and "message" in data:
            content = data.get("message", {}).get("content", "")
            if content: # Ensure content is not empty
                logger.debug(f"Extracted content (Legacy Ollama format): {content[:100]}...")
                return content
        
        logger.warning(f"Unexpected response structure from Ollama: {data}")
        return None # Return None if no valid content found or structure is unexpected
    except requests.exceptions.HTTPError as e:
        logger.error(f"Ollama request failed with HTTPError: {e}", exc_info=True)
        logger.error(f"Ollama response content for HTTPError: {e.response.text if e.response else 'No response content'}")
        raise # Re-raise to be caught by the route's error handler
    except requests.exceptions.RequestException as e: # Catches ConnectionError, Timeout, etc.
        logger.error(f"Ollama request failed with RequestException: {e}", exc_info=True)
        raise # Re-raise
    except Exception as e: # Catch any other unexpected errors, e.g., JSONDecodeError
        logger.error(f"An unexpected error occurred in query_ollama: {e}", exc_info=True)
        raise # Re-raise

def get_response_with_fallback(messages: list,
                               chat_url: str = OLLAMA_CHAT_URL,
                               models_url: str = OLLAMA_MODELS_URL,
                               initial_model: str = OLLAMA_MODEL,
                               timeout: int = 60) -> str | None:
    """
    Attempt to get a response using the initial model, then fallback through available models if needed.
    """
    try:
        resp = query_ollama(messages, model=initial_model, chat_url=chat_url, timeout=timeout)
        if resp:
            return resp
        logger.warning(f"Primary model '{initial_model}' returned no content, falling back.")
    except Exception as e:
        logger.warning(f"Primary model '{initial_model}' failed: {e}")

    # Fetch available models for fallback
    try:
        r = requests.get(models_url, timeout=10)
        r.raise_for_status()
        data = r.json()
        models = []
        # OpenAI-compatible /v1/models format
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            for entry in data["data"]:
                if isinstance(entry, dict):
                    mid = entry.get("id") or entry.get("name")
                    if mid:
                        models.append(mid)
        # Legacy Ollama /api/models format
        elif isinstance(data, dict) and "models" in data and isinstance(data["models"], list):
            for entry in data["models"]:
                if isinstance(entry, dict):
                    mid = entry.get("name")
                    if mid:
                        models.append(mid)
        else:
            logger.warning(f"Unexpected models structure from {models_url}: {data}")
        # Try fallback models in order, skipping initial
        for model in models:
            if model == initial_model:
                continue
            try:
                resp2 = query_ollama(messages, model=model, chat_url=chat_url, timeout=timeout)
                if resp2:
                    logger.info(f"Falling back to model '{model}'")
                    return resp2
            except Exception as fe:
                logger.warning(f"Model '{model}' failed during fallback: {fe}")
        logger.error("All fallback models failed to provide a response.")
    except Exception as e:
        logger.error(f"Failed to retrieve models list for fallback from {models_url}: {e}", exc_info=True)
    return None


# ---------------------------------------------------------------------------
# n8n utility
# ---------------------------------------------------------------------------

def query_n8n(message: str,
              session_id: str | None = None,
              system_prompt: str | None = None,
              timeout: int = 60,
              primary_url: str = N8N_WEBHOOK_URL,
              fallback_url: str = N8N_WEBHOOK_FALLBACK) -> dict:
    """Send a chat message to the configured n8n webhook.

    Args:
        message: User message to forward.
        session_id: Optional session identifier to maintain context on n8n side.
        system_prompt: Optional system prompt.
        timeout: Request timeout.
        primary_url: First webhook URL to try.
        fallback_url: Secondary URL to try if the first fails (network error or non-2xx).

    Returns:
        Parsed JSON response from n8n.

    Raises:
        requests.exceptions.RequestException: If both primary and fallback fail.
    """

    payload = {
        "message": message,
    }
    if session_id:
        payload["sessionId"] = session_id
    if system_prompt:
        payload["system_prompt"] = system_prompt

    headers = {"Content-Type": "application/json"}

    # Build list of URL candidates: primary, fallback, and HTTP variants
    try:
        from urllib.parse import urlparse, urlunparse
    except ImportError:
        urlparse = urlunparse = None
    candidates = []
    for url in (primary_url, fallback_url):
        if url and url not in candidates:
            candidates.append(url)
    if urlparse and urlunparse:
        for url in list(candidates):
            parsed = urlparse(url)
            if parsed.scheme == 'https':
                newp = parsed._replace(scheme='http')
                http_url = urlunparse(newp)
                if http_url not in candidates:
                    candidates.append(http_url)
    logger.debug(f"query_n8n: URL candidates = {candidates}")

    attempts = []
    for url in candidates:
        try:
            logger.debug(f"Sending message to n8n webhook {url}: {payload}")
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
            logger.debug(f"n8n response status from {url}: {resp.status_code}")
            if 200 <= resp.status_code < 300:
                try:
                    return resp.json()
                except ValueError:
                    return {"text": resp.text}
            else:
                text_snippet = resp.text.strip().replace('\n', ' ')[:200]
                logger.warning(f"n8n webhook {url} returned HTTP {resp.status_code}: {text_snippet}")
                attempts.append((url, f"HTTP {resp.status_code}: {text_snippet}"))
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to reach n8n webhook {url}: {e}")
            attempts.append((url, f"Error: {e}"))
            last_error = e
    # All attempts failed; log detailed summary
    summary = '; '.join(f"{u} => {m}" for u, m in attempts)
    logger.error(f"All attempts to contact n8n webhook failed. Attempts: {summary}")
    if 'last_error' in locals():
        raise last_error
    else:
        raise Exception(f"n8n webhook unreachable. Attempts: {summary}")


app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Static Page Routes ---

@app.route("/")
def home():
    """Serves the main home page (index.html)."""
    return render_template("index.html")

@app.route("/politique")
def politique():
    """Serves the integration policy page (politique.html)."""
    return render_template("politique.html")

@app.route("/contact")
def contact():
    """Serves the HR contact page (contact.html)."""
    return render_template("contact.html")

@app.route("/coulisses")
def coulisses():
    """Serves the 'Les Coulisses' page (coulisses.html)."""
    return render_template("coulisses.html")

# --- Chatbot UI Routes ---

@app.route("/rh-chatbot")
def rh_chatbot():
    """Serves the dedicated HR chatbot page (rh_chatbot.html)."""
    return render_template("rh_chatbot.html")

@app.route("/test-zone")
def test_zone():
    """Serves the n8n webhook test zone page (test_zone_chatbot.html)."""
    return render_template("test_zone_chatbot.html")

# --- API Endpoints ---

@app.route("/nuria-chat", methods=["POST"]) # Renamed route
def nuria_chat(): # Renamed function
    """
    Handles chat messages from the frontend, proxies them to the Ollama API,
    and returns the AI's response.
    Accepts JSON with "message", optionally "system_prompt" and "model".
    Returns JSON with "response" or "error" and "details".
    """
    try:
        data = request.get_json(silent=True) # silent=True prevents raising an exception on bad JSON
        if not data or "message" not in data or not data["message"]: # Check if data is None or message is empty
            logger.warning("/nuria-chat: Received empty or malformed request.") # Updated log message
            return jsonify({"error": "Aucun message reçu ou format incorrect.", "details": "Request payload was missing or 'message' field was empty."}), 400

        user_msg = data["message"]
        # Consider redacting or summarizing user_msg if it can be very long or sensitive
        logger.info(f"/nuria-chat: Received message (first 100 chars): '{user_msg[:100]}...'") # Updated log message
        
        # Allow overriding system prompt or model from request for more flexibility (e.g. for RH chatbot)
        system_prompt = data.get("system_prompt", SYSTEM_PROMPT)
        model_to_use = data.get("model", OLLAMA_MODEL)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]

        # Try primary model and fall back as needed
        answer = get_response_with_fallback(
            messages,
            chat_url=OLLAMA_CHAT_URL,
            models_url=OLLAMA_MODELS_URL,
            initial_model=model_to_use
        )
        if not answer:
            logger.warning(f"/nuria-chat: All models failed for message: {user_msg[:100]}...")
            return jsonify({"error": "Désolé, je n'ai pas pu générer de réponse.",
                            "details": "Aucun modèle IA n'a renvoyé de réponse valide."}), 500
        logger.info(f"/nuria-chat: Sending response (first 100 chars): '{str(answer)[:100]}...'")
        return jsonify({"response": answer})

    except requests.exceptions.ConnectionError as e:
        logger.error(f"/nuria-chat: Ollama connection error: {e}", exc_info=True) # Updated log message
        return jsonify({"error": "Connexion à l'assistant IA impossible. Veuillez réessayer plus tard.", "details": "Connection to AI service failed."}), 502
    except requests.exceptions.Timeout as e:
        logger.error(f"/nuria-chat: Ollama timeout: {e}", exc_info=True) # Updated log message
        return jsonify({"error": "L'assistant IA n'a pas répondu à temps. Veuillez réessayer.", "details": "Request to AI service timed out."}), 504
    except requests.exceptions.HTTPError as e: # Raised by resp.raise_for_status() in query_ollama
        logger.error(f"/nuria-chat: Ollama HTTP error: {e}", exc_info=True) # Updated log message
        return jsonify({"error": "Erreur de communication avec l'assistant IA.", "details": f"AI service returned HTTP {e.response.status_code}."}), e.response.status_code if e.response else 500
    except Exception as e:
        logger.error(f"/nuria-chat: An unexpected error occurred: {e}", exc_info=True) # Updated log message
        return jsonify({"error": "Une erreur inattendue est survenue sur le serveur.", "details": str(e)}), 500

@app.route("/models", methods=["GET"])
def list_models():
    """
    Proxy endpoint to fetch available models from the configured Ollama API.
    This allows the frontend to get a list of models without directly exposing the Ollama URL.
    """
    logger.info(f"/models: Request received for model list from {OLLAMA_MODELS_URL}")
    try:
        resp = requests.get(OLLAMA_MODELS_URL, timeout=10) # Short timeout for model listing
        resp.raise_for_status()
        data = resp.json()
        logger.debug(f"/models: Raw response from Ollama: {str(data)[:500]}") # Log part of the response
        
        models = []
        # Handle different possible structures for model listing (OpenAI-like vs legacy Ollama)
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list): # OpenAI /v1/models format
            for entry in data["data"]:
                if isinstance(entry, dict):
                    model_id = entry.get("id") or entry.get("name") # 'id' for OpenAI, 'name' sometimes used
                    if model_id:
                        models.append(model_id)
        elif isinstance(data, dict) and "models" in data and isinstance(data["models"], list): # Legacy /api/tags or /api/models format
             for entry in data["models"]:
                if isinstance(entry, dict):
                    model_name = entry.get("name") # Usually 'name' in legacy
                    if model_name:
                        models.append(model_name)
        else:
            logger.warning(f"/models: Unexpected data structure for models: {data}")

        logger.info(f"/models: Successfully fetched {len(models)} models. Models: {models}")
        return jsonify(models=models)
    except requests.exceptions.RequestException as e:
        logger.error(f"/models: Error connecting to Ollama models endpoint: {e}", exc_info=True)
        return jsonify({"error": "Impossible de récupérer la liste des modèles IA.", "details": str(e)}), 502
    except Exception as e:
        logger.error(f"/models: An unexpected error occurred while listing models: {e}", exc_info=True)
        return jsonify({"error": "Une erreur inattendue est survenue lors de la récupération des modèles.", "details": str(e)}), 500

# ---------------------------------------------------------------------------
# n8n Proxy Endpoint
# ---------------------------------------------------------------------------


@app.route("/n8n-chat", methods=["POST"])
def n8n_chat():
    """Proxy endpoint to forward chat messages to the n8n webhook.

    Expects JSON payload: {"message": "...", "sessionId": "optional", "system_prompt": "optional"}
    Returns whatever n8n returns, wrapped in JSON if necessary.
    """
    try:
        data = request.get_json(silent=True)
        if not data or not data.get("message"):
            return jsonify({"error": "Aucun message fourni."}), 400

        user_msg = str(data["message"])
        session_id = data.get("sessionId") or data.get("session_id")
        system_prompt = data.get("system_prompt")

        logger.info(f"/n8n-chat: Forwarding message to n8n. Session: {session_id}, First 100 chars: '{user_msg[:100]}...' ")

        n8n_resp = query_n8n(
            message=user_msg,
            session_id=session_id,
            system_prompt=system_prompt,
            timeout=60,
            primary_url=N8N_WEBHOOK_URL,
            fallback_url=N8N_WEBHOOK_FALLBACK
        )

        logger.debug(f"/n8n-chat: Raw n8n response: {str(n8n_resp)[:500]}")

        # Simply relay the JSON as-is
        return jsonify(n8n_resp)

    except requests.exceptions.RequestException as e:
        logger.error(f"/n8n-chat: Error contacting n8n: {e}", exc_info=True)
        return jsonify({"error": "Le service RH est injoignable.", "details": str(e)}), 502
    except Exception as e:
        logger.error(f"/n8n-chat: Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "Erreur interne du serveur.", "details": str(e)}), 500

# --- Static Asset Serving ---

@app.route('/assets/<path:filename>')
def serve_assets(filename: str):
    """Serves static files from the 'static/assets' directory."""
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

@app.route('/favicon.ico')
def favicon():
    """Serves the favicon.ico from the static folder."""
    return send_from_directory(app.static_folder, 'favicon.ico')

# --- Main Application Execution ---

if __name__ == "__main__":
    # Note: Flask's default debug mode is generally not recommended for production.
    # Use a production-ready WSGI server (e.g., Gunicorn, Waitress) in production.
    app.run(debug=True, host="0.0.0.0", port=8080)
