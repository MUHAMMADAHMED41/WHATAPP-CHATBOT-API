from flask import Flask, request, jsonify
import requests


import logging
import sys

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
VERIFY_TOKEN = ''
ACCESS_TOKEN = ''
PHONE_NUMBER_ID = ''
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    print(">>> Webhook HIT", flush=True)

    if request.method == 'GET':
        print(">>> GET Verification Request", flush=True)
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
                            send_message(sender, msg_body)  # Echo the same message
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
    print(">>> Starting Flask WhatsApp server...")
    app.run(debug=True, port=5000)
