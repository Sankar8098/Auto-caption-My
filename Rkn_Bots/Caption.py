import os
import re
import time
import asyncio
from pyrogram import Client, filters, errors, types
from pyrogram.errors import FloodWait
from config import Rkn_Bots
from .database import total_user, getid, delete, addCap, updateCap, insert, chnl_ids

# Default caption format (can be changed with /set_caption)
DEF_CAP = os.environ.get(
    "DEF_CAP",
    "<b><a href='telegram.me/SK_MoviesOffl'>{file_caption}</a></b>"
)

# Emoji Reactions List
myEmoji = ["👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱"]

# Send Reaction Emoji
async def send_reaction(chat_id, message_id):
    doEmoji = random.choice(myEmoji)
    await bot.send_chat_action(chat_id, "typing")
    await bot.send_message(chat_id, doEmoji)

# Start Command
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    user_id = message.from_user.id
    await insert(user_id)
    
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hey, {message.from_user.mention}\n\n"
                "I'm an auto-caption bot. I automatically edit captions for videos, audio files, and documents posted on channels.\n\n"
                "Use <code>/set_caption</code> to set a caption\n"
                "Use <code>/delcaption</code> to delete the caption and set it to default.\n\n"
                "Note: All commands work on channels only.</b>",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton('Updates', url='https://t.me/RknDeveloper'),
            types.InlineKeyboardButton('Support', url='https://t.me/Rkn_Bots_Support')
        ], [
            types.InlineKeyboardButton('🔥 Source Code 🔥', url='https://github.com/RknDeveloper/Rkn-AutoCaptionBot')
        ]])
    )
    
    # Send a random emoji reaction
    await send_reaction(message.chat.id, message.id)

# Set Caption
@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    if not message.caption:
        return

    for file_type in ("video", "audio", "document", "voice"):
        obj = getattr(message, file_type, None)
        if obj and hasattr(obj, "file_name"):
            file_name = obj.file_name or "Unknown"

            # Remove usernames (e.g., @ChannelName)
            file_name = re.sub(r"@\w+\s*", "", file_name)

            # Remove the last file extension (e.g., .mkv, .mp4, .avi)
            file_name = re.sub(r"\.\w{2,4}$", "", file_name)

            # Replace remaining dots with spaces
            file_name = file_name.replace(".", " ")

            # Get existing caption (assumed to contain the Fast Download Link)
            file_caption = message.caption or ""

            # Extract only the **download link** from the caption (if available)
            link_match = re.search(r'https?://\S+', file_caption)
            download_link = link_match.group(0) if link_match else ""

            # **Final Caption Format**
            formatted_caption = f"{file_name}\n\n➠ Fast Download Link : {download_link}"

            # Fetch custom caption from DB (if set)
            cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})

            # Use custom caption if available, otherwise use default format
            if cap_dets:
                new_caption = cap_dets["caption"].format(file_name=file_name, file_caption=formatted_caption)
            else:
                new_caption = formatted_caption

            # **Force Edit by Adding a Zero-Width Space (if needed)**
            if new_caption.strip() == file_caption.strip():
                new_caption += "​"  # Unicode zero-width space

            try:
                await message.edit_caption(new_caption)
                print(f"✅ Caption updated successfully: {new_caption}")
            except errors.FloodWait as e:
                print(f"⏳ FloodWait detected! Waiting {e.x} seconds...")
                await asyncio.sleep(e.x)
                await message.edit_caption(new_caption)
            except errors.RPCError as e:
                print(f"❌ Telegram Error: {e}")
