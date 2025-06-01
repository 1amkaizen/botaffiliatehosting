import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your Replit app URL + /webhook

if not TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL tidak ditemukan. Set ke https://your-repl-name.your-username.repl.co/webhook")

# Set webhook
url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
data = {"url": WEBHOOK_URL}

response = requests.post(url, data=data)
print(f"Webhook setup response: {response.json()}")

# Check webhook info
info_url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
info_response = requests.get(info_url)
print(f"Webhook info: {info_response.json()}")
```

becomes:

```python
# This file is not needed for polling mode
# If you want to use webhooks later, you can implement the webhook setup here
```

```
</replit_final_file>