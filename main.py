import os, threading, requests, re
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

app = Flask('')
@app.route('/')
def home(): return "Zwe Bot is LIVE!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.environ.get('BOT_TOKEN')

async def search_yt(query):
    # YouTube Block တာကျော်ဖို့ DuckDuckGo ကနေတစ်ဆင့် ရှာမယ်
    try:
        search_url = f"https://duckduckgo.com/html/?q=site:youtube.com+{query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(search_url, headers=headers, timeout=10).text
        v_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', r)
        
        results = []
        for vid in list(dict.fromkeys(v_ids))[:5]:
            results.append({"title": f"Video {vid}", "videoId": vid})
        return results
    except: return []

async def handle_start(update, context):
    await update.message.reply_text(" Zwe Multi-Downloader!\nသီချင်းနာမည်ဖြစ်စေ၊ Video Link ဖြစ်စေ ပို့ပေးပါ။")

async def handle_message(update, context):
    text = update.message.text
    if "http" in text:
        await download_video(update, text, "mp4")
        return

    context.user_data['last_q'] = text
    msg = await update.message.reply_text(" ရှာဖွေနေပါတယ်...")
    results = await search_yt(text)
    
    if not results:
        await msg.edit_text(" ရှာမတွေ့ပါ။ နာမည် အမှန်ပြန်ရိုက်ပေးပါ။")
        return

    kb = [[InlineKeyboardButton(f" ရလဒ် {i+1}", callback_data=f"sel|{e['videoId']}")] for i, e in enumerate(results)]
    await msg.edit_text(" ရလဒ်များ တွေ့ရှိသည် -", reply_markup=InlineKeyboardMarkup(kb))

async def handle_button(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    
    if data[0] == "back":
        last_q = context.user_data.get('last_q')
        results = await search_yt(last_q)
        kb = [[InlineKeyboardButton(f" ရလဒ် {i+1}", callback_data=f"sel|{e['videoId']}")] for i, e in enumerate(results)]
        await query.edit_message_text(" ရလဒ်များ -", reply_markup=InlineKeyboardMarkup(kb))
        return

    vid = data[1]
    if data[0] == "sel":
        kb = [[InlineKeyboardButton(" MP3", callback_data=f"mp3|{vid}"), 
               InlineKeyboardButton(" MP4", callback_data=f"mp4|{vid}")],
              [InlineKeyboardButton(" နောက်သို့", callback_data="back")]]
        await query.edit_message_text("Format ရွေးပါ-", reply_markup=InlineKeyboardMarkup(kb))
        return

    await query.edit_message_text(" ဒေါင်းလုဒ်ဆွဲနေပါပြီ...")
    await download_video(update, f"https://www.youtube.com/watch?v={vid}", data[0])

async def download_video(update, url, mode):
    # Cobalt API (Stable API)
    try:
        api_url = "https://api.cobalt.tools/api/json"
        payload = {"url": url, "downloadMode": "audio" if mode == "mp3" else "video"}
        res = requests.post(api_url, json=payload, headers={"Accept": "application/json"}, timeout=20).json()
        
        file_url = res.get("url")
        file_name = f"file.{'mp3' if mode == 'mp3' else 'mp4'}"
        
        with requests.get(file_url, stream=True) as r:
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024): f.write(chunk)
            
        with open(file_name, 'rb') as f:
            if mode == "mp3": await update.effective_message.reply_audio(audio=f)
            else: await update.effective_message.reply_video(video=f)
        os.remove(file_name)
    except:
        await update.effective_message.reply_text(" ဒေါင်းလုဒ်မရပါ။ Server ခဏပိတ်နေလို့ပါ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling()

if __name__ == '__main__':
    keep_alive()
    main()
