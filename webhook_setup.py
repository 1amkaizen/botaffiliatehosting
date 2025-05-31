
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan")

# Get webhook URL from environment variable (secret)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not WEBHOOK_URL:
    print("❌ WEBHOOK_URL environment variable tidak ditemukan!")
    print("\n📋 Langkah-langkah setup:")
    print("1. Buka tab 'Secrets' di workspace")
    print("2. Tambahkan secret baru:")
    print("   Key: WEBHOOK_URL")
    print("   Value: URL webhook Anda")
    print("\n🔗 Contoh URL webhook untuk berbagai platform:")
    print("   - Replit: https://your-repl-name.your-username.repl.co/webhook")
    print("   - Vercel: https://your-project.vercel.app/webhook")
    print("   - Netlify: https://your-site.netlify.app/webhook")
    print("   - Railway: https://your-app.railway.app/webhook")
    print("   - Render: https://your-app.onrender.com/webhook")
    print("   - Heroku: https://your-app.herokuapp.com/webhook")
    print("   - Custom domain: https://yourdomain.com/webhook")
    print("   - Ngrok (development): https://abc123.ngrok.io/webhook")
    print("\n💡 Setelah menambahkan secret, jalankan script ini lagi.")
    exit(1)

print(f"🔗 Setting webhook to: {WEBHOOK_URL}")

# Set webhook
url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
data = {"url": WEBHOOK_URL}

try:
    response = requests.post(url, data=data)
    result = response.json()
    print(f"📡 Webhook setup response: {result}")

    if result.get("ok"):
        print("✅ Webhook berhasil diset!")
    else:
        print(f"❌ Error setting webhook: {result.get('description')}")
        
        # Provide helpful error messages
        error_desc = result.get('description', '').lower()
        if 'failed to resolve host' in error_desc:
            print("\n💡 Tips troubleshooting:")
            print("- Pastikan URL webhook dapat diakses dari internet")
            print("- Untuk Replit: pastikan repl sedang berjalan")
            print("- Untuk Vercel: pastikan deployment berhasil")
            print("- Untuk custom domain: pastikan domain aktif dan SSL valid")
        elif 'bad webhook' in error_desc:
            print("\n💡 Tips troubleshooting:")
            print("- URL harus menggunakan HTTPS")
            print("- Pastikan format URL benar")
            print("- Pastikan endpoint /webhook ada di server")

except requests.exceptions.RequestException as e:
    print(f"❌ Network error: {e}")
    exit(1)

# Check webhook info
try:
    info_url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
    info_response = requests.get(info_url)
    webhook_info = info_response.json()
    
    if webhook_info.get("ok"):
        current_url = webhook_info.get("result", {}).get("url")
        if current_url:
            print(f"✅ Current webhook URL: {current_url}")
            print(f"📊 Pending updates: {webhook_info.get('result', {}).get('pending_update_count', 0)}")
        else:
            print("❌ No webhook is currently set")
    else:
        print("❌ Could not get webhook info")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Error getting webhook info: {e}")
