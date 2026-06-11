import os
import json
import urllib.error
import urllib.request
from html import escape

from flask import Flask, request, jsonify, current_app
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/send-email": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-API-Key"],
        "supports_credentials": False,
        "max_age": 86400
    },
    r"/ping": {
        "origins": "*"
    }
})

def get_env(name, default=None):
    value = os.getenv(name, default)
    if isinstance(value, str):
        return value.strip().strip('"').strip("'")
    return value


RESEND_API_URL = get_env("RESEND_API_URL", "https://api.resend.com/emails")
RESEND_API_KEY = get_env("RESEND_API_KEY")
RESEND_FROM = get_env("RESEND_FROM", "Portfolio <onboarding@resend.dev>")
MAIL_FROM_NAME = get_env("MAIL_FROM_NAME", "Portfolio")
MAIL_TO = get_env("MAIL_TO")
API_KEY = get_env("API_KEY")

REQUIRED_EMAIL_CONFIG = {
    "RESEND_API_KEY": RESEND_API_KEY,
    "RESEND_FROM": RESEND_FROM,
    "MAIL_TO": MAIL_TO,
    "API_KEY": API_KEY,
}


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({
        "success": True,
        "message": "pong"
    })

@app.route("/send-email", methods=["POST"])
def send_email():
    client_api_key = request.headers.get("X-API-Key")

    if not client_api_key or client_api_key != API_KEY:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid JSON payload."
        }), 400

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not name or not email or not message:
        return jsonify({
            "success": False,
            "message": "Name, email, and message are required."
        }), 400

    missing_config = [
        key for key, value in REQUIRED_EMAIL_CONFIG.items()
        if value is None or value == ""
    ]
    if missing_config:
        current_app.logger.error(
            "Missing email configuration: %s",
            ", ".join(missing_config)
        )
        return jsonify({
            "success": False,
            "message": "Email service is not configured."
        }), 500

    text_body = f"""Name: {name}
Email: {email}

Message:
{message}
"""

    html_body = f"""
        <h2 style="margin-bottom:0;">{escape(MAIL_FROM_NAME)} Contact Form Message:</h2>
        <hr style="margin:0; border:0; border-top:1px solid #000;">

        <p><strong>Name:</strong> {escape(name)}</p>
        <p><strong>Email:</strong> {escape(email)}</p>
        <p><strong>Message:</strong></p>
        <p>{escape(message).replace("\n", "<br>")}</p>
    """

    payload = {
        "from": RESEND_FROM,
        "to": [MAIL_TO],
        "subject": f"{MAIL_FROM_NAME} Contact Form: {name}",
        "html": html_body,
        "text": text_body,
        "reply_to": email,
    }

    try:
        request_body = json.dumps(payload).encode("utf-8")
        resend_request = urllib.request.Request(
            RESEND_API_URL,
            data=request_body,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "flask-contact-form-api/1.0",
            },
            method="POST",
        )

        with urllib.request.urlopen(resend_request, timeout=30) as response:
            response_body = response.read().decode("utf-8")
            current_app.logger.info("Resend email sent: %s", response_body)

        return jsonify({
            "success": True,
            "message": "Message sent successfully."
        })

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        current_app.logger.error(
            "Resend API error. status=%s body=%s",
            error.code,
            error_body
        )
        return jsonify({
            "success": False,
            "message": "Unable to send email."
        }), 500

    except Exception:
        current_app.logger.exception(
            "Resend request failed while sending contact form email. from=%s to=%s",
            RESEND_FROM,
            MAIL_TO
        )
        return jsonify({
            "success": False,
            "message": "Unable to send email."
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
