import os
import logging
from pyrogram import Client, filters
from Script import script
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import START_MSG, CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from utils import Media, get_file_details, get_size
from pyrogram.errors import UserNotParticipant
from database.users_chats_db import db
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start"))
async def start(bot, cmd):
    usr_cmdall1 = cmd.text
    if usr_cmdall1.startswith("/start subinps"):
        if AUTH_CHANNEL:
            invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
            try:
                user = await bot.get_chat_member(int(AUTH_CHANNEL), cmd.from_user.id)
                if user.status == "kicked":
                    await bot.send_message(
                        chat_id=cmd.from_user.id,
                        text="Sorry Sir, You are Banned to use me.",
                        parse_mode="markdown",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                ident, file_id = cmd.text.split("_-_-_-_")
                await bot.send_message(
                    chat_id=cmd.from_user.id,
                    text="**Please Join My Updates Channel to use this Bot!**",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [ 
                                InlineKeyboardButton("β₯οΈ πΉπΎπΈπ½ π²π·π°π½π½π΄π» β₯οΈ", url=invite_link.invite_link)                           
                            ],
                            [
                                InlineKeyboardButton("β»οΈ πππ π°πΆπ°πΈπ½ β»οΈ", callback_data=f"checksub#{file_id}")
                            ]
                        ]
                    ),
                    parse_mode="markdown"
                )
                return
            except Exception:
                await bot.send_message(
                    chat_id=cmd.from_user.id,
                    text="Something went Wrong.",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        try:
            ident, file_id = cmd.text.split("_-_-_-_")
            filedetails = await get_file_details(file_id)
            for files in filedetails:
                title = files.file_name
                size=get_size(files.file_size)
                f_caption=files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                    except Exception as e:
                        print(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{files.file_name}"
                buttons = [
                    [                
                        InlineKeyboardButton('β πππ±ππ²ππΈπ±π΄ β', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')
                    ]
                    ]
                await bot.send_cached_media(
                    chat_id=cmd.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                    )
        except Exception as err:
            await cmd.reply_text(f"Something went wrong!\n\n**Error:** `{err}`")
    elif len(cmd.command) > 1 and cmd.command[1] == 'subscribe':
        invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="**Please Join My Updates Channel To Use This Bot..π!**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("β₯οΈ πΉπΎπΈπ½ π²π·π°π½π½π΄π» β₯οΈ", url=invite_link.invite_link)
                    ]
                ]
            )
        )
    else:
        await cmd.reply_text(  
            START_MSG,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('β πππ±ππ²ππΈπ±π΄ β', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')
                    ],
                    [
                        InlineKeyboardButton("β₯οΈ π²π·π°π½π½π΄π» β₯οΈ", url="https://t.me/MWUpdatez"),
                        InlineKeyboardButton("β‘ π°π±πΎππ β‘", callback_data="about")
                    ],
                    [
                        InlineKeyboardButton("β»οΈ ππ΄π°ππ²π· π·π΄ππ΄ β»οΈ", switch_inline_query_current_chat='')
                    ]
                ]
            )
        )


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = 'π **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("π°π²π²π΄πππΈπ½πΆ π΅πΈπ»π΄π....π", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'π Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')

@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply('π°π²π²π΄πππΈπ½πΆ πππ°πππ π³π΄ππ°πΈπ»π...')
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    await rju.edit(script.STATUS_TXT.format(files, total_users, totl_chats, size, free))


