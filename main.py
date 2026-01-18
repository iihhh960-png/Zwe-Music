import os
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
import yt_dlp

app = Flask('')
@app.route('/')
def home(): return "Bot is running with Cobalt API (No Cookies Needed)!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): threading.Thread(target=run, daemon=True).start()

# Render Environment Variables ထဲမှာ BOT_TOKEN ထည့်ထားပါ
TOKEN = os.environ.get('BOT_TOKEN')

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" Zwe Music & Video Downloader!\nသီချင်းနာမည် သို့မဟုတ် အဆိုတော်နာမည် ရိုက်ပို့ပေးပါ။ (Cookies မလိုပါ)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text(f" '{query}' ကို ရှာဖွေနေပါတယ်...")
    
    # ရှာဖွေရုံသက်သက်ဖြစ်လို့ Cookie မလိုအပ်ပါ
    ydl_opts = {
        'quiet': True, 'noplaylist': True, 'extract_flat': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            keyboard = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in results]
            await msg.edit_text(" ရလဒ်များ -", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await msg.edit_text(" ရှာဖွေလို့မရပါ။ ခဏနေမှ ပြန်စမ်းကြည့်ပါ။")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    action, video_id = data[0], data[1]
    target_url = f"https://www.youtube.com/watch?v={video_id}"

    if action == "sel":
        keyboard = [[InlineKeyboardButton(" MP3 (Audio)", callback_data=f"mp3|{video_id}"),
                     InlineKeyboardButton(" MP4 (Video)", callback_data=f"mp4|{video_id}")]]
        await query.edit_message_text(text="ဘယ်လို Format နဲ့ ဒေါင်းမလဲ? -", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await query.edit_message_text(text=" Cobalt Server မှတစ်ဆင့် ဒေါင်းလုဒ်ဆွဲနေပါတယ်...")

    # Cobalt API သုံးပြီး ဒေါင်းလုဒ်ဆွဲခြင်း (ဒါကြောင့် Cookie မလိုတာပါ)
    api_url = "https://api.cobalt.tools/api/json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "url": target_url,
        "downloadMode": "audio" if action == "mp3" else "video",
        "videoQuality": "720"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        result = response.json()
        
        if result.get("status") in ["stream", "redirect"]:
            file_url = result.get("url")
            file_ext = "mp3" if action == "mp3" else "mp4"
            file_name = f"{video_id}.{file_ext}"
            
            # ဒေါင်းလုဒ်ဆွဲခြင်း
            r = requests.get(file_url, stream=True)
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            
            # Telegram သို့ ပို့ခြင်း
            with open(file_name, 'rb') as f:
                if action == "mp3": await query.message.reply_audio(audio=f)
                else: await query.message.reply_video(video=f)
            
            os.remove(file_name) # Server နေရာလွတ်စေရန် ပြန်ဖျက်ခြင်း
        else:
            await query.message.reply_text(" ဒေါင်းလုဒ်ဆွဲ၍ မရပါ။ နောက်တစ်ပုဒ် စမ်းကြည့်ပါ။")
    except Exception:
        await query.message.reply_text(" Server မအားသေးလို့ပါ။ ခဏနေမှ ပြန်စမ်းပါ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    keep_alive()
    main()
