import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
import yt_dlp

# --- Render အတွက် Web Server (Bot အိပ်မပျော်စေရန်) ---
app = Flask('')
@app.route('/')
def home(): 
    return "Bot is alive and running!"

def run(): 
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive(): 
    threading.Thread(target=run).start()

# --- Telegram Bot Configuration ---
TOKEN = '8514502979:AAGemVEqrs6BaaMM6iawm-A0vN8AJsCVXGk'

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" မင်္ဂလာပါ! Zwe Music Downloader မှ ကြိုဆိုပါတယ်။\n\nဒေါင်းလုဒ်ဆွဲလိုတဲ့ သီချင်းနာမည် သို့မဟုတ် အဆိုတော်နာမည်ကို ရိုက်ပို့ပေးပါ ခင်ဗျာ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text(f" '{query}' ကို ရှာဖွေနေပါတယ်...")
    
    ydl_opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
        except:
            await msg.edit_text(" ရှာဖွေမှု အဆင်မပြေပါဘူး။")
            return
            
    if not results:
        await msg.edit_text(" ဘာမှ ရှာမတွေ့ပါဘူး။")
        return
        
    keyboard = [[InlineKeyboardButton(e['title'][:50], callback_data=e['id'])] for e in results]
    await msg.edit_text(" အဆိုတော်နှင့် သီချင်းကို ရွေးချယ်ပါ -", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    video_id = query.data
    
    await query.edit_message_text(text=" ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    
    file_path = f"{video_id}.mp3"
    
    # FFmpeg နေရာ အတိအကျကို ညွှန်ပြခြင်း (Render build shell အရ)
    ffmpeg_bin_path = os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': video_id,
        'ffmpeg_location': ffmpeg_bin_path, # လမ်းကြောင်း အသေညွှန်ထားသည်
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        
        # သီချင်းဖိုင် ပို့ပေးရန်
        with open(file_path, 'rb') as audio:
            await query.message.reply_audio(audio=audio, title=f"Downloaded by Zwe Music")
            
        # ပို့ပြီးရင် ဖိုင်ပြန်ဖျက်ရန်
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        print(f"Error: {e}")
        await query.message.reply_text(" အမှားအယွင်းရှိလို့ ပြန်ကြိုးစားကြည့်ပါ။ (FFmpeg လမ်းကြောင်း မှားနေနိုင်ပါသည်)")

def main():
    # Bot အဟောင်းတွေနဲ့ မငြိအောင် drop_pending_updates သုံးထားသည်
    app_tg = Application.builder().token(TOKEN).build()
    app_tg.add_handler(CommandHandler("start", handle_start))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_tg.add_handler(CallbackQueryHandler(handle_button))
    
    print("Bot is starting polling...")
    app_tg.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    keep_alive() # Web server ဖွင့်ခြင်း
    main()       # Bot ဖွင့်ခြင်း
