from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# ========== CONFIGURATION ==========
# Replace with your actual values from Meta
PHONE_NUMBER_ID = "1059667987236268"   # Your test number ID
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"  # Paste your temporary token

# WhatsApp API endpoint
WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ========== GYM BOT RESPONSES ==========
def get_reply(user_text):
    user_text = user_text.strip().lower()
    
    # Simple keyword matching
    if user_text in ["1", "hours", "timing", "open"]:
        return "🏋️ Gym hours: 6 AM – 10 PM (Mon-Sat). Closed Sunday. Location: Main Street, near City Hospital."
    
    elif user_text in ["2", "plans", "membership", "price"]:
        return ("💪 Membership plans:\n"
                "1 Month: $30\n"
                "3 Months: $80\n"
                "12 Months: $280\n"
                "Send PLAN1, PLAN3, or PLAN12 to buy.")
    
    elif user_text in ["3", "buy", "purchase", "pay"]:
        return ("💰 To buy a membership, send payment to:\n"
                "Bank: ABC Bank\n"
                "Account: 1234-5678-90\n"
                "Name: Gym Owner\n"
                "Then share screenshot here. We'll activate within 1 hour.")
    
    elif user_text in ["4", "contact", "owner", "help"]:
        return ("📞 Contact owner: +92 331 1353491 (WhatsApp only, 10 AM – 6 PM)")
    
    elif "plan1" in user_text:
        return "You selected 1 Month plan: $30. Send payment to the bank account above and share screenshot."
    
    elif "plan3" in user_text:
        return "You selected 3 Months plan: $80. Send payment to the bank account above and share screenshot."
    
    elif "plan12" in user_text:
        return "You selected 12 Months plan: $280. Send payment to the bank account above and share screenshot."
    
    else:
        return ("Welcome to GymBot! 🏋️\n"
                "Type a number:\n"
                "1 – Hours & location\n"
                "2 – Membership plans\n"
                "3 – Buy now\n"
                "4 – Contact owner")

# ========== FUNCTION TO SEND WHATSAPP MESSAGE ==========
def send_whatsapp_message(to_number, text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

# ========== WEBHOOK TO RECEIVE INCOMING MESSAGES ==========
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    # Log incoming message for debugging
    print("Received:", json.dumps(data, indent=2))
    
    try:
        # Extract user's message and phone number
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            msg = messages[0]
            user_number = msg.get("from")  # User's WhatsApp number
            user_text = msg.get("text", {}).get("body", "")
            
            # Get bot reply
            reply_text = get_reply(user_text)
            
            # Send reply back to user
            send_whatsapp_message(user_number, reply_text)
    except Exception as e:
        print("Error:", e)
    
    return jsonify({"status": "ok"}), 200

# ========== VERIFICATION ENDPOINT (FOR META WEBHOOK SETUP) ==========
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = "gym123"  # You can change this, but remember it
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == verify_token:
        print("Webhook verified!")
        return challenge, 200
    else:
        return "Verification failed", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)