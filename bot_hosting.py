
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from data_hosting import HOSTING_OPTIONS
import json
import os
from dotenv import load_dotenv
from flask import Flask, request

# Global dict to track user state
user_state = {}

# Flask app for webhook
app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Web Hosting", "VPS Hosting", "Cloud Hosting"]], one_time_keyboard=True)
    await update.message.reply_text(
        "Halo! Selamat datang di layanan hosting kami.\n"
        "Ketik /help untuk info bantuan.\n\n"
        "Pilih jenis hosting yang ingin kamu beli:",
        reply_markup=reply_markup
    )
    user_state[update.effective_user.id] = {"step": "jenis"}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Panduan Bot Hosting*\n\n"
        "/start - Memulai pemilihan paket hosting\n"
        "/paket - Memilih paket hosting\n"
        "/help - Menampilkan pesan bantuan ini\n\n"
        "Setelah memilih jenis hosting, kamu akan diminta memilih durasi paket.\n"
        "Kemudian, akan ditampilkan pilihan paket lengkap dengan harga dan fitur."
    )
    await update.message.reply_markdown(help_text)

async def paket_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sama seperti start tapi lebih singkat
    reply_markup = ReplyKeyboardMarkup([["Web Hosting", "VPS Hosting", "Cloud Hosting"]], one_time_keyboard=True)
    await update.message.reply_text("Silakan pilih jenis hosting:", reply_markup=reply_markup)
    user_state[update.effective_user.id] = {"step": "jenis"}

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    state = user_state.get(user_id, {})

    if state.get("step") == "jenis":
        if text in HOSTING_OPTIONS:
            user_state[user_id] = {"step": "durasi", "jenis": text}
            durations = list(HOSTING_OPTIONS[text].keys())
            reply_markup = ReplyKeyboardMarkup([[d] for d in durations], one_time_keyboard=True)
            await update.message.reply_text("Pilih durasi paket:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Mohon pilih jenis hosting yang valid.")

    elif state.get("step") == "durasi":
        jenis = state.get("jenis")
        if jenis and text in HOSTING_OPTIONS[jenis]:
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

# Initialize the bot application
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan. Pastikan sudah diset di .env atau environment variables.")

# Create bot application
bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("help", help_command))
bot_app.add_handler(CommandHandler("paket", paket_command))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

@app.route('/')
def health_check():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    try:
        # Get the JSON data from the request
        json_data = request.get_json()
        
        if json_data:
            # Create an Update object from the JSON data
            update = Update.de_json(json_data, bot_app.bot)
            
            # Process the update
            bot_app.update_queue.put_nowait(update)
        
        return "OK", 200
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return "Error", 500

if __name__ == "__main__":
    import asyncio
    
    # Start the bot's update processing in background
    async def start_bot():
        await bot_app.initialize()
        await bot_app.start()
        # Start processing updates
        await bot_app.updater.start_polling()
    
    # Run the bot initialization in background
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())
    
    print("Bot webhook server is running...")
    app.run(host="0.0.0.0", port=5000, debug=False)
