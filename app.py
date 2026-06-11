import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Portfolio")
MAIL_TO = os.getenv("MAIL_TO", MAIL_USERNAME)
API_KEY = os.getenv("API_KEY")


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
            <h2 style="margin-bottom:0;">{MAIL_FROM_NAME} Contact Form Message:</h2>
            <hr style="margin:0; border:0; border-top:1px solid #000;">

            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Message:</strong></p>
            <p>{message}</p>
        """

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT) as server:
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

    except Exception as e:
        print(f"SMTP Error: {e}")
        return jsonify({
            "success": False,
            "message": "Unable to send email."
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)