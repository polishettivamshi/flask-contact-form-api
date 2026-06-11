# Contact Form API

A simple Flask API that sends contact form submissions to an email address using Resend.

## Features

* Send contact form messages via email
* API key authentication
* HTML and plain text email support
* Environment variable configuration

## Requirements

* Python 3.10+
* Resend API key

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
RESEND_API_KEY=your-resend-api-key
RESEND_FROM=Portfolio <onboarding@resend.dev>
MAIL_FROM_NAME=Portfolio
MAIL_TO=your-email@gmail.com

API_KEY=your-secret-api-key
```

`RESEND_FROM` must be a sender allowed by your Resend account. For quick testing, Resend supports `onboarding@resend.dev`; for production, verify your own domain in Resend and use an address from that domain.

## Run the Application

```bash
python app.py
```

Server will start at:

```text
http://localhost:8000
```

## API Endpoint

### Send Email

**POST** `/send-email`

Headers:

```http
Content-Type: application/json
X-API-Key: your-secret-api-key
```

Request Body:

```json
{
  "name": "Vamshi",
  "email": "vamshi@example.com",
  "message": "Hello, this is a test message."
}
```

Success Response:

```json
{
  "success": true,
  "message": "Message sent successfully."
}
```

Error Response:

```json
{
  "success": false,
  "message": "Unauthorized"
}
```
