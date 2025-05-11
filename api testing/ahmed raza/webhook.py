from flask import Flask, request, jsonify
import requests
import logging
import sys
from bot import process_message

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("whatsapp_app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)

# Config values
VERIFY_TOKEN = 'whatsapp_token_123'
ACCESS_TOKEN = 'EAAmh2sa0pIABO9qiHVXayrYaO8DntG5eQ8wZByVrlfGgYNZBzi4LNPFHHyMTrmdDOaE7AXa6jZAuJfAu7zfj6I9qu9NE8AssvoDno0UpHsXZBPBrG3pKJp2UlzkdxiFztYq00909ZCVHcekJik2J0sue84g5olNdRnyDWUUlLVSOc9ufPWa6Jz1Ji'
PHONE_NUMBER_ID = '631271576741899'
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    logging.debug("Webhook HIT")

    if request.method == 'GET':
        logging.debug("GET Verification Request")
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logging.info("✅ Webhook verified!")
            return challenge, 200
        else:
            logging.warning("❌ Verification failed")
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
                            # Process message using AI Ilim Bot
                            response_text = process_message(sender, msg_body)
                            send_message(sender, response_text)
                        else:
                            logging.warning("Missing sender or message in payload.")
        except Exception as e:
            logging.exception("Exception while handling incoming message")

        return 'EVENT_RECEIVED', 200

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

if __name__ == '__main__':
    logging.info("Starting Flask WhatsApp server...")
    app.run(debug=True, port=5000)