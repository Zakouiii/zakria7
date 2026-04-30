from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# =========================
# 🔑 إعدادات
# =========================
PAGE_TOKEN = "EAAMD5SUZAe8YBRXJJUDEJLkodssihglZAqBFjCM04U46WpMbdjnaJP2UYnuI3xZCR09ZBdWzn0tmXOU526qk5wp9nQ4WFwbKqMY2tqjcpjv6PeDYLdvgmdA9zr3UYChHUk5ZBaIz8ZAhlvXOYP64eLFmUnROA8eIYWYMXIbMDooNE3jQFmP3hAChHimVg6ZBU8P9yo0JQZDZD"
VERIFY_TOKEN = "zako70012"

PHONE_API = "https://relation-cap-prince-exhibitions.trycloudflare.com/run"

users = {}

# =========================
# 📩 إرسال رسالة فيسبوك
# =========================
def send_message(psid, text):
    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_TOKEN}

    payload = {
        "recipient": {"id": psid},
        "message": {"text": text}
    }

    requests.post(url, json=payload, params=params)


# =========================
# 🌐 الصفحة الرئيسية
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "message": "API + Facebook Bot شغال 🚀"
    })


# =========================
# 📱 API الهاتف (Cloudflare)
# =========================
@app.route("/run", methods=["POST"])
def run():
    data = request.json

    return jsonify({
        "status": "ok",
        "received": data
    })


# =========================
# 🔐 تحقق فيسبوك
# =========================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "error", 403


# =========================
# 📩 استقبال رسائل فيسبوك
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        entry = data["entry"][0]
        messaging = entry["messaging"][0]

        psid = messaging["sender"]["id"]

        message = messaging.get("message")

        # ❌ تجاهل غير الرسائل
        if not message:
            return "ok", 200

        # ❌ منع echo
        if message.get("is_echo"):
            return "ok", 200

        text = message.get("text", "")

        # 📱 إرسال للهاتف
        try:
            requests.post(PHONE_API, json={
                "action": "message",
                "text": text
            })
        except:
            pass

        send_message(psid, f"📩 وصلت رسالتك: {text}")

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


# =========================
# 🚀 تشغيل السيرفر
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    app.run(host="0.0.0.0", port=port)