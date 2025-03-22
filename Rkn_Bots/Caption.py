import asyncio
import random
import re
import os
import sys
import time
from pyrogram import Client, filters, errors, types
from pyrogram.errors import FloodWait
from config import Rkn_Bots
from .database import total_user, getid, delete, addCap, updateCap, insert, chnl_ids

# List of emojis for reactions
myEmoji = ["👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "😍", "🐳", "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒", "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂", "🤷", "🤷‍♀", "😡"]

async def send_reaction(chat_id, message_id):
    emoji = random.choice(myEmoji)
    await bot.send_chat_action(chat_id, "typing")
    await bot.send_message(chat_id, emoji)

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["rknusers"]))
async def all_db_users_here(client, message):
    x = await message.reply_text("Please Wait....")
    total = await total_user()
    await x.edit(f"Tᴏᴛᴀʟ Usᴇʀ :- `{total}`")

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if message.reply_to_message:
        rkn = await message.reply_text("Getting All IDs from the database..\nPlease wait")
        all_users = await getid()
        tot = await total_user()
        success, failed, deactivated, blocked = 0, 0, 0, 0
        await rkn.edit(f"ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...")

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
            except Exception:
                failed += 1
                await delete({"_id": user['_id']})
            try:
                await rkn.edit(
                    f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ</u>\n\n"
                    f"• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n"
                    f"• sᴜᴄᴄᴇssғᴜʟ: {success}\n"
                    f"• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n"
                    f"• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n"
                    f"• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}"
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)

        await rkn.edit(
            f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>\n\n"
            f"• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n"
            f"• sᴜᴄᴄᴇssғᴜʟ: {success}\n"
            f"• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n"
            f"• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n"
            f"• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}"
        )

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(bot, message):
    msg = await bot.send_message(chat_id=message.chat.id, text="**🔄 Processes stopped. Bot is restarting...**")
    await asyncio.sleep(3)
    await msg.edit("**✅ Bot is restarted. Now you can use me**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    user_id = int(message.from_user.id)
    await insert(user_id)
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hey, {message.from_user.mention}\n\nI'm an auto-caption bot. "
                f"I automatically edit captions for videos, audio files, and documents posted on channels.\n\n"
                f"Use <code>/set_caption</code> to set a caption\n"
                f"Use <code>/delcaption</code> to delete caption and set to default.</b>",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton('Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/RknDeveloper'),
            types.InlineKeyboardButton('Sᴜᴩᴩᴏʀᴛ', url='https://t.me/Rkn_Bots_Support')
        ], [
            types.InlineKeyboardButton('🔥 Source Code 🔥', url='https://github.com/RknDeveloper/Rkn-AutoCaptionBot')
        ]])
    )
    await send_reaction(message.chat.id, message.id)

@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    if not message.caption:
        return

    chnl_id = message.chat.id
    for file_type in ("video", "audio", "document", "voice"):
        obj = getattr(message, file_type, None)
        if obj and hasattr(obj, "file_name"):
            file_name = obj.file_name or "Unknown"
            file_caption = message.caption or ""

            file_name = re.sub(r"@\w+\s*", "", file_name)  # Remove usernames
            file_name = re.sub(r"_", " ", file_name)  # Replace underscores
            file_name = re.sub(r"\.\w+$", "", file_name)  # Remove file extensions

            cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})

            try:
                if cap_dets:
                    cap = cap_dets["caption"]
                    new_caption = cap.format(file_name=file_name, file_caption=file_caption)
                else:
                    new_caption = Rkn_Bots.DEF_CAP.format(file_name=file_name, file_caption=file_caption)

                await message.edit(new_caption)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await message.edit(new_caption)
            except Exception as e:
                print(f"Error editing caption: {e}")
                
