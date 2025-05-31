
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan")

# For Replit, the webhook URL will be your repl URL + /webhook
# Example: https://your-repl-name.your-username.repl.co/webhook
REPL_NAME = input("Enter your Repl name: ")
USERNAME = input("Enter your Replit username: ")
WEBHOOK_URL = f"https://{REPL_NAME}.{USERNAME}.repl.co/webhook"

print(f"Setting webhook to: {WEBHOOK_URL}")

# Set webhook
url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
data = {"url": WEBHOOK_URL}

response = requests.post(url, data=data)
result = response.json()
print(f"Webhook setup response: {result}")

if result.get("ok"):
    print("✅ Webhook set successfully!")
else:
    print(f"❌ Error setting webhook: {result.get('description')}")

# Check webhook info
info_url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
info_response = requests.get(info_url)
webhook_info = info_response.json()
print(f"Webhook info: {webhook_info}")

if webhook_info.get("result", {}).get("url"):
    print(f"✅ Current webhook URL: {webhook_info['result']['url']}")
else:
    print("❌ No webhook is currently set")
