import os
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
import yt_dlp

app = Flask('')
@app.route('/')
def home(): return "Zwe Bot is LIVE!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.environ.get('BOT_TOKEN')

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" Zwe Music & Video Downloader!\nသီချင်းနာမည် ရိုက်ပို့ပေးပါ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text(f" '{query}' ကို ရှာဖွေနေပါတယ်...")
    
    # yt-dlp နဲ့ တိုက်ရိုက်ရှာဖွေခြင်း (API မလိုပါ)
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'extract_flat': True,
        'force_generic_extractor': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            if not search_results:
                await msg.edit_text(" ဘာမှရှာမတွေ့ပါ။")
                return
            
            keyboard = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in search_results]
            await msg.edit_text(" သီချင်းရွေးချယ်ပါ -", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await msg.edit_text(" ရှာဖွေမှု အဆင်မပြေပါ။ ခဏနေမှ ပြန်စမ်းပါ။")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    action, video_id = data[0], data[1]
    
    if action == "sel":
        keyboard = [[InlineKeyboardButton(" MP3", callback_data=f"mp3|{video_id}"),
                     InlineKeyboardButton(" MP4", callback_data=f"mp4|{video_id}")]]
        await query.edit_message_text(text="ဘယ်လို Format နဲ့ ဒေါင်းမလဲ?-", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await query.edit_message_text(text=" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    
    # Cobalt API သုံးပြီး ဒေါင်းလုဒ်ဆွဲခြင်း
    api_url = "https://api.cobalt.tools/api/json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "downloadMode": "audio" if action == "mp3" else "video",
        "videoQuality": "720"
    }
    
    try:
        res = requests.post(api_url, json=payload, headers=headers).json()
        if res.get("status") in ["stream", "redirect"]:
            file_url = res.get("url")
            file_ext = "mp3" if action == "mp3" else "mp4"
            file_name = f"{video_id}.{file_ext}"
            
            r = requests.get(file_url, stream=True)
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            
            with open(file_name, 'rb') as f:
                if action == "mp3": await query.message.reply_audio(audio=f)
                else: await query.message.reply_video(video=f)
            os.remove(file_name)
        else:
            await query.message.reply_text(" ဒေါင်းလုဒ်ဆွဲလို့ မရပါ။ နောက်တစ်ပုဒ် စမ်းကြည့်ပါ။")
    except:
        await query.message.reply_text(" Server အလုပ်မလုပ်ပါ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    keep_alive()
    main()
