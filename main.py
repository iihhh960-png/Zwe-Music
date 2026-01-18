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
    context.user_data['last_query'] = query # ရှာဖွေမှုမှတ်ထားရန်
    await search_and_show_results(update, query)

async def search_and_show_results(update_or_query, text):
    # Search function
    ydl_opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch5:{text}", download=False)['entries']
            keyboard = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in results]
            
            if hasattr(update_or_query, 'message'):
                await update_or_query.message.reply_text(" သီချင်းရွေးချယ်ပါ -", reply_markup=InlineKeyboardMarkup(keyboard))
            else: # Callback query အတွက်
                await update_or_query.edit_message_text(" သီချင်းရွေးချယ်ပါ -", reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        msg = " ရှာမရပါ။"
        if hasattr(update_or_query, 'message'): await update_or_query.message.reply_text(msg)
        else: await update_or_query.edit_message_text(msg)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    action = data[0]

    if action == "back": # Back ခလုတ်နှိပ်လျှင်
        last_query = context.user_data.get('last_query')
        if last_query: await search_and_show_results(query, last_query)
        else: await query.edit_message_text("သီချင်းနာမည် ပြန်ပို့ပေးပါ။")
        return

    video_id = data[1]
    if action == "sel":
        keyboard = [
            [InlineKeyboardButton(" MP3", callback_data=f"mp3|{video_id}"),
             InlineKeyboardButton(" MP4", callback_data=f"mp4|{video_id}")],
            [InlineKeyboardButton(" နောက်သို့", callback_data="back")]
        ]
        await query.edit_message_text(text="Format ရွေးချယ်ပါ-", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await query.edit_message_text(text=" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    
    # Server ကိုယ်တိုင်ကနေ တိုက်ရိုက်ဒေါင်းမယ့်အပိုင်း
    file_ext = 'mp3' if action == 'mp3' else 'mp4'
    file_path = f"{video_id}.{file_ext}"
    
    ydl_opts = {
        'format': 'bestaudio/best' if action == 'mp3' else 'best',
        'outtmpl': video_id,
        'nocheckcertificate': True,
        'quiet': True,
    }
    if action == 'mp3':
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        
        with open(file_path, 'rb') as f:
            if action == 'mp3': await query.message.reply_audio(audio=f)
            else: await query.message.reply_video(video=f)
        os.remove(file_path)
    except Exception as e:
        await query.message.reply_text(" ဒေါင်းလုဒ်မရပါ။ YouTube က ပိတ်ထားလို့ ဖြစ်နိုင်ပါတယ်။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    keep_alive()
    main()
