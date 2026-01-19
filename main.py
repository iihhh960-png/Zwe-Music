import os, threading, yt_dlp
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

app = Flask('')
@app.route('/')
def home(): return "Bot is Live with Cookies!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.environ.get('BOT_TOKEN')

async def handle_start(update, context):
    await update.message.reply_text(" Zwe Music Downloader!\nသီချင်းနာမည် ပို့ပေးပါ။")

async def search_yt(query):
    opts = {'quiet': True, 'cookiefile': 'cookies.txt', 'noplaylist': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']

async def handle_message(update, context):
    query = update.message.text
    context.user_data['last_q'] = query
    msg = await update.message.reply_text(" ရှာဖွေနေပါတယ်...")
    try:
        results = await search_yt(query)
        kb = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in results]
        await msg.edit_text(" ရလဒ်များ -", reply_markup=InlineKeyboardMarkup(kb))
    except: await msg.edit_text(" Cookie အမှားအယွင်းရှိနေသည်။")

async def handle_button(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    
    if data[0] == "back": # နောက်သို့ ခလုတ်
        last_q = context.user_data.get('last_q')
        results = await search_yt(last_q)
        kb = [[InlineKeyboardButton(e['title'][:50], callback_data=f"sel|{e['id']}")] for e in results]
        await query.edit_message_text(" ရလဒ်များ -", reply_markup=InlineKeyboardMarkup(kb))
        return

    vid = data[1]
    if data[0] == "sel":
        kb = [[InlineKeyboardButton(" MP3", callback_data=f"mp3|{vid}"), InlineKeyboardButton(" MP4", callback_data=f"mp4|{vid}")],
              [InlineKeyboardButton(" နောက်သို့", callback_data="back")]]
        await query.edit_message_text("Format ရွေးပါ-", reply_markup=InlineKeyboardMarkup(kb))
        return

    await query.edit_message_text(" ဒေါင်းလုဒ်ဆွဲနေပါပြီ...")
    ext = 'mp3' if data[0] == 'mp3' else 'mp4'
    opts = {'format': 'bestaudio/best' if data[0] == 'mp3' else 'best', 'outtmpl': vid, 'cookiefile': 'cookies.txt'}
    if data[0] == 'mp3': opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([f"https://www.youtube.com/watch?v={vid}"])
        with open(f"{vid}.{ext}", 'rb') as f:
            if data[0] == 'mp3': await query.message.reply_audio(audio=f)
            else: await query.message.reply_video(video=f)
        os.remove(f"{vid}.{ext}")
    except: await query.message.reply_text(" ဒေါင်းမရပါ။ Cookie သက်တမ်းကုန်နေပြီ။")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.run_polling()

if __name__ == '__main__':
    keep_alive()
    main()
