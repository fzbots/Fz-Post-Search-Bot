import asyncio
import logging
from info import *
from pyrogram import enums
from pyrogram.errors import UserNotParticipant, FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from imdb import Cinemagoer
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton

# Initialize MongoDB client and collections
DATABASE_URI = DATABASE_URI  # imported from info

dbclient = AsyncIOMotorClient(DATABASE_URI)
db = dbclient["Channel-Filter"]
grp_col = db["GROUPS"]
user_col = db["USERS"]
dlt_col = db["Auto-Delete"]

ia = Cinemagoer()

async def add_group(group_id, group_name, user_name, user_id, channels, f_sub, verified):
    data = {
        "_id": group_id,
        "name": group_name,
        "user_id": user_id,
        "user_name": user_name,
        "channels": channels,
        "f_sub": f_sub,
        "verified": verified
    }
    await grp_col.update_one({"_id": group_id}, {"$set": data}, upsert=True)

async def get_group(group_id):
    group = await grp_col.find_one({"_id": group_id})
    if group is None:
        return {
            "_id": group_id,
            "name": "",
            "user_id": None,
            "user_name": "",
            "channels": [],
            "f_sub": False,
            "verified": False
        }
    return group
    
async def update_group(group_id, new_data):
    await grp_col.update_one({"_id": group_id}, {"$set": new_data})

async def delete_group(group_id):
    await grp_col.delete_one({"_id": group_id})
    
async def delete_user(user_id):
    await user_col.delete_one({"_id": user_id})

async def get_groups():
    total = await grp_col.count_documents({})
    cursor = grp_col.find({})
    groups = await cursor.to_list(length=int(total))
    return total, groups

async def add_user(user_id, name):
    data = {"_id": user_id, "name": name}
    try:
        await user_col.insert_one(data)
    except DuplicateKeyError:
        pass

async def get_users():
    total = await user_col.count_documents({})
    cursor = user_col.find({})
    users = await cursor.to_list(length=int(total))
    return total, users

async def search_imdb(query):
    try:
        # If query is numeric, fetch by ID
        int(query)
        movie = ia.get_movie(query)
        return movie.get("title", "")
    except ValueError:
        # Otherwise, search by name
        movies = ia.search_movie(query, results=10)
        results = []
        for movie in movies:
            title = movie.get("title", "Unknown")
            year = f" - {movie.get('year')}" if movie.get('year') else ""
            results.append({"title": title, "year": year, "id": movie.movieID})
        return results

async def force_sub(bot, message):
    group = await get_group(message.chat.id)
    f_sub = group.get("f_sub")
    admin = group.get("user_id")
    # If no forced subscription, allow
    if not f_sub:
        return True
    if message.from_user is None:
        return True
    try:
        # Check if user is a member of the subscription channel
        f_chat = await bot.get_chat(f_sub)
        f_link = f_chat.invite_link
        member = await bot.get_chat_member(f_sub, message.from_user.id)
        if member.status == enums.ChatMemberStatus.BANNED:
            await message.reply(f"ꜱᴏʀʀʏ {message.from_user.mention}! You are banned in our channel and will be banned here soon.")
            await asyncio.sleep(10)
            await bot.ban_chat_member(message.chat.id, message.from_user.id)
            return False
    except UserNotParticipant:
        # Restrict until they join
        await bot.restrict_chat_member(
            chat_id=message.chat.id, 
            user_id=message.from_user.id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        await message.reply(
            f"🚫 Hey {message.from_user.mention}! To send messages here, first join our channel then send your request here",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Join Channel", url=f_link)]
            ])
        )
        await message.delete()
        return False
    except Exception as e:
        logging.error(f"Error in force_sub: {e}")
        if admin:
            await bot.send_message(chat_id=admin, text=f"❌ Error in force_sub: `{str(e)}`")
        return False
    return True

async def broadcast_messages(user_id, message):
    from pyrogram.errors import FloodWait
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await delete_user(int(user_id))
        logging.info(f"{user_id} removed: deactivated account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await delete_user(int(user_id))
        logging.info(f"{user_id} removed: invalid peer id.")
        return False, "Error"
    except Exception as e:
        logging.error(f"Error broadcasting to {user_id}: {e}")
        return False, "Error"
