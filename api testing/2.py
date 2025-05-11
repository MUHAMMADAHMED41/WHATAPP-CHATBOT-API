from flask import Flask, request, jsonify
import requests
import logging
import sys
import google.generativeai as genai

# === Gemini Configuration ===
GEMINI_API_KEY = ""  # Replace with your Gemini API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# === Logging Setup ===
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("whatsapp_app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)

# === WhatsApp Config ===
VERIFY_TOKEN = 'whatsapp_token_123'
ACCESS_TOKEN = 'EAAmh2sa0pIABO1Dv9pgFcEYZBSBVZCZB1PFiJeinYtqTVgy6ETimvN1yChf9XZAZBqtQwhG4kBGdSjUVJjZBnUohwS4PBZADH776wuMpkcT328Gbl0eTHcDUikpMKFo7NPOBagJF9LMgA3mtSWsBIxEy0vvzKfQqwP9G69pq3MkDLZA2RbqAjBWG9h5jUPfR7z5AQYfG7tb1qeH5mRFkw13x8EKZBZBg9V'  # Replace with your actual token
PHONE_NUMBER_ID = ''
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

# === AI Urdu Response Generator ===
def get_ai_urdu_response(prompt):
    try:
        system_prompt = "you are an helpful assistant company name dialer portal and give info on prices and services of that netwoking ,teleomunnication company"
        response = model.generate_content([system_prompt, prompt])
        return f"🌟 {response.text.strip()}\n\n📘 AI سے مدد"
    except Exception as e:
        logging.exception("❌ Gemini AI response failed")
        return "sorry cant reply you right now please try again later"

# === WhatsApp Message Sender ===
def send_message(to, message_text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    logging.debug(f"Sending message to {to}: {message_text}")
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        logging.info(f"✅ Message sent successfully: {response.status_code}")
        logging.debug(response.text)
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to send message to {to}")
        logging.exception(e)

# === Webhook Route ===
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    print(">>> Webhook HIT", flush=True)

    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print(">>> ✅ Webhook verified!", flush=True)
            return challenge, 200
        else:
            print(">>> ❌ Verification failed", flush=True)
            return 'Verification token mismatch', 403

    elif request.method == 'POST':
        try:
            data = request.get_json()
            logging.debug(f"POST webhook data: {data}")

            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    messages = value.get('messages', [])

                    for message in messages:
                        sender = message.get('from')
                        msg_body = message.get('text', {}).get('body')

                        if sender and msg_body:
                            logging.info(f"Received message from {sender}: {msg_body}")
                            response_text = get_ai_urdu_response(msg_body)
                            send_message(sender, response_text)
                        else:
                            logging.warning("Missing sender or message in payload.")
        except Exception as e:
            logging.exception("Exception while handling incoming message")

        return 'EVENT_RECEIVED', 200

# === Server Start ===
if __name__ == '__main__':
    print(">>> Starting Flask WhatsApp AI Urdu Teacher Assistant...")
    app.run(debug=True, port=5000)
