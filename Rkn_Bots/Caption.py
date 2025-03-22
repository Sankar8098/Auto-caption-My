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
@Client.on_message(filters.command("set_caption") & filters.channel)
async def setCap(bot, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /set_caption <code>Your caption</code>\n"
                                   "Use {file_name} to show the file name and {file_caption} for the original caption.")
    
    chnl_id = message.chat.id
    caption = message.text.split(" ", 1)[1]  

    # Check if channel already has a custom caption
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    
    if chkData:
        await updateCap(chnl_id, caption)
        return await message.reply(f"✅ Your new caption has been updated: {caption}")
    else:
        await addCap(chnl_id, caption)
        return await message.reply(f"✅ Caption set successfully: {caption}")

# Delete Caption
@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & filters.channel)
async def delCap(bot, msg):
    chnl_id = msg.chat.id
    try:
        await chnl_ids.delete_one({"chnl_id": chnl_id})
        return await msg.reply("<b>✅ Success! Default caption will be used from now.</b>")
    except Exception as e:
        e_val = await msg.reply(f"❌ Error: {e}")
        await asyncio.sleep(5)
        await e_val.delete()
        return

# Auto Edit Caption
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

            # Get existing caption
            file_caption = message.caption or ""
            cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})

            if cap_dets:
                new_caption = cap_dets["caption"].format(file_name=file_name, file_caption=file_caption)
            else:
                new_caption = DEF_CAP.format(file_name=file_name, file_caption=file_caption)

            # Skip editing if caption is unchanged
            if new_caption.strip() == file_caption.strip():
                print("⚠️ Caption unchanged, skipping edit.")
                return

            try:
                await message.edit_caption(new_caption)
                print("✅ Caption updated successfully!")
            except errors.FloodWait as e:
                print(f"⏳ FloodWait detected! Waiting {e.x} seconds...")
                await asyncio.sleep(e.x)
                await message.edit_caption(new_caption)
            except errors.RPCError as e:
                print(f"❌ Telegram Error: {e}")

# Broadcast Message to All Users
@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if message.reply_to_message:
        rkn = await message.reply_text("🔄 Fetching all users...")
        all_users = await getid()
        tot = await total_user()
        success, failed, deactivated, blocked = 0, 0, 0, 0

        async for user in all_users:
            try:
                time.sleep(1)
                await message.reply_to_message.copy(user['_id'])
                success += 1
            except errors.InputUserDeactivated:
                deactivated += 1
                await delete({"_id": user['_id']})
            except errors.UserIsBlocked:
                blocked += 1
                await delete({"_id": user['_id']})
            except Exception as e:
                failed += 1
                await delete({"_id": user['_id']})
                pass
            try:
                await rkn.edit(f"📢 **Broadcasting...**\n\n"
                               f"👥 Total Users: {tot}\n"
                               f"✅ Sent: {success}\n"
                               f"🚫 Blocked: {blocked}\n"
                               f"🗑 Deleted: {deactivated}\n"
                               f"❌ Failed: {failed}")
            except FloodWait as e:
                await asyncio.sleep(e.x)

        await rkn.edit("✅ **Broadcast Completed!**")

# Restart Bot
@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(bot, message):
    msg = await bot.send_message(message.chat.id, "🔄 Restarting bot...")
    await asyncio.sleep(3)
    await msg.edit("✅ **Bot restarted successfully!**")
    os.execl(sys.executable, sys.executable, *sys.argv)
            
