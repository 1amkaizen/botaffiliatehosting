import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telegram import Update
from telegram.ext import Application
from data_hosting import HOSTING_OPTIONS
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot
application = Application.builder().token(TOKEN).build()

async def handle_message(update: Update):
    """Handle incoming messages"""
    message = update.message
    user_id = update.effective_user.id
    text = message.text

    if text == "/start":
        await message.reply_text(
            "Halo! Selamat datang di layanan hosting kami.\n"
            "Ketik /help untuk info bantuan.\n\n"
            "Pilih jenis hosting yang ingin kamu beli:",
            reply_markup={"keyboard": [["Web Hosting", "VPS Hosting", "Cloud Hosting"]], "one_time_keyboard": True}
        )
        return

    if text == "/help":
        help_text = (
            "🤖 *Panduan Bot Hosting*\n\n"
            "/start - Memulai pemilihan paket hosting\n"
            "/paket - Memilih paket hosting\n"
            "/help - Menampilkan pesan bantuan ini\n\n"
            "Setelah memilih jenis hosting, kamu akan diminta memilih durasi paket.\n"
            "Kemudian, akan ditampilkan pilihan paket lengkap dengan harga dan fitur."
        )
        await message.reply_markdown(help_text)
        return

    # Handle hosting selection
    if text in HOSTING_OPTIONS:
        durations = list(HOSTING_OPTIONS[text].keys())
        await message.reply_text(
            "Pilih durasi paket:",
            reply_markup={"keyboard": [[d] for d in durations], "one_time_keyboard": True}
        )
        return

    # Handle duration selection
    for hosting_type, durations in HOSTING_OPTIONS.items():
        if text in durations:
            paket_list = HOSTING_OPTIONS[hosting_type][text]
            for paket in paket_list:
                fitur_text = "\n".join([f"• {f}" for f in paket['fitur']])
                response = (
                    f"📦 *{paket.get('nama', hosting_type)}* - {text}\n\n"
                    f"💰 Harga: {paket['harga']}\n"
                    f"🔧 Fitur:\n{fitur_text}\n"
                    f"🔗 [Klik untuk beli]({paket['link']})"
                )
                await message.reply_markdown(response)
            return

    await message.reply_text(
        "Ketik /start untuk memulai pemilihan paket atau /help untuk bantuan."
    )

@csrf_exempt
@require_POST
def webhook(request):
    """Handle incoming webhook requests from Telegram"""
    try:
        update = Update.de_json(json.loads(request.body), application.bot)
        application.loop.run_until_complete(handle_message(update))
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})