# Contact Form API

A simple Flask API that sends contact form submissions to an email address using SMTP.

## Features

* Send contact form messages via email
* API key authentication
* HTML and plain text email support
* Environment variable configuration

## Requirements

* Python 3.10+
* Gmail App Password (or SMTP credentials)

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
MAILER=xxxxxxxx
MAIL_HOST=xxxxxxxxxxxxx
MAIL_PORT=465
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_ENCRYPTION=xxxxx
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=Portfolio
MAIL_TO=your-email@gmail.com

API_KEY=your-secret-api-key
```

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
