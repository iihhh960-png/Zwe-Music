import os, threading, requests, yt_dlp
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

app = Flask('')
@app.route('/')
def home(): return "Zwe Bot is LIVE!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.environ.get('BOT_TOKEN')

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" Zwe Music & Video Downloader!\nသီချင်းနာမည် ပို့ပေးပါ။")

async def search_yt(query):
    # Cookie မပါဘဲ yt-dlp နဲ့ တိုက်ရိုက်ရှာမယ်
    ydl_opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    context.user_data['last_q'] = query
    msg = await update.message.reply_text(" ရှာဖွေနေပါတယ်...")
    try:
        results = await search_yt(query)
        kb = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in results]
        await msg.edit_text(" ရလဒ်များ -", reply_markup=InlineKeyboardMarkup(kb))
    except:
        await msg.edit_text(" ရှာဖွေမှု အဆင်မပြေပါ။ ခဏနေမှ ပြန်စမ်းပါ။")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    action = data[0]

    if action == "back":
        last_q = context.user_data.get('last_q')
        if last_q:
            results = await search_yt(last_q)
            kb = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in results]
            await query.edit_message_text(" ရလဒ်များ -", reply_markup=InlineKeyboardMarkup(kb))
        return

    vid = data[1]
    if action == "sel":
        kb = [
            [InlineKeyboardButton(" MP3", callback_data=f"mp3|{vid}"), InlineKeyboardButton(" MP4", callback_data=f"mp4|{vid}")],
            [InlineKeyboardButton(" နောက်သို့", callback_data="back")]
        ]
        await query.edit_message_text("Format ရွေးပါ-", reply_markup=InlineKeyboardMarkup(kb))
        return

    await query.edit_message_text(" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    
    # YouTube က ပိတ်ထားရင် Cobalt API နဲ့ ပြောင်းဒေါင်းမယ်
    api_url = "https://api.cobalt.tools/api/json"
    payload = {
        "url": f"https://www.youtube.com/watch?v={vid}",
        "downloadMode": "audio" if action == "mp3" else "video",
        "videoQuality": "720"
    }
    
    try:
        r = requests.post(api_url, json=payload, headers={"Accept": "application/json"}).json()
        if r.get("status") in ["stream", "redirect"]:
            file_url = r.get("url")
            file_name = f"{vid}.{'mp3' if action == 'mp3' else 'mp4'}"
            
            with requests.get(file_url, stream=True) as res:
                with open(file_name, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=1024*1024): f.write(chunk)
            
            with open(file_name, 'rb') as f:
                if action == "mp3": await query.message.reply_audio(audio=f)
                else: await query.message.reply_video(video=f)
            os.remove(file_name)
        else:
            await query.message.reply_text(" ဒေါင်းလုဒ်မရပါ။ တစ်ခြားတစ်ပုဒ် စမ်းကြည့်ပါ။")
    except:
        await query.message.reply_text(" Server အလုပ်မလုပ်ပါ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling()

if __name__ == '__main__':
    keep_alive()
    main()
