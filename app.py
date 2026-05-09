from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# ========== CONFIGURATION ==========
PHONE_NUMBER_ID = "1059667987236268"
ACCESS_TOKEN = "EAAgSVdSxtf0BRW5gLOWeHxUT75mxtRcqnFVTUPpZBVzXbVEmL9pZAAdZANI0Ndqd2n87qnMZAVgL1DLlz8FjH2RFD9cxTy8unELQdar1d2NTBOo8zjtoZC88bpjseKET2mVeHUYBZBku5rnZCqZAgL5UyPn17Fk4ofwrxnfOowwsTJv1Cgs2I3Pvpu0YahTdw5gdgEd1RV6LuSWA7ksH9kZBK6ZBfeLw1Y3tpTQJpS6TEvodWKqkZCxUtaJ2gZAIZAZCiKqK8xA7929AXJ4uhFw5yfHZCW2xkHo"   # <-- REPLACE WITH YOUR REAL TOKEN

WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ========== HELPER: SEND TEXT MESSAGE ==========
def send_text(to_number, text):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(WHATSAPP_API_URL, headers=headers, json=data)

# ========== HELPER: SEND INTERACTIVE BUTTON MENU ==========
def send_main_menu(to_number):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🏋️ Welcome to GymBot! Choose an option:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "hours", "title": "📍 Hours & Location"}},
                    {"type": "reply", "reply": {"id": "plans", "title": "💪 Membership Plans"}},
                    {"type": "reply", "reply": {"id": "buy", "title": "💰 Buy Membership"}},
                    {"type": "reply", "reply": {"id": "contact", "title": "📞 Contact Owner"}}
                ]
            }
        }
    }
    requests.post(WHATSAPP_API_URL, headers=headers, json=data)

# ========== SEND BACK TO MENU BUTTON ==========
def send_back_menu(to_number, text_message):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    # First send the detailed text
    send_text(to_number, text_message)
    # Then send a small menu button as a separate interactive message
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🔙 Go back to main menu?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "menu", "title": "🔙 Main Menu"}}
                ]
            }
        }
    }
    requests.post(WHATSAPP_API_URL, headers=headers, json=data)

# ========== BOT RESPONSE LOGIC ==========
def handle_interaction(to_number, button_id):
    if button_id == "hours":
        reply = "🏋️ Gym Hours: 6 AM – 10 PM (Mon-Sat). Closed Sunday.\n📍 Location: Main Street, near City Hospital."
        send_back_menu(to_number, reply)
    
    elif button_id == "plans":
        reply = ("💪 Membership Plans:\n\n"
                 "1 Month: $30\n"
                 "3 Months: $80\n"
                 "12 Months: $280\n\n"
                 "To purchase, tap 'Buy Membership' on main menu.")
        send_back_menu(to_number, reply)
    
    elif button_id == "buy":
        reply = ("💰 Payment Instructions:\n\n"
                 "Bank: ABC Bank\n"
                 "Account: 1234-5678-90\n"
                 "Name: Gym Owner\n\n"
                 "Send payment and share screenshot here. We'll activate within 1 hour.")
        send_back_menu(to_number, reply)
    
    elif button_id == "contact":
        reply = "📞 Contact Owner: +92 331 1353491 (WhatsApp only, 10 AM – 6 PM)"
        send_back_menu(to_number, reply)
    
    elif button_id == "menu":
        send_main_menu(to_number)
    
    else:
        send_main_menu(to_number)

# ========== WEBHOOK RECEIVER ==========
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received:", json.dumps(data, indent=2))
    
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])
        
        if messages:
            msg = messages[0]
            user_number = msg["from"]
            
            # Check if it's a button interaction
            if "interactive" in msg and msg["interactive"]["type"] == "button_reply":
                button_id = msg["interactive"]["button_reply"]["id"]
                handle_interaction(user_number, button_id)
            
            # Or regular text message
            elif "text" in msg:
                user_text = msg["text"]["body"].strip().lower()
                # If user typed a number or keyword, map to buttons
                if user_text in ["1", "hours", "location", "timing"]:
                    handle_interaction(user_number, "hours")
                elif user_text in ["2", "plans", "membership", "price"]:
                    handle_interaction(user_number, "plans")
                elif user_text in ["3", "buy", "purchase", "pay"]:
                    handle_interaction(user_number, "buy")
                elif user_text in ["4", "contact", "owner"]:
                    handle_interaction(user_number, "contact")
                elif user_text in ["menu", "back", "main"]:
                    send_main_menu(user_number)
                else:
                    send_main_menu(user_number)
    
    except Exception as e:
        print("Error:", e)
    
    return jsonify({"status": "ok"}), 200

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == "gym123":
        return challenge, 200
    return "Verification failed", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
