
import os
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from threading import Thread

class Command(BaseCommand):
    help = 'Start the Django server with bot webhook'

    def handle(self, *args, **options):
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hosting_bot.settings')
        
        # Initialize Django
        get_wsgi_application()
        
        # Run Django development server
        from django.core.management import execute_from_command_line
        port = os.getenv("PORT", "5000")
        
        self.stdout.write(
            self.style.SUCCESS(f'🤖 Django Bot server starting on port {port}...')
        )
        self.stdout.write(f"📊 Access dashboard at: http://0.0.0.0:{port}")
        self.stdout.write(f"🔗 Webhook endpoint: http://0.0.0.0:{port}/webhook")
        
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])
