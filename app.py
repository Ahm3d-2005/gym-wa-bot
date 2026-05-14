from flask import Flask, request, jsonify
import requests
import json
import time
import os  # Required for Port binding

app = Flask(__name__)

# ===== CONFIGURATION =====
# Updated to match the ID in your screenshots
PHONE_NUMBER_ID = "1114308051764214" 
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")

WHATSAPP_API_URL = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

# Helper to send text
def send_text(to, text):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    try:
        r = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
        print(f"Send Text Status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"Error sending text: {e}")

# Main menu buttons
def send_main_menu(to):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🏋️ Welcome to GymBot by Ahmed! Please choose an option:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "hours", "title": "📍 Hours & Location"}},
                    {"type": "reply", "reply": {"id": "plans", "title": "💪 Membership Plans"}},
                    {"type": "reply", "reply": {"id": "buy", "title": "💰 Buy Membership"}}
                ]
            }
        }
    }
    try:
        r = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
        print(f"Send Menu Status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"Error sending menu: {e}")

# Detailed Handlers
def send_back_button(to, info_text):
    send_text(to, info_text)
    time.sleep(1)
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🔙 Return to Menu"},
            "action": {
                "buttons": [{"type": "reply", "reply": {"id": "main_menu", "title": "🏠 Back to Menu"}}]
            }
        }
    }
    requests.post(WHATSAPP_API_URL, headers=headers, json=data)

def handle_button(to, button_id):
    if button_id == "hours":
        send_back_button(to, "🏋️ Gym Hours: 6 AM – 10 PM (Mon-Sat)\n📍 Location: Main Street.")
    elif button_id == "plans":
        send_back_button(to, "💪 Plans: 1 Month: $30 | 3 Months: $80")
    elif button_id == "buy":
        send_back_button(to, "💰 Bank: ABC Bank\nAccount: 1234-5678-90")
    else:
        send_main_menu(to)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == "gym123":
        return request.args.get("hub.challenge"), 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(f"Incoming: {json.dumps(data)}") # View this in Render logs
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
            user_number = msg["from"]
            
            if "interactive" in msg:
                handle_button(user_number, msg["interactive"]["button_reply"]["id"])
            elif "text" in msg:
                send_main_menu(user_number)
    except Exception as e:
        print(f"Webhook Error: {e}")
    return jsonify({"status": "ok"}), 200

# FIX: Dynamic Port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
