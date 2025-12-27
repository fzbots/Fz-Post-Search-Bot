# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import traceback
import certifi
from asyncio.exceptions import TimeoutError

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)

from pymongo import MongoClient
from info import API_ID, API_HASH, DATABASE_URI, ADMIN

# =========================
# MongoDB (TLS SAFE CONFIG)
# =========================
mongo_client = MongoClient(
    DATABASE_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=20000
)

database = mongo_client.userdb.sessions
# =========================

strings = {
    'need_login': "U have to /login before using then bot can download restricted content ❕",
    'already_logged_in': "You are already logged in.\nIf you want to login again, /logout to proceed.",
}

SESSION_STRING_SIZE = 351


def get(obj, key, default=None):
    try:
        return obj[key]
    except Exception:
        return default


# =========================
# LOGOUT
# =========================
@Client.on_message(filters.private & filters.command(["logout"]) & filters.user(ADMIN))
async def logout(_, msg: Message):
    user_data = database.find_one({"chat_id": msg.chat.id})
    if user_data is None or not user_data.get("session"):
        return

    database.update_one(
        {"_id": user_data["_id"]},
        {"$set": {"session": None, "logged_in": False}}
    )

    await msg.reply("**Logout Successfully** ♦")


# =========================
# LOGIN
# =========================
@Client.on_message(filters.private & filters.command(["login"]) & filters.user(ADMIN))
async def main(bot: Client, message: Message):
    user_data = database.find_one({"chat_id": message.from_user.id})

    if get(user_data, "logged_in", False):
        await message.reply(strings["already_logged_in"])
        return

    user_id = int(message.from_user.id)

    phone_number_msg = await bot.ask(
        chat_id=user_id,
        text=(
            "<b>Please send your phone number which includes country code</b>\n"
            "<b>Example:</b> <code>+13124562345, +9171828181889</code>"
        )
    )

    if phone_number_msg.text == "/cancel":
        return await phone_number_msg.reply("<b>Process cancelled!</b>")

    phone_number = phone_number_msg.text

    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()

    await phone_number_msg.reply("Sending OTP...")

    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(
            user_id,
            (
                "Please check for OTP in official Telegram account.\n\n"
                "If OTP is `12345`, send it as: `1 2 3 4 5`\n\n"
                "**Enter /cancel to cancel the process**"
            ),
            filters=filters.text,
            timeout=600
        )
    except PhoneNumberInvalid:
        await phone_number_msg.reply("`PHONE_NUMBER` **is invalid.**")
        return

    if phone_code_msg.text == "/cancel":
        return await phone_code_msg.reply("<b>Process cancelled!</b>")

    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)

    except PhoneCodeInvalid:
        await phone_code_msg.reply("**OTP is invalid.**")
        return

    except PhoneCodeExpired:
        await phone_code_msg.reply("**OTP is expired.**")
        return

    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(
            user_id,
            (
                "**Two-step verification enabled. Please provide password.**\n\n"
                "Enter /cancel to cancel the process"
            ),
            filters=filters.text,
            timeout=300
        )

        if two_step_msg.text == "/cancel":
            return await two_step_msg.reply("<b>Process cancelled!</b>")

        try:
            await client.check_password(password=two_step_msg.text)
        except PasswordHashInvalid:
            await two_step_msg.reply("**Invalid Password Provided**")
            return

    string_session = await client.export_session_string()
    await client.disconnect()

    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply("<b>Invalid session string</b>")

    try:
        user_data = database.find_one({"chat_id": message.from_user.id})

        data = {
            "session": string_session,
            "logged_in": True
        }

        uclient = Client(
            ":memory:",
            session_string=string_session,
            api_id=API_ID,
            api_hash=API_HASH
        )
        await uclient.connect()
        await uclient.disconnect()

        if user_data:
            database.update_one({"_id": user_data["_id"]}, {"$set": data})
        else:
            data["chat_id"] = message.from_user.id
            database.insert_one(data)

    except Exception as e:
        traceback.print_exc()
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")

    await bot.send_message(
        message.from_user.id,
        "<b>Account Login Successfully.\n\n"
        "If you face AUTH KEY error, use /logout and /login again.</b>"
    )


# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
