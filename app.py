from flask import Flask, request, jsonify
import requests
import json
import traceback

app = Flask(__name__)

# ===== CONFIG =====
PHONE_NUMBER_ID = "1059667987236268"
ACCESS_TOKEN = "EAAgSVdSxtf0BRW5gLOWeHxUT75mxtRcqnFVTUPpZBVzXbVEmL9pZAAdZANI0Ndqd2n87qnMZAVgL1DLlz8FjH2RFD9cxTy8unELQdar1d2NTBOo8zjtoZC88bpjseKET2mVeHUYBZBku5rnZCqZAgL5UyPn17Fk4ofwrxnfOowwsTJv1Cgs2I3Pvpu0YahTdw5gdgEd1RV6LuSWA7ksH9kZBK6ZBfeLw1Y3tpTQJpS6TEvodWKqkZCxUtaJ2gZAIZAZCiKqK8xA7929AXJ4uhFw5yfHZCW2xkHo"   # <-- GENERATE NEW ONE FROM META

WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

def send_request(url, headers, data):
    """Helper to log request/response"""
    print(f"Sending to {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2)}")
    resp = requests.post(url, headers=headers, json=data)
    print(f"Response status: {resp.status_code}")
    print(f"Response body: {resp.text}")
    return resp

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
    send_request(WHATSAPP_API_URL, headers, data)

def send_back_menu(to, info_text):
    # First send the info as text
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    text_data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": info_text}}
    send_request(WHATSAPP_API_URL, headers, text_data)
    
    # Then send a single back button
    back_data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🔙 What would you like to do?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "menu", "title": "🔙 Main Menu"}}
                ]
            }
        }
    }
    send_request(WHATSAPP_API_URL, headers, back_data)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("\n=== INCOMING WEBHOOK ===")
    print(json.dumps(data, indent=2))
    print("========================\n")
    
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])
        
        if not messages:
            return jsonify({"status": "ok"}), 200
        
        msg = messages[0]
        user_number = msg["from"]
        
        # === FORCED TEST: send a plain text message first ===
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
        test_data = {"messaging_product": "whatsapp", "to": user_number, "type": "text", "text": {"body": "🔧 Bot received your message. Now loading menu..."}}
        requests.post(WHATSAPP_API_URL, headers=headers, json=test_data)
        # ====================================================
        
        # Now try to send the main menu (buttons)
        send_main_menu(user_number)
        
    except Exception as e:
        print("ERROR in webhook:")
        traceback.print_exc()
    
    return jsonify({"status": "ok"}), 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == "gym123":
        return challenge, 200
    return "Verification failed", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
