
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from data_hosting import HOSTING_OPTIONS
from .models import BotLog
from dotenv import load_dotenv

load_dotenv()

# Global dict to track user state
user_state = {}

def log_user_action(update: Update, action: str, command: str = None):
    """Log user interactions to Django model"""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    
    BotLog.objects.create(
        user_id=user.id if user else None,
        username=user.username if user else None,
        first_name=user.first_name if user else None,
        last_name=user.last_name if user else None,
        chat_type=chat.type if chat else None,
        message_text=message.text if message else None,
        command=command,
        action=action
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, "start_command", "/start")
    
    if not update.effective_chat or not update.message:
        return
        
    if not update.effective_user:
        await update.message.reply_text("Maaf, tidak dapat mengidentifikasi pengguna.")
        return
        
    chat_type = update.effective_chat.type
    
    if chat_type in ['group', 'supergroup', 'channel']:
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

# ... (copy semua handler lainnya dari bot_hosting.py dengan modifikasi untuk Django)

# Initialize Telegram bot
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan. Pastikan sudah diset di .env atau environment variables.")

telegram_app = ApplicationBuilder().token(TOKEN).build()

def setup_bot_handlers():
    """Setup all bot handlers"""
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("help", help_command))
    # Tambahkan handler lainnya di sini
    
setup_bot_handlers()