@Client.on_message(filters.command('logger') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('start'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('β πππ±ππ²ππΈπ±π΄ β', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')
        ],
        [
            InlineKeyboardButton("β₯οΈ CHAΠΠΞL β₯οΈ", url="https://t.me/MWUpdatez"),
            InlineKeyboardButton("β‘ ΞBOUT β‘", callback_data="about")
        ],
        [
            InlineKeyboardButton("β»οΈ SΞARCH HΞRΞ β»οΈ", switch_inline_query_current_chat='')
        ]
        ]
    await message.reply(text="<b>β­ββββββββββββββββ£</b>\n<b>β£βͺΌ πΌπ π½π°πΌπ΄ βΊβΊ <a href='https://t.me/Search010Bot'>πΌπ π±πΎπ</a></b>\n<b>β£βͺΌ π²ππ΄π°ππΎπ βΊβΊ <a href='https://t.me/Aadhi011/'>κͺκͺα¦κ«α» </a></b>\n<b>β£βͺΌ ππΎπππ²π΄ π²πΎπ³π΄ βΊβΊ <a href='https://github.com/Aadhi000/Movies-Search-Bot-MW'>πΌπ-π±πΎπ</a></b>\n<b>β£βͺΌ π³π°ππ°π±π°ππ΄ βΊβΊ πΌπΎπ½πΆπΎ π³π±</b>\n<b>β£βͺΌ π»πΈπ±ππ°ππ βΊβΊ πΏπππΎπΆππ°πΌ</b>\n<b>β£βͺΌ π»π°π½πΆππ°πΆπ΄ βΊβΊ πΏπππ·πΎπ½</b>\n<b>β°ββββββββββββββββ£</b>", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
        
@Client.on_message(filters.command('home'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('β πππ±ππ²ππΈπ±π΄ β', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')
        ],
        [
            InlineKeyboardButton("β₯οΈ CHAΠΠΞL β₯οΈ", url="https://t.me/MWUpdatez"),
            InlineKeyboardButton("β‘ ΞBOUT β‘", callback_data="about")
        ],
        [
            InlineKeyboardButton("β»οΈ SΞARCH HΞRΞ β»οΈ", switch_inline_query_current_chat='')
        ]
        ]
    await message.reply(text="<b>β­ββββββββββββββββ£</b>\n<b>β£βͺΌ πΌπ π½π°πΌπ΄ βΊβΊ <a href='https://t.me/Search010Bot'>πΌπ π±πΎπ</a></b>\n<b>β£βͺΌ π²ππ΄π°ππΎπ βΊβΊ <a href='https://t.me/Aadhi011/'>κͺκͺα¦κ«α» </a></b>\n<b>β£βͺΌ ππΎπππ²π΄ π²πΎπ³π΄ βΊβΊ <a href='https://github.com/Aadhi000/Movies-Search-Bot-MW'>πΌπ-π±πΎπ</a></b>\n<b>β£βͺΌ π³π°ππ°π±π°ππ΄ βΊβΊ πΌπΎπ½πΆπΎ π³π±</b>\n<b>β£βͺΌ π»πΈπ±ππ°ππ βΊβΊ πΏπππΎπΆππ°πΌ</b>\n<b>β£βͺΌ π»π°π½πΆππ°πΆπ΄ βΊβΊ πΏπππ·πΎπ½</b>\n<b>β°ββββββββββββββββ£</b>", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
        



@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("π°π²π²π΄πππΈπ½πΆ π΅πΈπ»π΄π....π", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return

    result = await Media.collection.delete_one({
        'file_name': media.file_name,
        'file_size': media.file_size,
        'mime_type': media.mime_type
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        await msg.edit('File not found in database')
@Client.on_message(filters.command('about'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('β πππ±ππ²ππΈπ±π΄ β', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')
        ]
        ]
    await message.reply(text="<b>β­ββββββββββββββββ£</b>\n<b>β£βͺΌ πΌπ π½π°πΌπ΄ βΊβΊ <a href='https://t.me/Search010Bot'>πΌπ π±πΎπ</a></b>\n<b>β£βͺΌ π²ππ΄π°ππΎπ βΊβΊ <a href='https://t.me/Aadhi011/'>κͺκͺα¦κ«α» </a></b>\n<b>β£βͺΌ ππΎπππ²π΄ π²πΎπ³π΄ βΊβΊ <a href='https://github.com/Aadhi000/Movies-Search-Bot-MW'>πΌπ-π±πΎπ</a></b>\n<b>β£βͺΌ π³π°ππ°π±π°ππ΄ βΊβΊ πΌπΎπ½πΆπΎ π³π±</b>\n<b>β£βͺΌ π»πΈπ±ππ°ππ βΊβΊ πΏπππΎπΆππ°πΌ</b>\n<b>β£βͺΌ π»π°π½πΆππ°πΆπ΄ βΊβΊ πΏπππ·πΎπ½</b>\n<b>β°ββββββββββββββββ£</b>", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

@Client.on_message(filters.command('help'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('β πππ±ππ²ππΈπ±π΄ β', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')
        ]
        ]
