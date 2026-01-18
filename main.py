import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

# --- Render အတွက် Port ဖွင့်ပေးရန် (Flask) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- Telegram Bot Code ---
TOKEN = '8514502979:AAGemVEqrs6BaaMM6iawm-A0vN8AJsCVXGk'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text(f" '{query}' ကို ရှာဖွေနေပါတယ်...")

    ydl_opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            results = info['entries']
        except Exception:
            await msg.edit_text("ရှာဖွေမှု အဆင်မပြေပါဘူး။")
            return

    if not results:
        await msg.edit_text("ဘာမှ ရှာမတွေ့ပါဘူး။")
        return

    keyboard = [[InlineKeyboardButton(entry['title'][:50], callback_data=entry['id'])] for entry in results]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await msg.edit_text("အဆိုတော်နှင့် သီချင်းကို ရွေးချယ်ပါ -", reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    video_id = query.data
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    await query.edit_message_text(text=" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")

    file_path = f"{video_id}.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': video_id,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await query.message.reply_audio(audio=open(file_path, 'rb'))
        os.remove(file_path)
    except Exception as e:
        await query.message.reply_text("အမှားအယွင်းရှိလို့ ပြန်ကြိုးစားကြည့်ပါ။")

def main():
    app_tg = Application.builder().token(TOKEN).build()
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_tg.add_handler(CallbackQueryHandler(handle_button))
    print("Bot is starting...")
    app_tg.run_polling()

if __name__ == '__main__':
    keep_alive() # Render Port ကို စတင်ဖွင့်ခြင်း
    main() # Telegram Bot ကို စတင်ဖွင့်ခြင်း
