#!/usr/bin/env python3
"""
Django Telegram Bot Hosting Service
"""

import os
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hosting_bot.settings')

# Initialize Django
django.setup()

if __name__ == "__main__":
    # Run migrations first
    print("🔄 Running Django migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])

    # Get port from environment
    port = int(os.getenv("PORT", 5000))

    print(f"🤖 Django Bot webhook server starting on port {port}...")
    print(f"📊 Access logs dashboard at: http://0.0.0.0:{port}")
    print(f"🔗 Webhook endpoint: http://0.0.0.0:{port}/webhook")
    print(f"💚 Health check: http://0.0.0.0:{port}/health")
    print(f"🧪 Test endpoint: http://0.0.0.0:{port}/test")

    # Check if required environment variables are set
    from dotenv import load_dotenv
    load_dotenv()

    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        print(f"✅ Webhook URL configured: {webhook_url}")
    else:
        print("⚠️  WEBHOOK_URL not set - use webhook_setup.py to configure")

    # Run Django development server
    execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])