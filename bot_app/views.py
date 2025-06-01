
import json
import asyncio
import os
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from .models import BotLog
from .bot_handlers import setup_bot_handlers, telegram_app
from data_hosting import HOSTING_OPTIONS
from dotenv import load_dotenv

load_dotenv()

@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    """Handle incoming Telegram updates"""
    try:
        update_data = json.loads(request.body)
        print(f"Received webhook data: {update_data}")
        
        if update_data:
            update = Update.de_json(update_data, telegram_app.bot)
            
            # Process the update asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(telegram_app.process_update(update))
            loop.close()
            
        return JsonResponse({"status": "ok"})
    except Exception as e:
        print(f"Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def health_check(request):
    """Health check endpoint"""
    TOKEN = os.getenv("BOT_TOKEN")
    return JsonResponse({
        "status": "healthy",
        "bot_token_configured": bool(TOKEN),
        "database_accessible": True
    })

def logs_dashboard(request):
    """Display bot usage logs"""
    # Get recent logs
    logs = BotLog.objects.all()[:100]
    
    # Get user statistics
    unique_users = BotLog.objects.values('user_id').distinct().count()
    total_interactions = BotLog.objects.count()
    
    # Get command usage statistics
    command_stats = BotLog.objects.filter(
        command__isnull=False
    ).values('command').annotate(
        count=Count('command')
    ).order_by('-count')
    
    stats = (unique_users, total_interactions)
    
    return render(request, 'logs.html', {
        'logs': logs,
        'stats': stats,
        'command_stats': command_stats
    })

def api_stats(request):
    """API endpoint for bot statistics"""
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    
    # Get daily statistics
    daily_stats = BotLog.objects.extra(
        select={'date': 'DATE(timestamp)'}
    ).values('date').annotate(
        interactions=Count('id')
    ).order_by('-date')[:30]
    
    return JsonResponse({
        "daily_stats": [
            {"date": stat['date'], "interactions": stat['interactions']} 
            for stat in daily_stats
        ]
    })

def test_bot(request):
    """Test bot functionality"""
    TOKEN = os.getenv("BOT_TOKEN")
    return JsonResponse({
        "message": "Bot server is running!",
        "endpoints": {
            "dashboard": "/",
            "webhook": "/webhook",
            "health": "/health",
            "stats_api": "/api/stats"
        },
        "bot_info": {
            "token_configured": bool(TOKEN),
            "database_exists": True
        }
    })
