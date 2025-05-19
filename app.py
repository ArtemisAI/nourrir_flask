# nourrir_flask/app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import logging, os, smtplib
from email.message import EmailMessage
from config import LOG_FILE

# N8N public URL for embedding, if provided
N8N_PUBLIC_URL = os.getenv("N8N_PUBLIC_URL")
from services.chat_service import get_reply

# logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

app = Flask(__name__, static_folder='static', template_folder='templates')

# -------------------------------------------------
# Email helper  (uses environment variables for SMTP credentials)
# -------------------------------------------------


def _send_email(to_addr: str, subject: str, body: str) -> bool:
    """Send an email via SMTP. Returns True on success.

    Credentials are read from environment variables so that no secret appears in
    the codebase:

        SMTP_SERVER   (default: smtp.gmail.com)
        SMTP_PORT     (default: 465)
        SMTP_USERNAME (required)
        SMTP_PASSWORD (required)
        SMTP_USE_TLS  ("true" to use STARTTLS instead of implicit TLS)
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_pass:
        logging.warning("SMTP credentials not configured; email not sent.")
        return False

    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        use_tls = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
        if use_tls:
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)
        logging.info("Contact email sent to %s", to_addr)
        return True
    except Exception as e:
        logging.error("Failed to send contact email: %s", e)
        return False

# -------------------------------------------------
# Additional informational pages
# -------------------------------------------------



# New routes for values page and policy PDF viewer






@app.route("/")
def home():        return render_template("index.html")

@app.route("/politique")
def politique():   return render_template("politique.html")

@app.route("/contact")
def contact():     return render_template("contact.html")

# Company values page
@app.route("/valeurs")
def valeurs():
    return render_template("valeurs.html")

# Policy PDF viewer (protected client-side)
@app.route("/politique-pdf")
def politique_pdf():
    return render_template("politique_pdf.html")

# -------------------------------------------------
# Public n8n UI embed
# -------------------------------------------------


@app.route("/n8n")
def n8n_page():
    if not N8N_PUBLIC_URL:
        return "n8n n'est pas configuré", 404
    return render_template("n8n.html", n8n_url=N8N_PUBLIC_URL)

# -------------------------------------------------
# Contact form
# -------------------------------------------------


@app.route("/submit-contact", methods=["POST"])
def submit_contact():
    data = request.json or {}
    name = data.get("name", "")
    email = data.get("email", "")
    subject = data.get("subject", "Message formulaire de contact") or "Message formulaire de contact"
    message = data.get("message", "(vide)")

    body_lines = [
        f"Nom: {name}",
        f"Email: {email}",
        f"Sujet: {subject}",
        "\nMessage:\n",
        message,
    ]
    body = "\n".join(body_lines)

    # Attempt to send the email; silently continue if it fails so the user is
    # not confronted with an error.
    _send_email("n8n.artemisai@gmail.com", subject, body)

    return jsonify({"message": "Merci! Votre message a bien été envoyé."})

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

# -------------------------------------------------
# Template context
# -------------------------------------------------


@app.context_processor
def inject_globals():
    return {"N8N_PUBLIC_URL": N8N_PUBLIC_URL}

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
