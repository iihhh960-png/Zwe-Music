import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
import yt_dlp

app = Flask('')
@app.route('/')
def home(): return "Zwe Bot is running!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.environ.get('BOT_TOKEN')

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" Zwe Music & Video Downloader!\nသီချင်းနာမည် ရိုက်ပို့ပေးပါ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text(f" '{query}' ကို ရှာဖွေနေပါတယ်...")
    
    ydl_opts = {
        'quiet': True, 'noplaylist': True, 'extract_flat': True,
        'cookiefile': 'cookies.txt',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            keyboard = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in results]
            await msg.edit_text(" သီချင်းရွေးချယ်ပါ -", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await msg.edit_text(" YouTube က ပိတ်ထားပါတယ်။ Cookie အသစ် ပြန်လဲပေးပါ။")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    action, video_id = data[0], data[1]

    if action == "sel":
        keyboard = [[InlineKeyboardButton(" MP3 (Audio)", callback_data=f"mp3|{video_id}"),
                     InlineKeyboardButton(" MP4 (Video)", callback_data=f"mp4|{video_id}")]]
        await query.edit_message_text(text="Format ရွေးပေးပါ -", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await query.edit_message_text(text=" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    file_ext = "mp3" if action == "mp3" else "mp4"
    file_path = f"{video_id}.{file_ext}"

    ydl_opts = {
        'format': 'bestaudio/best' if action == "mp3" else 'best[ext=mp4]/best',
        'outtmpl': video_id,
        'cookiefile': 'cookies.txt',
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    if action == "mp3":
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        
        with open(file_path, 'rb') as f:
            if action == "mp3": await query.message.reply_audio(audio=f)
            else: await query.message.reply_video(video=f)
        os.remove(file_path)
    except Exception:
        await query.message.reply_text(" ဒေါင်းလုဒ်မရပါ။ Cookie အသစ် ပြန်လဲပေးပါ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    keep_alive()
    main()
