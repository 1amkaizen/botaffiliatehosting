
#!/usr/bin/env python3
"""
Deployment Helper untuk Bot Telegram
Mendukung berbagai platform hosting
"""

import os
from dotenv import load_dotenv

load_dotenv()

def show_deployment_guide():
    print("🚀 Panduan Deployment Bot Telegram")
    print("=" * 50)
    
    print("\n📝 File yang diperlukan untuk deployment:")
    print("- bot_hosting.py (main app)")
    print("- data_hosting.py")
    print("- data/ folder (berisi hosting packages)")
    print("- templates/ folder (berisi logs.html)")
    print("- requirements.txt atau pyproject.toml")
    
    print("\n🔧 Environment Variables yang diperlukan:")
    print("- BOT_TOKEN: Token bot Telegram Anda")
    print("- WEBHOOK_URL: URL webhook lengkap (contoh: https://yourapp.com/webhook)")
    
    print("\n🌐 Platform Hosting yang Didukung:")
    
    # Replit
    print("\n1. 🟢 REPLIT (Recommended)")
    print("   - URL: https://your-repl-name.your-username.repl.co/webhook")
    print("   - Setup: Sudah otomatis dengan file .replit")
    print("   - Secrets: Gunakan tab Secrets untuk BOT_TOKEN dan WEBHOOK_URL")
    
    # Vercel
    print("\n2. 🔵 VERCEL")
    print("   - URL: https://your-project.vercel.app/webhook")
    print("   - Setup: Buat vercel.json:")
    print('   {')
    print('     "functions": {')
    print('       "bot_hosting.py": {')
    print('         "runtime": "python3.9"')
    print('       }')
    print('     },')
    print('     "routes": [')
    print('       {"src": "/(.*)", "dest": "/bot_hosting.py"}')
    print('     ]')
    print('   }')
    
    # Railway
    print("\n3. 🚂 RAILWAY")
    print("   - URL: https://your-app.railway.app/webhook")
    print("   - Setup: Otomatis detect Python")
    print("   - Variables: Set di Railway dashboard")
    
    # Render
    print("\n4. 🎨 RENDER")
    print("   - URL: https://your-app.onrender.com/webhook")
    print("   - Setup: Web Service dengan Python environment")
    print("   - Start Command: python bot_hosting.py")
    
    # Heroku
    print("\n5. 🟣 HEROKU")
    print("   - URL: https://your-app.herokuapp.com/webhook")
    print("   - Setup: Buat Procfile:")
    print("   web: python bot_hosting.py")
    
    # Custom/VPS
    print("\n6. 🖥️  CUSTOM/VPS")
    print("   - URL: https://yourdomain.com/webhook")
    print("   - Setup: Install Python, dependencies, setup reverse proxy")
    print("   - SSL: Pastikan HTTPS aktif (Let's Encrypt)")
    
    print("\n🔄 Langkah deployment umum:")
    print("1. Push code ke repository Git")
    print("2. Connect repository ke platform hosting")
    print("3. Set environment variables (BOT_TOKEN, WEBHOOK_URL)")
    print("4. Deploy aplikasi")
    print("5. Jalankan python webhook_setup.py untuk set webhook")
    
    print("\n✅ Verifikasi deployment:")
    print("- Akses /health endpoint untuk cek status")
    print("- Akses /test endpoint untuk cek konfigurasi")
    print("- Test bot di Telegram")
    
if __name__ == "__main__":
    show_deployment_guide()
