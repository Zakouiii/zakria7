from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

PAGE_TOKEN = "EAAMD5SUZAe8YBRXJJUDEJLkodssihglZAqBFjCM04U46WpMbdjnaJP2UYnuI3xZCR09ZBdWzn0tmXOU526qk5wp9nQ4WFwbKqMY2tqjcpjv6PeDYLdvgmdA9zr3UYChHUk5ZBaIz8ZAhlvXOYP64eLFmUnROA8eIYWYMXIbMDooNE3jQFmP3hAChHimVg6ZBU8P9yo0JQZDZD"
VERIFY_TOKEN = "zako70012"

PHONE_URL = "https://vernon-ripe-enhance-fold.trycloudflare.com/run"

users = {}

# =========================
# 🌐 الصفحة الرئيسية
# =========================
@app.route("/")
def home():
    return jsonify({
        "message": "API زاكي شغال 🚀",
        "usage": {
            "browser": "/test?phone=07xxxxxxxx",
            "post": "/run"
        }
    })


# =========================
# 🧪 اختبار من المتصفح (GET)
# =========================
@app.route("/test", methods=["GET"])
def test():
    phone = request.args.get("phone")

    if not phone:
        return {"error": "ضع رقم الهاتف ?phone=07xxxx"}

    # إرسال للهاتف
    try:
        r = requests.post(PHONE_URL, json={
            "action": "send_otp",
            "phone": phone
        })

        return {
            "status": "sent",
            "phone": phone,
            "response": r.text
        }

    except Exception as e:
        return {"error": str(e)}


# =========================
# 📡 API (POST للهاتف أو أي تطبيق)
# =========================
@app.route("/run", methods=["POST"])
def run():
    data = request.json

    try:
        r = requests.post(PHONE_URL, json=data)

        return jsonify({
            "status": "ok",
            "sent_to_phone": data,
            "phone_response": r.text
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# =========================
# ❤️ Facebook Webhook
# =========================
def send_message(psid, text):
    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_TOKEN}

    payload = {
        "recipient": {"id": psid},
        "message": {"text": text}
    }

    requests.post(url, json=payload, params=params)


@app.route("/webhook", methods=["GET"])
def verify():
    if (request.args.get("hub.mode") == "subscribe" and
        request.args.get("hub.verify_token") == VERIFY_TOKEN):
        return request.args.get("hub.challenge"), 200
    return "error", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        entry = data["entry"][0]
        messaging = entry["messaging"][0]

        psid = messaging["sender"]["id"]
        text = messaging.get("message", {}).get("text", "")

        send_message(psid, f"📩 استلمت: {text}")

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


# =========================
# 🚀 تشغيل السيرفر
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)