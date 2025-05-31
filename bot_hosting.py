
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from data_hosting import HOSTING_OPTIONS
import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import asyncio
from datetime import datetime
import sqlite3
from threading import Thread

# Load environment variables
load_dotenv()

# Global dict to track user state
user_state = {}

# Flask app for webhook and logging interface
app = Flask(__name__)

# Database setup for logging
def init_db():
    conn = sqlite3.connect('bot_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            chat_type TEXT,
            message_text TEXT,
            command TEXT,
            action TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_user_action(update: Update, action: str, command: str = None):
    """Log user interactions to database"""
    conn = sqlite3.connect('bot_logs.db')
    cursor = conn.cursor()
    
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    
    cursor.execute('''
        INSERT INTO bot_logs (timestamp, user_id, username, first_name, last_name, 
                             chat_type, message_text, command, action)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        user.id if user else None,
        user.username if user else None,
        user.first_name if user else None,
        user.last_name if user else None,
        chat.type if chat else None,
        message.text if message else None,
        command,
        action
    ))
    
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, "start_command", "/start")
    
    # Check if we have valid update
    if not update.effective_chat or not update.message:
        return
        
    # Check if we have valid user (important for groups)
    if not update.effective_user:
        await update.message.reply_text("Maaf, tidak dapat mengidentifikasi pengguna.")
        return
        
    # Check if this is a group/channel
    chat_type = update.effective_chat.type
    
    if chat_type in ['group', 'supergroup', 'channel']:
        # In groups/channels, don't use custom keyboard
        await update.message.reply_text(
            "🤖 *Bot Hosting Services*\n\n"
            "Halo! Selamat datang di layanan hosting kami.\n"
            "Gunakan perintah berikut untuk berinteraksi:\n\n"
            "• /start - Memulai pemilihan paket\n"
            "• /webhosting - Lihat paket Web Hosting\n"
            "• /vpshosting - Lihat paket VPS Hosting\n"
            "• /cloudhosting - Lihat paket Cloud Hosting\n"
            "• /help - Bantuan lengkap\n\n"
            "Ketik salah satu perintah di atas untuk mulai!",
            parse_mode='Markdown'
        )
    else:
        # Private chat - use keyboard
        reply_markup = ReplyKeyboardMarkup([["Web Hosting", "VPS Hosting", "Cloud Hosting"]], one_time_keyboard=True)
        await update.message.reply_text(
            "Halo! Selamat datang di layanan hosting kami.\n"
            "Ketik /help untuk info bantuan.\n\n"
            "Pilih jenis hosting yang ingin kamu beli:",
            reply_markup=reply_markup
        )
    
    user_state[update.effective_user.id] = {"step": "jenis"}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, "help_command", "/help")
    
    if not update.message:
        return
        
    help_text = (
        "🤖 *Panduan Bot Hosting*\n\n"
        "/start - Memulai pemilihan paket hosting\n"
        "/paket - Memilih paket hosting\n"
        "/webhosting - Lihat paket Web Hosting\n"
        "/vpshosting - Lihat paket VPS Hosting\n"
        "/cloudhosting - Lihat paket Cloud Hosting\n"
        "/help - Menampilkan pesan bantuan ini\n\n"
        "Bot ini dapat digunakan di grup, channel, atau chat pribadi.\n"
        "Di grup/channel, gunakan perintah command langsung.\n"
        "Di chat pribadi, kamu bisa menggunakan keyboard atau command."
    )
    await update.message.reply_markdown(help_text)

async def paket_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, "paket_command", "/paket")
    
    if not update.effective_chat or not update.message or not update.effective_user:
        return
        
    # Sama seperti start tapi lebih singkat
    chat_type = update.effective_chat.type
    
    if chat_type in ['group', 'supergroup', 'channel']:
        await update.message.reply_text(
            "Gunakan salah satu perintah berikut:\n"
            "• /webhosting - Web Hosting\n"
            "• /vpshosting - VPS Hosting\n"
            "• /cloudhosting - Cloud Hosting"
        )
    else:
        reply_markup = ReplyKeyboardMarkup([["Web Hosting", "VPS Hosting", "Cloud Hosting"]], one_time_keyboard=True)
        await update.message.reply_text("Silakan pilih jenis hosting:", reply_markup=reply_markup)
    
    user_state[update.effective_user.id] = {"step": "jenis"}

async def webhosting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Web Hosting packages"""
    log_user_action(update, "webhosting_command", "/webhosting")
    
    if not update.effective_chat or not update.message:
        return
        
    print(f"Webhosting command triggered in chat: {update.effective_chat.type}")
    try:
        await show_hosting_packages(update, "Web Hosting")
    except Exception as e:
        print(f"Error in webhosting command: {e}")
        await update.message.reply_text("Maaf, terjadi kesalahan. Silakan coba lagi.")

async def vpshosting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show VPS Hosting packages"""
    log_user_action(update, "vpshosting_command", "/vpshosting")
    
    if not update.effective_chat or not update.message:
        return
        
    print(f"VPS hosting command triggered in chat: {update.effective_chat.type}")
    try:
        await show_hosting_packages(update, "VPS Hosting")
    except Exception as e:
        print(f"Error in vpshosting command: {e}")
        await update.message.reply_text("Maaf, terjadi kesalahan. Silakan coba lagi.")

async def cloudhosting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Cloud Hosting packages"""
    log_user_action(update, "cloudhosting_command", "/cloudhosting")
    
    if not update.effective_chat or not update.message:
        return
        
    print(f"Cloud hosting command triggered in chat: {update.effective_chat.type}")
    try:
        await show_hosting_packages(update, "Cloud Hosting")
    except Exception as e:
        print(f"Error in cloudhosting command: {e}")
        await update.message.reply_text("Maaf, terjadi kesalahan. Silakan coba lagi.")

async def show_hosting_packages(update: Update, hosting_type: str):
    """Display all packages for a hosting type"""
    log_user_action(update, f"viewed_{hosting_type.lower().replace(' ', '_')}_packages")
    
    if not update.message:
        return
        
    if hosting_type not in HOSTING_OPTIONS:
        await update.message.reply_text("Jenis hosting tidak ditemukan.")
        return
    
    response_text = f"📦 {hosting_type} - Semua Paket\n\n"
    
    for duration, packages in HOSTING_OPTIONS[hosting_type].items():
        response_text += f"🕒 {duration.capitalize()}:\n"
        for i, paket in enumerate(packages, 1):
            fitur_text = ", ".join(paket['fitur'][:3])  # Show first 3 features
            if len(paket['fitur']) > 3:
                fitur_text += f" + {len(paket['fitur']) - 3} lainnya"
            
            response_text += (
                f"{i}. {paket.get('nama', hosting_type)} - {paket['harga']}\n"
                f"   {fitur_text}\n"
                f"   🔗 {paket['link']}\n\n"
            )
    
    # Split long messages if needed
    if len(response_text) > 4000:
        # Send in chunks
        for duration, packages in HOSTING_OPTIONS[hosting_type].items():
            chunk_text = f"📦 {hosting_type} - {duration.capitalize()}\n\n"
            for i, paket in enumerate(packages, 1):
                fitur_text = ", ".join(paket['fitur'][:3])
                if len(paket['fitur']) > 3:
                    fitur_text += f" + {len(paket['fitur']) - 3} lainnya"
                
                chunk_text += (
                    f"{i}. {paket.get('nama', hosting_type)} - {paket['harga']}\n"
                    f"   {fitur_text}\n"
                    f"   🔗 {paket['link']}\n\n"
                )
            await update.message.reply_text(chunk_text, disable_web_page_preview=True)
    else:
        await update.message.reply_text(response_text, disable_web_page_preview=True)

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, "text_message")
    
    # Check if we have valid user and message
    if not update.effective_user or not update.message:
        print("Received update without user or message, skipping...")
        return
    
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check if text exists
    if not text:
        return
        
    state = user_state.get(user_id, {})
    chat_type = update.effective_chat.type

    # In groups/channels, only respond to private chat workflow
    if chat_type in ['group', 'supergroup', 'channel']:
        # Don't respond to random text in groups, only commands
        return

    if state.get("step") == "jenis":
        if text in HOSTING_OPTIONS:
            user_state[user_id] = {"step": "durasi", "jenis": text}
            durations = list(HOSTING_OPTIONS[text].keys())
            reply_markup = ReplyKeyboardMarkup([[d] for d in durations], one_time_keyboard=True)
            await update.message.reply_text("Pilih durasi paket:", reply_markup=reply_markup)
            log_user_action(update, f"selected_hosting_type", text)
        else:
            await update.message.reply_text("Mohon pilih jenis hosting yang valid.")

    elif state.get("step") == "durasi":
        jenis = state.get("jenis")
        if jenis and text in HOSTING_OPTIONS[jenis]:
            log_user_action(update, f"selected_duration", f"{jenis} - {text}")
            paket_list = HOSTING_OPTIONS[jenis][text]  # List paket
            for paket in paket_list:
                fitur_text = "\n".join([f"• {f}" for f in paket['fitur']])
                response = (
                    f"📦 *{paket.get('nama', jenis)}* - {text}\n\n"
                    f"💰 Harga: {paket['harga']}\n"
                    f"🔧 Fitur:\n{fitur_text}\n"
                    f"🔗 [Klik untuk beli]({paket['link']})"
                )
                await update.message.reply_markdown(response)
            user_state[user_id] = {"step": None}
        else:
            await update.message.reply_text("Mohon pilih durasi paket yang valid.")

    else:
        # Jika user ketik random pesan, kasih panduan
        await update.message.reply_text(
            "Ketik /start untuk memulai pemilihan paket atau /help untuk bantuan."
        )

# Initialize Telegram bot
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan. Pastikan sudah diset di .env atau environment variables.")

telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("paket", paket_command))
telegram_app.add_handler(CommandHandler("webhosting", webhosting_command))
telegram_app.add_handler(CommandHandler("vpshosting", vpshosting_command))
telegram_app.add_handler(CommandHandler("cloudhosting", cloudhosting_command))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

# Flask routes
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    try:
        # Get the update from Telegram
        update_data = request.get_json()
        if update_data:
            update = Update.de_json(update_data, telegram_app.bot)
            
            # Process the update asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(telegram_app.process_update(update))
            loop.close()
            
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def logs_dashboard():
    """Display bot usage logs"""
    conn = sqlite3.connect('bot_logs.db')
    cursor = conn.cursor()
    
    # Get recent logs
    cursor.execute('''
        SELECT timestamp, user_id, username, first_name, last_name, 
               chat_type, message_text, command, action
        FROM bot_logs 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''')
    logs = cursor.fetchall()
    
    # Get user statistics
    cursor.execute('''
        SELECT COUNT(DISTINCT user_id) as unique_users,
               COUNT(*) as total_interactions
        FROM bot_logs
    ''')
    stats = cursor.fetchone()
    
    # Get command usage statistics
    cursor.execute('''
        SELECT command, COUNT(*) as count
        FROM bot_logs 
        WHERE command IS NOT NULL
        GROUP BY command
        ORDER BY count DESC
    ''')
    command_stats = cursor.fetchall()
    
    conn.close()
    
    return render_template('logs.html', 
                         logs=logs, 
                         stats=stats, 
                         command_stats=command_stats)

@app.route('/api/stats')
def api_stats():
    """API endpoint for bot statistics"""
    conn = sqlite3.connect('bot_logs.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('''
        SELECT COUNT(DISTINCT user_id) as unique_users,
               COUNT(*) as total_interactions,
               DATE(timestamp) as date,
               COUNT(*) as daily_interactions
        FROM bot_logs
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        LIMIT 30
    ''')
    daily_stats = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        "daily_stats": [{"date": row[2], "interactions": row[3]} for row in daily_stats]
    })

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    print("Bot webhook server starting...")
    print("Access logs dashboard at: http://localhost:5000")
    print("Webhook endpoint: http://localhost:5000/webhook")
    
    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
