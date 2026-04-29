import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "fron12015")
PAGE_ACCESS_TOKEN = os.environ.get(
    "PAGE_ACCESS_TOKEN",
    "EAAMD5SUZAe8YBRflfIWi9S5gsw5QOvIcVmnjKNMpi346YLYekgOy3IsE0NZAO1nFnNvV1AGs1DqpuTF6vt1njr6MZAuqyIu7dTEidWtac9SsbE4oFoVEKRTjJUVJ1TqO2RuwXVP49v3Ugx4VUi8eXZAnblQWJLrSarWo5Iy9aStPHI8ezZCvlpkOALRyyWBx0D1yxgQZDZD",
)

AI_API_URL = "https://baithek.com/chatbee/health_ai/new_health.php"
FB_GRAPH_URL = "https://graph.facebook.com/v18.0/me/messages"

SYSTEM_PROMPT = (
    "أنت مساعد ودود ومحترم تتحدث بالعربية الفصحى المبسطة. "
    "ردودك واضحة ومختصرة ومفيدة. "
    "تتعامل مع الناس بلطف واحترام، وتسأل أسئلة توضيحية إذا لزم الأمر. "
    "إذا سألك المستخدم عن أمر طبي خطير، انصحه بمراجعة طبيب مختص."
)

THUMBS_UP_EMOJIS = {"👍", "👍🏻", "👍🏼", "👍🏽", "👍🏾", "👍🏿"}


def get_ai_reply(user_message):
    try:
        payload = {
            "name": "Usama",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(AI_API_URL, json=payload, headers=headers, timeout=30)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI API error: {e}")
        return "عذراً، حدث خطأ أثناء معالجة رسالتك. حاول مرة أخرى."


def send_message(recipient_id, message_text):
    try:
        params = {"access_token": PAGE_ACCESS_TOKEN}
        headers = {"Content-Type": "application/json"}
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
        }
        r = requests.post(FB_GRAPH_URL, params=params, headers=headers, json=payload, timeout=30)
        if r.status_code != 200:
            print(f"Send message error: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Send message exception: {e}")


def is_thumbs_up(text):
    if not text:
        return False
    stripped = text.strip()
    if stripped in THUMBS_UP_EMOJIS:
        return True
    for emoji in THUMBS_UP_EMOJIS:
        if emoji in stripped and len(stripped) <= 6:
            return True
    return False


@app.route("/", methods=["GET"])
def home():
    return "Facebook Messenger Bot is running.", 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully.")
        return challenge, 200
    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json(silent=True) or {}

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event.get("sender", {}).get("id")
                message = event.get("message", {})

                if message.get("is_echo"):
                    continue

                if not sender_id:
                    continue

                user_text = message.get("text", "")

                if is_thumbs_up(user_text):
                    print(f"Thumbs up from {sender_id}")
                    send_message(sender_id, "👍")
                    continue

                if user_text:
                    print(f"Message from {sender_id}: {user_text}")
                    ai_reply = get_ai_reply(user_text)
                    send_message(sender_id, ai_reply)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)