# nourrir_flask/app.py

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import requests

# Configuration for Ollama chat API endpoints
# Default to the publicly-hosted Ollama service; override via environment if needed.
OLLAMA_CHAT_URL = os.getenv(
    "OLLAMA_CHAT_URL",
    "https://ollama.artemis-ai.ca/v1/chat/completions"
)
OLLAMA_MODELS_URL = os.getenv(
    "OLLAMA_MODELS_URL",
    "https://ollama.artemis-ai.ca/v1/models"
)
# Model identifier, must match an available model from /models (default to phi4:latest)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi4:latest")

# Default system prompt for NuRiH Ami
SYSTEM_PROMPT = (
    "Tu es NuRiH Ami, assistant éducatif pour le bien-être, nutrition et créativité. "
    "Sois amical, inclusif, bref et adapté à tous publics."
)

def query_ollama(messages, model=OLLAMA_MODEL, chat_url=OLLAMA_CHAT_URL, timeout=60):
    """
    Send messages to Ollama chat API (OpenAI-compatible or legacy) and return assistant content.
    """
    payload = {"model": model, "messages": messages, "stream": False}
    resp = requests.post(chat_url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    # OpenAI-compatible response parsing
    if isinstance(data, dict) and "choices" in data:
        choices = data.get("choices", [])
        if choices and isinstance(choices[0], dict):
            msg = choices[0].get("message", {})
            content = msg.get("content")
            if content is not None:
                return content
    # Fallback to legacy Ollama API format
    if isinstance(data, dict) and "message" in data:
        return data.get("message", {}).get("content", "")
    # Unexpected format
    return str(data)

app = Flask(__name__, static_folder='static', template_folder='templates')

# HOME
@app.route("/")
def home():
    return render_template("index.html")

# Politique d'intégration
@app.route("/politique")
def politique():
    return render_template("politique.html")

# Contact RH
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Proxy pour NuRiH Ami chatbot (Ollama chat API)
@app.route("/nurih-ami", methods=["POST"])
def nurih_ami():
    """
    Proxy: receive chat message from frontend, forward to Ollama chat API, return result.
    Uses OLLAMA_URL and OLLAMA_MODEL from environment or defaults.
    """
    data = request.get_json(silent=True) or {}
    user_msg = data.get("message", "")
    if not user_msg:
        return jsonify({"error": "Aucun message reçu"}), 400

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ]

    try:
        answer = query_ollama(messages)
        if not answer:
            answer = "Je n'ai pas compris, peux-tu reformuler ?"
        return jsonify({"response": answer})
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connexion à Ollama impossible"}), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "Ollama n'a pas répondu à temps"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/models", methods=["GET"])
def list_models():
    """
    Proxy endpoint to fetch available models from Ollama API.
    """
    try:
        resp = requests.get(OLLAMA_MODELS_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        models = []
        if isinstance(data, dict):
            for entry in data.get("data", []):
                model_id = entry.get("id")
                if model_id:
                    models.append(model_id)
        return jsonify(models=models)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Pour servir correctement tous fichiers dans assets
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

# Optionnel : favicon (sinon supprime la route)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
