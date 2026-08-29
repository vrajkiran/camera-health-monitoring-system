import json
import smtplib
import urllib.parse
import urllib.request
from email.mime.text import MIMEText

from config import GMAIL_APP_PASSWORD, GMAIL_USER, ADMIN_EMAIL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def email_configured():
    return all([GMAIL_USER, GMAIL_APP_PASSWORD, ADMIN_EMAIL, "your_" not in GMAIL_USER, "your_" not in GMAIL_APP_PASSWORD])


def telegram_configured():
    return all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, "replace_with" not in TELEGRAM_BOT_TOKEN, "replace_with" not in TELEGRAM_CHAT_ID])


def send_email_report(subject, body, html=False):
    if not email_configured():
        return {"sent": False, "reason": "Email is not configured in .env"}

    message = MIMEText(body, "html" if html else "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = GMAIL_USER
    message["To"] = ADMIN_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_USER, [ADMIN_EMAIL], message.as_string())

    return {"sent": True, "channel": "EMAIL"}


def send_telegram_message(text, reply_markup=None):
    if not telegram_configured():
        return {"sent": False, "reason": "Telegram bot is not configured in .env"}

    params = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    if reply_markup:
        params["reply_markup"] = json.dumps(reply_markup)
    payload = urllib.parse.urlencode(params).encode("utf-8")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    request = urllib.request.Request(url, data=payload, method="POST")

    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))

    return {"sent": bool(data.get("ok")), "channel": "TELEGRAM", "telegram_response": data}


def build_alert_message(camera_name, location, root_cause):
    return (
        "UCEK-JNTUK Camera Health Notification\n"
        f"Camera: {camera_name}\n"
        f"Location: {location}\n"
        f"Condition: {root_cause}\n"
        "Please review the Camera Health Monitoring dashboard for operational follow-up."
    )


def send_email(camera_name, location, root_cause):
    subject = f"UCEK-JNTUK Camera Health Alert - {camera_name}"
    return send_email_report(subject, build_alert_message(camera_name, location, root_cause))


def send_telegram(camera_name, location, root_cause):
    return send_telegram_message(build_alert_message(camera_name, location, root_cause))

