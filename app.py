from flask import Flask, request, jsonify
import requests
import json
import time

app = Flask(__name__)

# ===== CONFIGURATION =====
# ⚠️ IMPORTANT: Replace with your actual details
PHONE_NUMBER_ID = "1059667987236268"
ACCESS_TOKEN = "EAAgSVdSxtf0BRWpSh2qcxZC2kh32cezwUkzxFzM6eW3jlsuL7Mye35foCVwIKWjYK7HCV2I1cnPJnemhdj349V7g0WQw7Whw7ZBzKDyb38hMlUY7Pyu5bVqN4TGcdhqRk3xaf4shtqnGCgNFbRwyqwigG0BP5x5DUgQDZCka0q9vh31AqbzZAqkWt4GP9VGZCHgZDZD"

WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ===== HELPER: SEND TEXT MESSAGE =====
def send_text(to, text):
    """Send a simple text message."""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    try:
        requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    except Exception as e:
        print(f"Error sending text: {e}")

# ===== MAIN MENU (3 buttons) =====
def send_main_menu(to):
    """Send the main menu with 3 interactive reply buttons."""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🏋️ Welcome to GymBot by Ahmed ! Always here for you. Please choose an option:"},
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
        requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    except Exception as e:
        print(f"Error sending menu: {e}")

# ===== BACK TO MENU BUTTON (Single Button) =====
def send_back_button(to, info_text):
    """
    Send a 'Back to Main Menu' button.
    First sends the detailed info as a text message, then sends a single button to go back.
    """
    # Send the detailed info as a text message
    send_text(to, info_text)

    # Send the single-button interactive message (with a 1-second delay)
    time.sleep(1)
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🔙 Main Menu"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "main_menu", "title": "🏠 Back to Main Menu"}}
                ]
            }
        }
    }
    try:
        requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    except Exception as e:
        print(f"Error sending back button: {e}")

# ===== HANDLE BUTTON INTERACTIONS =====
def handle_button(to, button_id):
    """Route button clicks to the appropriate action."""
    if button_id == "hours":
        info = "🏋️ Gym Hours: 6 AM – 10 PM (Mon-Sat)\nClosed on Sunday\n📍 Location: Main Street, near City Hospital."
        send_back_button(to, info)
    elif button_id == "plans":
        info = "💪 Membership Plans:\n\n1 Month: $30\n3 Months: $80\n12 Months: $280\n\nTo purchase, tap 'Buy Membership' from the main menu."
        send_back_button(to, info)
    elif button_id == "buy":
        info = "💰 Payment Instructions:\n\nBank: ABC Bank\nAccount: 1234-5678-90\nName: Gym Owner\n\nSend the payment and share a screenshot here. We'll activate your membership within 1 hour."
        send_back_button(to, info)
    elif button_id == "main_menu":
        send_main_menu(to)
    else:
        send_main_menu(to)

# ===== WEBHOOK HANDLER (GET for verification) =====
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Handle webhook verification from Meta."""
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == "gym123":
        return request.args.get("hub.challenge"), 200
    return "Verification failed", 403

# ===== WEBHOOK HANDLER (POST for incoming messages/buttons) =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received webhook data:", json.dumps(data, indent=2, ensure_ascii=False))  # Debug print

    try:
        # Parse the incoming event
        changes = data["entry"][0]["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])
        
        if not messages:
            return jsonify({"status": "ok"}), 200
        
        msg = messages[0]
        user_number = msg["from"]
        
        # Check for an interactive button reply
        if "interactive" in msg and msg["interactive"]["type"] == "button_reply":
            button_id = msg["interactive"]["button_reply"]["id"]
            handle_button(user_number, button_id)
        
        # Check for a plain text message (first contact or fallback)
        elif "text" in msg:
            # Any text message triggers the main menu
            send_main_menu(user_number)
    
    except Exception as e:
        print("Error in webhook:", e)
        import traceback
        traceback.print_exc()
        # Optionally, you could send a fallback message here
    
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
