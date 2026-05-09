from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# ===== CONFIGURATION =====
PHONE_NUMBER_ID = "1059667987236268"
ACCESS_TOKEN = "EAAgSVdSxtf0BRW5gLOWeHxUT75mxtRcqnFVTUPpZBVzXbVEmL9pZAAdZANI0Ndqd2n87qnMZAVgL1DLlz8FjH2RFD9cxTy8unELQdar1d2NTBOo8zjtoZC88bpjseKET2mVeHUYBZBku5rnZCqZAgL5UyPn17Fk4ofwrxnfOowwsTJv1Cgs2I3Pvpu0YahTdw5gdgEd1RV6LuSWA7ksH9kZBK6ZBfeLw1Y3tpTQJpS6TEvodWKqkZCxUtaJ2gZAIZAZCiKqK8xA7929AXJ4uhFw5yfHZCW2xkHo"   # <-- IMPORTANT: replace with your actual token

WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ===== HELPER: SEND TEXT MESSAGE =====
def send_text(to, text):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    requests.post(WHATSAPP_API_URL, headers=headers, json=data)

# ===== MAIN MENU (3 buttons) =====
def send_main_menu(to):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🏋️ Welcome to GymBot! Choose an option:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "hours", "title": "📍 Hours & Location"}},
                    {"type": "reply", "reply": {"id": "plans", "title": "💪 Membership Plans"}},
                    {"type": "reply", "reply": {"id": "buy", "title": "💰 Buy Membership"}}
                ]
            }
        }
    }
    requests.post(WHATSAPP_API_URL, headers=headers, json=data)

# ===== BACK TO MENU BUTTON (single button) =====
def send_back_button(to, info_text):
    # First send the detailed info as text
    send_text(to, info_text)
    # Then send a single button to go back
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🔙 What would you like to do?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "menu", "title": "🔙 Back to Main Menu"}}
                ]
            }
        }
    }
    requests.post(WHATSAPP_API_URL, headers=headers, json=data)

# ===== HANDLE BUTTON INTERACTIONS =====
def handle_button(to, button_id):
    if button_id == "hours":
        info = "🏋️ Gym Hours: 6 AM – 10 PM (Mon-Sat)\nClosed Sunday\n📍 Location: Main Street, near City Hospital"
        send_back_button(to, info)
    elif button_id == "plans":
        info = "💪 Membership Plans:\n\n1 Month: $30\n3 Months: $80\n12 Months: $280\n\nTo buy, tap 'Buy Membership' on main menu."
        send_back_button(to, info)
    elif button_id == "buy":
        info = "💰 Payment Instructions:\n\nBank: ABC Bank\nAccount: 1234-5678-90\nName: Gym Owner\n\nSend payment & share screenshot here. We'll activate within 1 hour."
        send_back_button(to, info)
    elif button_id == "menu":
        send_main_menu(to)
    else:
        send_main_menu(to)

# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Raw webhook:", json.dumps(data, indent=2))  # for debugging in logs

    try:
        changes = data["entry"][0]["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            user_number = msg["from"]

            # Case 1: Button reply
            if "interactive" in msg and msg["interactive"]["type"] == "button_reply":
                button_id = msg["interactive"]["button_reply"]["id"]
                handle_button(user_number, button_id)

            # Case 2: Plain text message (for first contact or fallback)
            elif "text" in msg:
                # Any text triggers main menu
                send_main_menu(user_number)
    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "ok"}), 200

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == "gym123":
        return request.args.get("hub.challenge"), 200
    return "Verification failed", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
