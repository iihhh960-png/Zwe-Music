import os
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

# Render အတွက် Bot နိုးနေအောင် လုပ်ပေးတဲ့အပိုင်း
app = Flask('')
@app.route('/')
def home(): return "Zwe Bot is running without YouTube Cookies!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.environ.get('BOT_TOKEN')

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" Zwe Music & Video Downloader မှ ကြိုဆိုပါတယ်!\n(YouTube Cookie မလိုသော Version)\n\nသီချင်းနာမည် သို့မဟုတ် အဆိုတော်နာမည် ရိုက်ပို့ပေးပါ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text(f" '{query}' ကို ရှာဖွေနေပါတယ်...")
    
    # YouTube Search လုပ်ဖို့ Piped API ကို သုံးထားပါတယ်
    search_url = f"https://pipedapi.kavin.rocks/search?q={query}&filter=all"
    try:
        r = requests.get(search_url).json()
        results = [i for i in r['items'] if i['type'] == 'stream'][:5]
        if not results:
            await msg.edit_text(" ဘာသီချင်းမှ ရှာမတွေ့ပါ။ နာမည် ပြန်စစ်ပေးပါ။")
            return
            
        keyboard = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['url'].split('=')[-1]}")] for e in results]
        await msg.edit_text(" သီချင်းရွေးချယ်ပါ -", reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        await msg.edit_text(" ရှာဖွေလို့မရပါ။ ခဏနေမှ ပြန်စမ်းပါ။")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    action, video_id = data[0], data[1]
    target_url = f"https://www.youtube.com/watch?v={video_id}"

    # MP3 သို့မဟုတ် MP4 ရွေးခိုင်းခြင်း
    if action == "sel":
        keyboard = [[InlineKeyboardButton(" MP3 (Audio)", callback_data=f"mp3|{video_id}"),
                     InlineKeyboardButton(" MP4 (Video)", callback_data=f"mp4|{video_id}")]]
        await query.edit_message_text(text="ဘယ်လို Format နဲ့ ဒေါင်းမလဲ? ရွေးပေးပါ -", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await query.edit_message_text(text=" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")

    # Cobalt API သုံးပြီး Cookie မလိုဘဲ ဒေါင်းခြင်း
    api_url = "https://api.cobalt.tools/api/json"
    payload = {
        "url": target_url, 
        "downloadMode": "audio" if action == "mp3" else "video", 
        "videoQuality": "720"
    }
    
    try:
        res = requests.post(api_url, json=payload, headers={"Accept": "application/json", "Content-Type": "application/json"}).json()
        if res.get("status") in ["stream", "redirect"]:
            file_url = res.get("url")
            file_ext = "mp3" if action == "mp3" else "mp4"
            file_name = f"{video_id}.{file_ext}"
            
            # ဖိုင်ကို Server ပေါ်သို့ ယာယီဒေါင်းခြင်း
            with requests.get(file_url, stream=True) as r:
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024): 
                        if chunk: f.write(chunk)
            
            # Telegram ဆီသို့ ဖိုင်ပို့ပေးခြင်း
            with open(file_name, 'rb') as f:
                if action == "mp3": await query.message.reply_audio(audio=f)
                else: await query.message.reply_video(video=f)
            
            # ပို့ပြီးရင် ဖိုင်ကို ပြန်ဖျက်ခြင်း
            os.remove(file_name)
        else:
            await query.message.reply_text(" ဒေါင်းလုဒ်မရပါ။ တစ်ခြားတစ်ပုဒ် စမ်းကြည့်ပါ။")
    except:
        await query.message.reply_text(" Server Error ဖြစ်သွားပါပြီ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    keep_alive()
    main()
