# webhook.py
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "Bearer "

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    elif request.method == "POST":
        data = request.get_json()
        print("Webhook received:", data)  # You can log or store this
        return "Event received", 200

if __name__ == "__main__":
    app.run(port=5000)
