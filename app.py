import os
import smtplib
from html import escape
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


MAIL_HOST = get_env("MAIL_HOST")
MAIL_PORT = int(get_env("MAIL_PORT", 465))
MAIL_USERNAME = get_env("MAIL_USERNAME")
MAIL_PASSWORD = get_env("MAIL_PASSWORD")
MAIL_FROM = get_env("MAIL_FROM")
MAIL_FROM_NAME = get_env("MAIL_FROM_NAME", "Portfolio")
MAIL_TO = get_env("MAIL_TO", MAIL_USERNAME)
API_KEY = get_env("API_KEY")

REQUIRED_EMAIL_CONFIG = {
    "MAIL_HOST": MAIL_HOST,
    "MAIL_PORT": MAIL_PORT,
    "MAIL_USERNAME": MAIL_USERNAME,
    "MAIL_PASSWORD": MAIL_PASSWORD,
    "MAIL_FROM": MAIL_FROM,
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

    try:
        msg = MIMEMultipart("alternative")

        msg["Subject"] = f"{MAIL_FROM_NAME} Contact Form: {name}"
        msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
        msg["To"] = MAIL_TO
        msg["Reply-To"] = email

        text_body = f"""
            Name: {name}
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

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT, timeout=30) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(
                MAIL_FROM,
                MAIL_TO,
                msg.as_string()
            )

        return jsonify({
            "success": True,
            "message": "Message sent successfully."
        })

    except Exception:
        current_app.logger.exception(
            "SMTP Error while sending contact form email. host=%s port=%s username=%s from=%s to=%s",
            MAIL_HOST,
            MAIL_PORT,
            MAIL_USERNAME,
            MAIL_FROM,
            MAIL_TO
        )
        return jsonify({
            "success": False,
            "message": "Unable to send email."
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
