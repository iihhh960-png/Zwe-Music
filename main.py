import os
import threading
import requests
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
    
    # API မသုံးဘဲ yt-dlp နဲ့ တိုက်ရိုက်ရှာမယ်
    ydl_opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            keyboard = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in search_results]
            await msg.edit_text(" သီချင်းရွေးချယ်ပါ -", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await msg.edit_text(f" ရှာမရပါ။ နောက်တစ်ကြိမ် ပြန်စမ်းပါ။")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    action, video_id = data[0], data[1]
    
    if action == "sel":
        keyboard = [[InlineKeyboardButton(" MP3", callback_data=f"mp3|{video_id}"),
                     InlineKeyboardButton(" MP4", callback_data=f"mp4|{video_id}")]]
        await query.edit_message_text(text="Format ရွေးချယ်ပါ-", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await query.edit_message_text(text=" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    
    # Cobalt API ကိုပဲ သုံးပြီး ဒေါင်းမယ် (ဒါက အကောင်းဆုံးမို့လို့ပါ)
    api_url = "https://api.cobalt.tools/api/json"
    payload = {
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "downloadMode": "audio" if action == "mp3" else "video",
        "videoQuality": "720"
    }
    
    try:
        res = requests.post(api_url, json=payload, headers={"Accept": "application/json"}).json()
        file_url = res.get("url")
        file_name = f"{video_id}.{'mp3' if action == 'mp3' else 'mp4'}"
        
        r = requests.get(file_url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk: f.write(chunk)
            
        with open(file_name, 'rb') as f:
            if action == "mp3": await query.message.reply_audio(audio=f)
            else: await query.message.reply_video(video=f)
        os.remove(file_name)
    except:
        await query.message.reply_text(" ဒေါင်းလုဒ်ဆွဲလို့ မရပါ။ Cobalt Server ပြဿနာပါ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    keep_alive()
    main()
