import os
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
import yt_dlp

# --- Render Web Server (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    threading.Thread(target=run, daemon=True).start()

# --- Configuration ---
TOKEN = '8514502979:AAGemVEqrs6BaaMM6iawm-A0vN8AJsCVXGk'

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" Zwe Music Downloader မှ ကြိုဆိုပါတယ်!\n\nသီချင်းနာမည် ရိုက်ပို့ပေးပါ ခင်ဗျာ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text(f" '{query}' ကို ရှာဖွေနေပါတယ်...")
    
    ydl_opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
    except Exception as e:
        await msg.edit_text(" ရှာဖွေမှု အဆင်မပြေပါဘူး။")
        return

    if not results:
        await msg.edit_text(" ဘာမှ ရှာမတွေ့ပါဘူး။")
        return
        
    keyboard = [[InlineKeyboardButton(e['title'][:50], callback_data=e['id'])] for e in results]
    await msg.edit_text(" သီချင်းရွေးချယ်ပါ -", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    video_id = query.data
    await query.edit_message_text(text=" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    
    file_path = f"{video_id}.mp3"
    # Render ပေါ်က FFmpeg လမ်းကြောင်းအတိအကျ
    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': video_id,
        'ffmpeg_location': ffmpeg_path,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        
        await query.message.reply_audio(audio=open(file_path, 'rb'), title="Downloaded by Zwe Music")
        os.remove(file_path)
    except Exception as e:
        print(f"Error: {e}")
        await query.message.reply_text(f" ဒေါင်းလုဒ်ဆွဲလို့ မရပါ။")

def main():
    keep_alive()
    # Conflict မဖြစ်အောင် drop_pending_updates ကို True ထားပါသည်
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    
    print("Bot is starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
