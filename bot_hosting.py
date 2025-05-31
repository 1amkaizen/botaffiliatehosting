from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from data_hosting import HOSTING_OPTIONS
import json
import os
from dotenv import load_dotenv

# Global dict to track user state
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if we have valid update
    if not update.effective_chat or not update.message:
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
    if not update.message:
        return
        
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
    if not update.effective_chat or not update.message:
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
    print(f"Webhosting command triggered in chat: {update.effective_chat.type}")
    try:
        await show_hosting_packages(update, "Web Hosting")
    except Exception as e:
        print(f"Error in webhosting command: {e}")
        await update.message.reply_text("Maaf, terjadi kesalahan. Silakan coba lagi.")

async def vpshosting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show VPS Hosting packages"""
    print(f"VPS hosting command triggered in chat: {update.effective_chat.type}")
    try:
        await show_hosting_packages(update, "VPS Hosting")
    except Exception as e:
        print(f"Error in vpshosting command: {e}")
        await update.message.reply_text("Maaf, terjadi kesalahan. Silakan coba lagi.")

async def cloudhosting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Cloud Hosting packages"""
    print(f"Cloud hosting command triggered in chat: {update.effective_chat.type}")
    try:
        await show_hosting_packages(update, "Cloud Hosting")
    except Exception as e:
        print(f"Error in cloudhosting command: {e}")
        await update.message.reply_text("Maaf, terjadi kesalahan. Silakan coba lagi.")

async def show_hosting_packages(update: Update, hosting_type: str):
    """Display all packages for a hosting type"""
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
    if not TOKEN:
        raise ValueError("BOT_TOKEN tidak ditemukan. Pastikan sudah diset di .env atau environment variables.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("paket", paket_command))
    app.add_handler(CommandHandler("webhosting", webhosting_command))
    app.add_handler(CommandHandler("vpshosting", vpshosting_command))
    app.add_handler(CommandHandler("cloudhosting", cloudhosting_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    print("Bot is running...")
    app.run_polling()