from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from data_hosting import HOSTING_OPTIONS

# Global dict to track user state
user_state = {}

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

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("paket", paket_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    print("Bot is running...")
    app.run_polling()