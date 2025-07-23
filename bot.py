import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

# Set your bot token here
BOT_TOKEN = "8141310043:AAFgY8uk8dedQS2FyjQ1u4caBol65w6PzIg"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download music using yt-dlp
async def download_song(query: str) -> str:
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'ytsearch',
            'quiet': True,
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            title = info.get('title', 'audio')
            filename = f"{title}.mp3"
            return filename if os.path.exists(filename) else None

    except Exception as e:
        logger.error(f"Download error: {e}")
        return None

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Send me a song name or YouTube link to download it as MP3!")

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text("🔎 Searching and downloading the song...")
    filename = await download_song(query)

    if filename:
        await update.message.reply_audio(audio=open(filename, 'rb'), title=filename)
        os.remove(filename)
    else:
        await update.message.reply_text("❌ Failed to download the song. Try a different name or link.")

# Main function
if __name__ == "__main__":
    # Initialize application
    app = ApplicationBuilder().token(BOT_TOKEN).read_timeout(60).connect_timeout(60).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Setup job scheduler
    scheduler = AsyncIOScheduler(timezone=utc)
    scheduler.start()

    logger.info("🎧 Music bot is running...")
    app.run_polling()
