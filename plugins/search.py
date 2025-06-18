# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
from info import *
from utils import *
from time import time 
from plugins.generate import database
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 

async def send_message_in_chunks(client, chat_id, text):
    max_length = 4096
    for i in range(0, len(text), max_length):
        msg = await client.send_message(chat_id=chat_id, text=text[i:i+max_length])
        asyncio.create_task(delete_after_delay(msg, 1800))

async def delete_after_delay(message: Message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    vj = database.find_one({"chat_id": ADMIN})
    if vj is None:
        return await message.reply("**Contact Admin Then Say To Login In Bot.**")
    
    User = Client("post_search", session_string=vj['session'], api_hash=API_HASH, api_id=API_ID)
    await User.connect()

    f_sub = await force_sub(bot, message)
    if f_sub == False:
        return

    channels = (await get_group(message.chat.id))["channels"]
    if not channels:
        return

    if message.text.startswith("/"):
        return

    full_query = message.text.lower().strip()
    keywords = [full_query] + full_query.split()

    head = f"<u>⭕ Here is the results {message.from_user.mention} 👇\n\n💢 Powered By </u> <b><I>@Faiz_Movies ❗</I></b>\n\n"
    results = ""

    try:
        for keyword in keywords:
            for channel in channels:
                async for msg in User.search_messages(chat_id=channel, query=keyword):
                    name = (msg.text or msg.caption).split("\n")[0]
                    if name in results:
                        continue
                    results += f"<b><I>♻️ {name}\n🔗 {msg.link}</I></b>\n\n"
            if results:
                break

        if not results:
            await message.reply("**No results found for your query.**")
        else:
            await send_message_in_chunks(bot, message.chat.id, head + results)

    except:
        pass
