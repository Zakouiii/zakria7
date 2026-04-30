from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# =========================
# 🤖 CHAT API (Proxy)
# =========================
UPSTREAM_URL = "https://api.appzoneai.com/v1/chat/completions"

CHAT_HEADERS = {
    'User-Agent': 'okhttp/4.9.2',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'authorization': 'Bearer az-chatai-key',
}

@app.route("/")
def home():
    return jsonify({
        "message": "مرحبا بك في API زاكي + فيسبوك بوت 🚀",
        "status": "running"
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json

        res = requests.post(
            UPSTREAM_URL,
            headers=CHAT_HEADERS,
            json=data
        )

        try:
            return jsonify(res.json())
        except:
            return jsonify({"raw": res.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# 📘 FACEBOOK MESSENGER BOT
# =========================
PAGE_TOKEN = "EAAMD5SUZAe8YBRXJJUDEJLkodssihglZAqBFjCM04U46WpMbdjnaJP2UYnuI3xZCR09ZBdWzn0tmXOU526qk5wp9nQ4WFwbKqMY2tqjcpjv6PeDYLdvgmdA9zr3UYChHUk5ZBaIz8ZAhlvXOYP64eLFmUnROA8eIYWYMXIbMDooNE3jQFmP3hAChHimVg6ZBU8P9yo0JQZDZD"
VERIFY_TOKEN = "zako70012"

users = {}

def send_message(psid, text, buttons=None):
    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_TOKEN}

    if buttons:
        payload = {
            "recipient": {"id": psid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons
                    }
                }
            }
        }
    else:
        payload = {
            "recipient": {"id": psid},
            "message": {"text": text}
        }

    requests.post(url, json=payload, params=params)


# 🔐 تحقق فيسبوك
@app.route("/webhook", methods=["GET"])
def verify():
    if (request.args.get("hub.mode") == "subscribe" and
        request.args.get("hub.verify_token") == VERIFY_TOKEN):
        return request.args.get("hub.challenge"), 200
    return "error", 403


# 📩 استقبال رسائل فيسبوك
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        entry = data["entry"][0]
        messaging = entry["messaging"][0]

        psid = messaging["sender"]["id"]

        text = messaging.get("message", {}).get("text", "")
        postback = messaging.get("postback", {}).get("payload", None)

        # 🧠 حالة المستخدم
        if psid not in users:
            users[psid] = {"step": "start"}

        user = users[psid]

        # 💬 أول رسالة
        if text and user["step"] == "start":
            user["step"] = "chat"
            send_message(psid, "👋 مرحبا بك في بوت زاكي، ارسل رسالتك الآن")

        # 🤖 محاكاة رد AI
        elif text and user["step"] == "chat":
            ai_data = {
                "model": "gpt-5.4-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text}
                        ]
                    }
                ]
            }

            try:
                r = requests.post(
                    UPSTREAM_URL,
                    headers=CHAT_HEADERS,
                    json=ai_data
                )

                reply = r.json()

                # محاولة استخراج الرد
                answer = str(reply)

            except:
                answer = "حدث خطأ في الاتصال بالذكاء الاصطناعي"

            send_message(psid, answer)

        # 🔘 زر (اختياري)
        elif postback:
            if postback == "START_BOT":
                send_message(psid, "🚀 تم تشغيل البوت بنجاح")

    except Exception as e:
        print("error:", e)

    return "ok", 200


# =========================
# 🚀 تشغيل السيرفر
# =========================
if __name__ == "__main__":
    print("🚀 Server running...")
    app.run(host="0.0.0.0", port=10000)