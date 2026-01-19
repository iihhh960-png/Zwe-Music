import os, threading, requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.environ.get('BOT_TOKEN')

async def search_yt(query):
    # Search API (YouTube search via Invidious)
    try:
        url = f"https://invidious.privacydev.net/api/v1/search?q={query}&type=video"
        r = requests.get(url, timeout=10).json()
        return r[:5]
    except:
        return []

async def handle_start(update, context):
    await update.message.reply_text(" Zwe Music Downloader!\nသီချင်းနာမည် ပို့ပေးပါ။")

async def handle_message(update, context):
    query = update.message.text
    context.user_data['last_q'] = query
    msg = await update.message.reply_text(" ရှာဖွေနေပါတယ်...")
    results = await search_yt(query)
    
    if not results:
        await msg.edit_text(" ရှာမတွေ့ပါ။ နောက်တစ်ကြိမ် ပြန်စမ်းပါ။")
        return

    kb = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['videoId']}")] for e in results]
    await msg.edit_text(" ရလဒ်များ -", reply_markup=InlineKeyboardMarkup(kb))

async def handle_button(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    
    if data[0] == "back":
        last_q = context.user_data.get('last_q')
        results = await search_yt(last_q)
        kb = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['videoId']}")] for e in results]
        await query.edit_message_text(" ရလဒ်များ -", reply_markup=InlineKeyboardMarkup(kb))
        return

    vid = data[1]
    if data[0] == "sel":
        kb = [[InlineKeyboardButton(" MP3", callback_data=f"mp3|{vid}"), InlineKeyboardButton(" MP4", callback_data=f"mp4|{vid}")],
              [InlineKeyboardButton(" နောက်သို့", callback_data="back")]]
        await query.edit_message_text("Format ရွေးပါ-", reply_markup=InlineKeyboardMarkup(kb))
        return

    await query.edit_message_text(" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    
    # Download via Cobalt API
    try:
        api_url = "https://api.cobalt.tools/api/json"
        payload = {"url": f"https://www.youtube.com/watch?v={vid}", "downloadMode": "audio" if data[0] == "mp3" else "video"}
        res = requests.post(api_url, json=payload, headers={"Accept": "application/json"}).json()
        
        file_url = res.get("url")
        file_name = f"{vid}.{'mp3' if data[0] == 'mp3' else 'mp4'}"
        
        with requests.get(file_url, stream=True) as r:
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024): f.write(chunk)
        
        with open(file_name, 'rb') as f:
            if data[0] == 'mp3': await query.message.reply_audio(audio=f)
            else: await query.message.reply_video(video=f)
        os.remove(file_name)
    except:
        await query.message.reply_text(" ဒေါင်းမရပါ။ Server ခဏပိတ်နေလို့ပါ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling()

if __name__ == '__main__':
    keep_alive()
    main()
