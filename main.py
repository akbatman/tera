import asyncio
import os
import time
from uuid import uuid4
from datetime import datetime
import redis
import telethon
import telethon.tl.types
from telethon import events
from telethon import TelegramClient, events
from telethon.tl.functions.messages import ForwardMessagesRequest
from telethon.types import Message, UpdateNewMessage
from telethon import Button
from cansend import CanSend
from config import *
from terabox import get_data
from stats import (
    track_message,
    get_message_count,
    get_new_user_count_today,
    get_top_active_users,
    get_file_type_stats,
)
from tools import (
    convert_seconds,
    download_file,
    download_image_to_bytesio,
    extract_code_from_url,
    get_formatted_size,
    get_urls_from_string,
    is_user_on_chat,
    get_bot_username,
)

BOT_USERNAME = get_bot_username(BOT_TOKEN)

bot = TelegramClient("tele", API_ID, API_HASH)

db = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


bot_start_time = time.time()
user_count = db.scard("users")
user_ids = db.smembers("users")  # Retrieve user IDs


def format_top_users(top_users):
    """Formats the top active users data for display."""
    formatted = ""
    for i, (user_id, score) in enumerate(top_users, start=1):
        formatted += (
            f"{i}. User ID: [{user_id}](tg://user?id={user_id}) (Score: {score})\n"
        )
    return formatted


