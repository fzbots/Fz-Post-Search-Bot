from pyrogram import Client, filters
from config import ADMIN, API_HASH, API_ID
from database import database, get_group
from utils import force_sub, send_message_in_chunks

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    vj = database.find_one({"chat_id": ADMIN})
    if vj is None:
        return await message.reply("*Contact Admin Then Say To Login In Bot.*")

    User = Client("post_search", session_string=vj['session'], api_hash=API_HASH, api_id=API_ID)
    await User.connect()

    f_sub = await force_sub(bot, message)
    if f_sub is False:
        return

    group_data = await get_group(message.chat.id)
    channels = group_data.get("channels", [])
    if not channels:
        return

    if message.text.startswith("/"):
        return

    query_words = message.text.lower().split()
    head = (
        f"🔍 Here is the results {message.from_user.mention} \n\n"
        f"🚨 Powered By </u><b><i>Faiz_Movies</i></b>\n\n"
    )
    results = ""

    try:
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=" ".join(query_words)):
                name = (msg.text or msg.caption or "").split("\n")[0].lower()

                if any(word in name for word in query_words):
                    if name in results:
                        continue
                    results += f"<b><i>{name}</i></b>\n👉 {msg.link}\n\n"

        if not results:
            await message.reply("*⚠️ No results found for your query.*")
        else:
            await send_message_in_chunks(bot, message.chat.id, head + results)

    except Exception as e:
        print("Search error:", e)
        pass
