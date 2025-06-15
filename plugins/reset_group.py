```python
from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.generate import database  # ye wahi database object hai

@Client.on_message(filters.command("resetgroup") & filters.group)
async def reset_group(client, message: Message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in ("administrator", "creator"):
        return await message.reply("Sirf group admins hi is command ka use kar sakte hain.")

    group_id = message.chat.id

    result = database.delete_many({"chat_id": group_id})
    if result.deleted_count > 0:
        await message.reply("✅ Group ki settings reset kar di gayi hain.")
    else:
        await message.reply("⚠️ Is group ke liye koi saved settings nahi mili.")

```