def format_file_stats(file_stats):
    """Formats the file type statistics for display."""
    formatted = ""
    for file_type, count in file_stats.items():
        formatted += f"{file_type}: {count}\n"
    return formatted


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        pattern="/ban (.*)", incoming=True, outgoing=False, from_users=ADMINS
    )
)
async def ban_user(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return

    try:
        user_id = int(m.pattern_match.group(1))  # Get user ID to ban
    except ValueError:
        return await m.reply("Invalid user ID format.")

    if db.sismember("banned_users", user_id):
        await m.reply("User is already banned.")
    else:
        db.sadd("banned_users", user_id)
        await m.reply(f"User ID {user_id} has been banned.")


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        pattern="/unban (.*)", incoming=True, outgoing=False, from_users=ADMINS
    )
)
async def unban_user(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return

    try:
        user_id = int(m.pattern_match.group(1))
    except ValueError:
        return await m.reply("Invalid user ID format.")

    if db.srem("banned_users", user_id):
        await m.reply(f"User ID {user_id} has been unbanned.")
    else:
        await m.reply("User is not banned.")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/stats$", incoming=True, outgoing=False))
async def stats_command(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    check_if = await is_user_on_chat(bot, f"@akimaxmovies_2", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @akimaxmovies_2 then send me the link again.")
    check_if = await is_user_on_chat(bot, f"@akimaxmovies_2", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @akimaxmovies_2 then send me the link again.")

    uptime = convert_seconds(time.time() - bot_start_time)
    message_count = get_message_count()
    new_users_today = get_new_user_count_today()
    top_users = get_top_active_users()
    file_stats = get_file_type_stats()

    stats_message = f"""
**Bot Statistics:**

** Total Messages: {message_count}**
** New Users Today: {new_users_today}**
** Top Active Users: {format_top_users(top_users)}**
** File Types: {format_file_stats(file_stats)}**

** Uptime: {uptime}**
** Users: {user_count}**

@{BOT_USERNAME}
"""

    if m.sender_id == OWNER_ID:
        await m.reply(stats_message)
    else:
        await m.reply("Sorry, this command is restricted to the bot owner.")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/start$", incoming=True, outgoing=False))
async def start(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return

    first_name = m.sender.first_name
    user_id = m.sender_id
    reply_text = f"""
**Hello, [{first_name}](tg://user?id={m.sender.id})!**  I am a bot to download videos from Terabox.

**Just send me the Terabox link** and I'll start downloading it for you.
"""
    if not db.sismember("users", str(m.sender_id)):
        db.sadd("users", str(m.sender_id))
    if not db.sismember("new_users", str(user_id)):  # Check Redis
        # Send new user notification (only if it's the first time)
        await bot.send_message(
            USER_CHANNEL,
            f"**New User Joined**\nName: {first_name} \nUser ID: [{user_id}](tg://user?id={user_id})\n@{BOT_USERNAME}",
            parse_mode="markdown",
        )
        db.sadd("new_users", str(user_id))

    check_if = await is_user_on_chat(bot, f"@akimaxmovies_2", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @akimaxmovies_2 then send me the link again.")
    check_if = await is_user_on_chat(bot, f"@akimaxmovies_2", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @akimaxmovies_2 then send me the link again.")
    await m.reply(
        reply_text,
        buttons=[
            [
                Button.url("😎𝐎𝐰𝐧𝐞𝐫😎", "https://t.me/MrKhan_00"),
                Button.url(
                    "𝐂𝐡𝐚𝐧𝐧𝐞𝐥", "https://t.me/akimaxmovies_2"
                ),
            ]
        ],
        link_preview=False,
        parse_mode="markdown",
    )


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/broadcast$", incoming=True, outgoing=False))
async def broadcast(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    user_id = m.sender_id
    if m.sender_id != OWNER_ID:  # Check if user is authorized
        await m.reply("Sorry, you don't have permission to broadcast.")
        return

    message_text = await m.get_reply_message()  # Get message to broadcast
    if not message_text:
        await m.reply("Please reply with the message you want to broadcast.")
        return
    for user_id in user_ids:
        try:
            await bot.send_message(int(user_id), message_text.message)
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")

    await m.reply("Broadcast sent successfully!")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/help$", incoming=True, outgoing=False))
async def help_command(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    check_if = await is_user_on_chat(bot, f" @akimaxmovies_2", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join  @akimaxmovies_2 then send me the link again.")
    check_if = await is_user_on_chat(bot, f" @akimaxmovies_2", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join  @akimaxmovies_2 then send me the link again.")
    help_text = """
𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀:

/𝘀𝘁𝗮𝗿𝘁 - 𝗦𝘁𝗮𝗿𝘁 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗲 𝗯𝗼𝘁.
/𝗵𝗲𝗹𝗽 - 𝗦𝗵𝗼𝘄 𝘁𝗵𝗶𝘀 𝗵𝗲𝗹𝗽 𝗺𝗲𝘀𝘀𝗮𝗴𝗲.

 𝗣𝗼𝘄𝗲𝗿𝗱 𝗕𝘆 𝗜𝗠𝗔𝗫 𝗖𝗟𝗢𝗨𝗗
"""
    link_preview = (False,)
    await m.reply(
        help_text,
        parse_mode="markdown",
        buttons=[
            [
                Button.url("😎𝐎𝐰𝐧𝐞𝐫😎", "https://t.me/MrKhan_00"),
                Button.url(
                    "𝐂𝐡𝐚𝐧𝐧𝐞𝐥", "https://t.me/akimaxmovies_2"
                ),
            ]
        ],
    )


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        incoming=True,
        outgoing=False,
        func=lambda message: message.text and get_urls_from_string(message.text),
    )
)
async def get_message(m: Message):
    asyncio.create_task(handle_message(m))


async def handle_message(m: Message):
    if m.is_group or m.is_channel:
        return
    username = m.sender.username
    first_name = m.sender.first_name
    user_id = m.sender_id
    if db.sismember("banned_users", user_id):
        await m.reply(
            "You are banned from using this bot. Conntact support for more info."
        )
        return

    url = get_urls_from_string(m.text)
    if not url:
        return await m.reply("𝗣𝗹𝗲𝗮𝘀𝗲 𝗲𝗻𝘁𝗲𝗿 𝗮 𝘃𝗮𝗹𝗶𝗱 𝘂𝗿𝗹.")
    check_if = await is_user_on_chat(bot, "@akimaxmovies_2", m.peer_id)
    if not check_if:
        return await m.reply("𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 @𝗮𝗸𝗶𝗺𝗮𝘅𝗺𝗼𝘃𝗶𝗲𝘀_𝟮  𝘁𝗵𝗲𝗻 𝘀𝗲𝗻𝗱 𝗺𝗲 𝘁𝗵𝗲 𝗹𝗶𝗻𝗸 𝗮𝗴𝗮𝗶𝗻.")
    check_if = await is_user_on_chat(bot, " @akimaxmovies_2", m.peer_id)
    if not check_if:
        return await m.reply("𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 @𝗮𝗸𝗶𝗺𝗮𝘅𝗺𝗼𝘃𝗶𝗲𝘀_𝟮  𝘁𝗵𝗲𝗻 𝘀𝗲𝗻𝗱 𝗺𝗲 𝘁𝗵𝗲 𝗹𝗶𝗻𝗸 𝗮𝗴𝗮𝗶𝗻.")
    is_spam = db.get(m.sender_id)
    if is_spam and m.sender_id not in [6791744215]:
        return await m.reply("𝗬𝗼𝘂 𝗮𝗿𝗲 𝘀𝗽𝗮𝗺𝗺𝗶𝗻𝗴. 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁 𝗮 𝟭 𝗺𝗶𝗻𝘂𝘁𝗲 𝗮𝗻𝗱 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻.")
    hm = await m.reply("Sending you the media wait...")
    count = db.get(f"check_{m.sender_id}")
    if count and int(count) > 30:
        return await hm.edit(
            "𝗬𝗼𝘂 𝗮𝗿𝗲 𝗹𝗶𝗺𝗶𝘁𝗲𝗱 𝗻𝗼𝘄. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗰𝗼𝗺𝗲 𝗯𝗮𝗰𝗸 𝗮𝗳𝘁𝗲𝗿 𝟭 𝗵𝗼𝘂𝗿𝘀 𝗼𝗿 𝘂𝘀𝗲 𝗮𝗻𝗼𝘁𝗵𝗲𝗿 𝗮𝗰𝗰𝗼𝘂𝗻𝘁."
        )
    shorturl = extract_code_from_url(url)
    if not shorturl:
        return await hm.edit("Seems like your link is invalid.")
    fileid = db.get(shorturl)
    if fileid:
        try:
            await hm.delete()
        except:
            pass

        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[int(fileid)],
                to_peer=m.chat.id,
                drop_author=True,
                # noforwards=True, #Uncomment it if you dont want to forward the media.
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )
        db.set(m.sender_id, time.monotonic(), ex=60)
        db.set(
            f"check_{m.sender_id}",
            int(count) + 1 if count else 1,
            ex=3600,
        )

        return
    track_message(m.sender_id)
    data = get_data(url)
    if not data:
        return await hm.edit("Sorry! API is dead or maybe your link is broken.")
    db.set(m.sender_id, time.monotonic(), ex=60)
    if (
        not data["file_name"].endswith(".mp4")
        and not data["file_name"].endswith(".mkv")
        and not data["file_name"].endswith(".Mkv")
        and not data["file_name"].endswith(".webm")
        and not data["file_name"].endswith(".ts")
        and not data["file_name"].endswith(".mov")
        and not data["file_name"].endswith(".hevc")
        and not data["file_name"].endswith(".png")
        and not data["file_name"].endswith(".jpg")
        and not data["file_name"].endswith(".jpeg")
    ):
        return await hm.edit(
            f"𝗦𝗼𝗿𝗿𝘆! 𝗙𝗶𝗹𝗲 𝗶𝘀 𝗻𝗼𝘁 𝘀𝘂𝗽𝗽𝗼𝗿𝘁𝗲𝗱 𝗳𝗼𝗿 𝗻𝗼𝘄. 𝗜 𝗰𝗮𝗻 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗼𝗻𝗹𝘆 .𝗺𝗽𝟰, .𝗺𝗸𝘃, .𝘄𝗲𝗯𝗺, .𝘁𝘀, .𝗺𝗼𝘃, .𝗵𝗲𝘃𝗰, .𝗽𝗻𝗴, .𝗷𝗽𝗴, .𝗷𝗽𝗲𝗴 𝗳𝗶𝗹𝗲𝘀."
        )
    if int(data["sizebytes"]) > 1024650000 and m.sender_id not in [6791744215]:
        return await hm.edit(
            f"𝗦𝗼𝗿𝗿𝘆! 𝗙𝗶𝗹𝗲 𝗶𝘀 𝘁𝗼𝗼 𝗯𝗶𝗴. 𝗜 𝗰𝗮𝗻 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗼𝗻𝗹𝘆 𝟭𝗚𝗕 𝗮𝗻𝗱 𝘁𝗵𝗶𝘀 𝗳𝗶𝗹𝗲 𝗶𝘀 𝗼𝗳 {data['size']} ."
        )

    start_time = time.time()
    cansend = CanSend()

    async def progress_bar(current_downloaded, total_downloaded, state="Sending"):

        if not cansend.can_send():
            return
        bar_length = 18
        percent = current_downloaded / total_downloaded
        arrow = "█" * int(percent * bar_length)
        spaces = "░" * (bar_length - len(arrow))

        elapsed_time = time.time() - start_time

        head_text = f"{state} `{data['file_name']}`"
        progress_bar = f"[{arrow + spaces}] {percent:.2%}"
        upload_speed = current_downloaded / elapsed_time if elapsed_time > 0 else 0
        speed_line = f"Speed: **{get_formatted_size(upload_speed)}/s**"

        time_remaining = (
            (total_downloaded - current_downloaded) / upload_speed
            if upload_speed > 0
            else 0
        )
        time_line = f"Time Remaining: `{convert_seconds(time_remaining)}`"

        size_line = f"Size: **{get_formatted_size(current_downloaded)}** / **{get_formatted_size(total_downloaded)}**"

        await hm.edit(
            f"{head_text}\n{progress_bar}\n{speed_line}\n{time_line}\n{size_line}",
            parse_mode="markdown",
        )

    uuid = str(uuid4())
    thumbnail = download_image_to_bytesio(data["thumb"], "thumbnail.png")

    try:
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            file=data["direct_link"],
            thumb=thumbnail if thumbnail else None,
            progress_callback=progress_bar,
            caption=f"""
File Name: `{data['file_name']}`
Size: **{data["size"]}**

 @akimaxmovies_2
""",
            supports_streaming=True,
            spoiler=True,
        )

        # pm2 start python3 --name "terabox" -- main.py
    except telethon.errors.rpcerrorlist.WebpageCurlFailedError:
        download = await download_file(
            data["direct_link"], data["file_name"], progress_bar
        )
        if not download:
            return await hm.edit(
                f"𝗦𝗼𝗿𝗿𝘆! 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗙𝗮𝗶𝗹𝗲𝗱 𝗯𝘂𝘁 𝘆𝗼𝘂 𝗰𝗮𝗻 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗶𝘁 𝗳𝗿𝗼𝗺 [here]({data['direct_link']}).",
                parse_mode="markdown",
            )
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            download,
            caption=f"""
File Name: `{data['file_name']}`
Size: **{data["size"]}**

 @akimaxmovies_2
""",
            progress_callback=progress_bar,
            thumb=thumbnail if thumbnail else None,
            supports_streaming=True,
            spoiler=True,
        )
        try:
            os.unlink(download)
        except Exception as e:
            print(e)
    except Exception:
        return await hm.edit(
            f"𝗦𝗼𝗿𝗿𝘆! 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗙𝗮𝗶𝗹𝗲𝗱 𝗯𝘂𝘁 𝘆𝗼𝘂 𝗰𝗮𝗻 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗶𝘁 𝗳𝗿𝗼𝗺 [here]({data['direct_link']}).",
            parse_mode="markdown",
        )
    try:
        os.unlink(download)
    except Exception as e:
        pass
    try:
        await hm.delete()
    except Exception as e:
        print(e)

    if shorturl:
        db.set(shorturl, file.id)
    if file:
        db.set(uuid, file.id)

        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[file.id],
                to_peer=m.chat.id,
                top_msg_id=m.id,
                drop_author=True,
                # noforwards=True,  #Uncomment it if you dont want to forward the media.
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )
        db.set(m.sender_id, time.monotonic(), ex=60)
        db.set(
            f"check_{m.sender_id}",
            int(count) + 1 if count else 1,
            ex=3600,
        )


bot.start(bot_token=BOT_TOKEN)
print("Bot started!")
print(f"This bot is connected to {BOT_USERNAME}.")
print("𝗧𝗵𝗶𝘀 𝗯𝗼𝘁 𝗶𝘀 𝗱𝗲𝗽𝗹𝗼𝘆𝗲𝗱 𝗯𝘆 @𝗮𝗸𝗶𝗺𝗮𝘅𝗺𝗼𝘃𝗶𝗲𝘀_𝟮 𝗸𝗶𝗻𝗱𝗹𝘆 𝗷𝗼𝗶𝗻 𝘁𝗵𝗶𝘀 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗼𝗿 𝗺𝗼𝗿𝗲 𝘂𝗽𝗱𝗮𝘁𝗲𝘀.")
bot.run_until_disconnected()
