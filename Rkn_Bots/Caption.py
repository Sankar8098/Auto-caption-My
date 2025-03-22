from pyrogram import Client, filters
import re
import asyncio
import os
from pyrogram.errors import FloodWait
from .database import addCap, updateCap, chnl_ids, total_user, getid, delete, insert

# Default Caption Format
DEF_CAP = "<b>{file_name}</b>\n\n➠ Fast Download Link : {file_caption}"

# ✅ Command to Set Custom Caption
@Client.on_message(filters.command("set_caption") & filters.channel)
async def setCap(bot, message):
    if len(message.command) < 2:
        return await message.reply(
            "Usage: /set_caption <code>Your caption (use {file_name} & {file_caption})</code>"
        )

    chnl_id = message.chat.id
    caption = message.text.split(" ", 1)[1]  # Extract user-provided caption

    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    if chkData:
        await updateCap(chnl_id, caption)
    else:
        await addCap(chnl_id, caption)

    await message.reply(f"✅ Custom caption set successfully!\n\nNew Caption:\n<code>{caption}</code>")

# ✅ Command to Delete Custom Caption
@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & filters.channel)
async def delCap(bot, message):
    chnl_id = message.chat.id
    try:
        await chnl_ids.delete_one({"chnl_id": chnl_id})
        await message.reply("✅ Caption deleted! Now using default caption.")
    except Exception as e:
        await message.reply(f"❌ Error deleting caption: {e}")

# ✅ Auto Caption Editing
@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    if not message.caption:
        return  # Skip if no caption

    for file_type in ("video", "audio", "document", "voice"):
        obj = getattr(message, file_type, None)
        if obj and hasattr(obj, "file_name"):
            file_name = obj.file_name or "Unknown"

            # ✅ Clean File Name (Remove . and Extensions)
            file_name = re.sub(r"@\w+\s*", "", file_name)  # Remove @username
            file_name = re.sub(r"\.\w{2,4}$", "", file_name)  # Remove .mkv, .mp4, etc.
            file_name = file_name.replace(".", " ")  # Replace remaining dots with spaces

            # ✅ Extract Download Link
            file_caption = message.caption or ""
            link_match = re.search(r'https?://\S+', file_caption)
            download_link = link_match.group(0) if link_match else ""

            # ✅ Fetch Custom Caption from DB
            cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})

            # ✅ Apply Custom Caption if Exists, Else Use Default
            if cap_dets:
                new_caption = cap_dets["caption"].format(file_name=file_name, file_caption=download_link)
            else:
                new_caption = DEF_CAP.format(file_name=file_name, file_caption=download_link)

            # ✅ Prevent Telegram from Skipping Edits
            if new_caption.strip() == file_caption.strip():
                new_caption += "​"  # Zero-Width Space

            try:
                await message.edit_caption(new_caption)
                print(f"✅ Caption updated successfully: {new_caption}")
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await message.edit_caption(new_caption)
            except Exception as e:
                print(f"❌ Error editing caption: {e}")

# ✅ Get Total Users Count
@Client.on_message(filters.private & filters.command("rknusers"))
async def all_db_users_here(client, message):
    x = await message.reply_text("Please Wait....")
    total = await total_user()
    await x.edit(f"👥 Total Users: `{total}`")

# ✅ Broadcast Message to All Users
@Client.on_message(filters.private & filters.command("broadcast"))
async def broadcast(bot, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast!")

    rkn = await message.reply_text("📡 Getting all user IDs...")
    all_users = await getid()
    tot = await total_user()
    
    success, failed, deactivated, blocked = 0, 0, 0, 0

    await rkn.edit(f"📣 Broadcasting to {tot} users...")

    async for user in all_users:
        try:
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
            await rkn.edit(f"✅ Success: {success}\n❌ Failed: {failed}\n🚫 Blocked: {blocked}\n👤 Deactivated: {deactivated}")
        except FloodWait as e:
            await asyncio.sleep(e.x)

    await rkn.edit("📢 Broadcast Completed!")

# ✅ Restart Bot
@Client.on_message(filters.private & filters.command("restart"))
async def restart_bot(bot, message):
    msg = await bot.send_message(chat_id=message.chat.id, text="🔄 Restarting bot...")
    await asyncio.sleep(3)
    await msg.edit("✅ Bot restarted successfully!")
    os.execl(sys.executable, sys.executable, *sys.argv)
