# nourrir_flask/app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import logging, os
from config import LOG_FILE
from services.chat_service import get_reply

# logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route("/")
def home():        return render_template("index.html")

@app.route("/politique")
def politique():   return render_template("politique.html")

@app.route("/contact")
def contact():     return render_template("contact.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/nurih-ami", methods=["POST"])
def nurih_ami():
    user_msg = (request.json or {}).get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "Aucun message reçu"}), 400
    answer = get_reply(user_msg)
    return jsonify({"response": answer})

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(app.static_folder, "assets"), filename)

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
