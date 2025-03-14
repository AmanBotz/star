import os
import subprocess
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# Configure logging.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Directories for storing cookie files and downloads.
COOKIES_DIR = "cookies"
DOWNLOADS_DIR = "downloads"
os.makedirs(COOKIES_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# In-memory mapping: user ID -> cookie file path.
user_cookies = {}

# Get environment variables.
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# FILE_SERVER_BASE_URL is not used in this version since we are sending the file directly.
# But you can keep it for reference.
FILE_SERVER_BASE_URL = os.environ.get("FILE_SERVER_BASE_URL", "http://localhost:8000")

# Initialize the Pyrogram client.
app = Client("hotstar_bot", bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    """Simple /start command to welcome the user."""
    await message.reply_text(
        "Welcome to the Hotstar Downloader Bot!\n\n"
        "First, send /setcookies with your cookies file (plain text) as an attachment. "
        "Then use /download <Hotstar URL> to download a video which will be sent back as a video message."
    )

@app.on_message(filters.command("setcookies"))
async def set_cookies(client: Client, message: Message):
    """
    /setcookies command:
    Save the attached cookies file to cookies/<user_id>.txt.
    """
    if message.document:
        file_path = os.path.join(COOKIES_DIR, f"{message.from_user.id}.txt")
        await message.download(file_name=file_path)
        user_cookies[message.from_user.id] = file_path
        await message.reply_text("Cookies file saved successfully. You can now use /download <Hotstar URL>.")
    else:
        await message.reply_text("Please attach your cookies file (plain text) with the /setcookies command.")

@app.on_message(filters.command("download"))
async def download_video(client: Client, message: Message):
    """
    /download command:
    Downloads a video from the provided Hotstar URL using the stored cookies,
    sends the video file directly to the user, and deletes the file afterward.
    """
    if len(message.command) < 2:
        await message.reply_text("Usage: /download <Hotstar Video URL>")
        return

    video_url = message.command[1]
    user_id = message.from_user.id

    if user_id not in user_cookies:
        await message.reply_text("No cookies file found. Please use /setcookies first.")
        return

    cookies_file = user_cookies[user_id]
    await message.reply_text("Starting download... This may take a few minutes.")

    # Define the output template for yt-dlp (saved in the downloads folder).
    output_template = os.path.join(DOWNLOADS_DIR, "%(title)s_%(id)s.%(ext)s")
    # Build the yt-dlp command.
    cmd = [
        "yt-dlp",
        "--cookies", cookies_file,
        "-o", output_template,
        "--print", "after_move:filepath",
        video_url,
    ]

    try:
        proc = await app.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True, check=True)
        )
        final_path = proc.stdout.strip()
        if not final_path or not os.path.exists(final_path):
            await message.reply_text("Download completed, but the file was not found.")
            return

        # Send the video file directly as a video message.
        await message.reply_video(video=final_path, caption="Here is your video!")
        # Delete the file after sending.
        try:
            os.remove(final_path)
            logger.info(f"Deleted file: {final_path}")
        except Exception as del_err:
            logger.error(f"Error deleting file: {del_err}")
    except subprocess.CalledProcessError as e:
        logger.error(f"yt-dlp error: {e.stderr}")
        await message.reply_text(f"Download failed: {e.stderr}")

if __name__ == "__main__":
    app.run()
