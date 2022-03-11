import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import START_MSG, CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from utils import Media, get_file_details, get_size
from pyrogram.errors import UserNotParticipant
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
                              InlineKeyboardButton("♥️ 𝙹𝙾𝙸𝙽 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 ♥️", url=invite_link.invite_link)                           
                            ],
                            [
                                InlineKeyboardButton("♻️ 𝚃𝚁𝚈 𝙰𝙶𝙰𝙸𝙽 ♻️", callback_data=f"checksub#{file_id}")
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
                        InlineKeyboardButton('✅ 𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴 ✅', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')
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
            text="**Please Join My Updates Channel To Use This Bot..🙂!**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("♥️ 𝙹𝙾𝙸𝙽 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 ♥️", url=invite_link.invite_link)
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
                        InlineKeyboardButton('✅ 𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴 ✅', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')
                    ],
                    [
                        InlineKeyboardButton("♥️ 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 ♥️", url="https://t.me/MWUpdatez"),
                        InlineKeyboardButton("⚡ 𝙰𝙱𝙾𝚄𝚃 ⚡", callback_data="about")
                    ],
                    [
                        InlineKeyboardButton("♻️ 𝚂𝙴𝙰𝚁𝙲𝙷 𝙷𝙴𝚁𝙴 ♻️", switch_inline_query_current_chat='')
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

    text = '📑 **Indexed channels/groups**\n'
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
    msg = await message.reply("𝙰𝙲𝙲𝙴𝚂𝚂𝙸𝙽𝙶 𝙵𝙸𝙻𝙴𝚂....🙈", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')


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
            InlineKeyboardButton("♥️ CHAИИΞL ♥️", url="https://t.me/MWUpdatez"),
            InlineKeyboardButton("⚡ ΛBOUT ⚡", callback_data="about")
        ],
        [
            InlineKeyboardButton("♻️ SΞARCH HΞRΞ ♻️", switch_inline_query_current_chat='')
        ]
        ]
    await message.reply(text="<b>╭━━━━━━━━━━━━━━━➣</b>\n<b>┣⪼ 𝙼𝚈 𝙽𝙰𝙼𝙴 ›› <a href='https://t.me/Search010Bot'>𝙼𝚂 𝙱𝙾𝚃</a></b>\n<b>┣⪼ 𝙲𝚁𝙴𝙰𝚃𝙾𝚁 ›› <a href='https://t.me/Aadhi011/'>ꪖꪖᦔꫝỉ </a></b>\n<b>┣⪼ 𝚂𝙾𝚄𝚁𝙲𝙴 𝙲𝙾𝙳𝙴 ›› <a href='https://github.com/Aadhi000/Movies-Search-Bot-MW'>𝙼𝚂-𝙱𝙾𝚃</a></b>\n<b>┣⪼ 𝙳𝙰𝚃𝙰𝙱𝙰𝚂𝙴 ›› 𝙼𝙾𝙽𝙶𝙾 𝙳𝙱</b>\n<b>┣⪼ 𝙻𝙸𝙱𝚁𝙰𝚁𝚈 ›› 𝙿𝚈𝚁𝙾𝙶𝚁𝙰𝙼</b>\n<b>┣⪼ 𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴 ›› 𝙿𝚈𝚃𝙷𝙾𝙽</b>\n<b>╰━━━━━━━━━━━━━━━➣</b>", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
        

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("𝙰𝙲𝙲𝙴𝚂𝚂𝙸𝙽𝙶 𝙵𝙸𝙻𝙴𝚂....🙈", quote=True)
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
            InlineKeyboardButton('✅ 𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴 ✅', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')          
        ]
        ]
    await message.reply(text="<b>╭━━━━━━━━━━━━━━━➣</b>\n<b>┣⪼ 𝙼𝚈 𝙽𝙰𝙼𝙴 ›› <a href='https://t.me/Search010Bot'>𝙼𝚂 𝙱𝙾𝚃</a></b>\n<b>┣⪼ 𝙲𝚁𝙴𝙰𝚃𝙾𝚁 ›› <a href='https://t.me/Aadhi011/'>ꪖꪖᦔꫝỉ </a></b>\n<b>┣⪼ 𝚂𝙾𝚄𝚁𝙲𝙴 𝙲𝙾𝙳𝙴 ›› <a href='https://github.com/Aadhi000/Movies-Search-Bot-MW'>𝙼𝚂-𝙱𝙾𝚃</a></b>\n<b>┣⪼ 𝙳𝙰𝚃𝙰𝙱𝙰𝚂𝙴 ›› 𝙼𝙾𝙽𝙶𝙾 𝙳𝙱</b>\n<b>┣⪼ 𝙻𝙸𝙱𝚁𝙰𝚁𝚈 ›› 𝙿𝚈𝚁𝙾𝙶𝚁𝙰𝙼</b>\n<b>┣⪼ 𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴 ›› 𝙿𝚈𝚃𝙷𝙾𝙽</b>\n<b>╰━━━━━━━━━━━━━━━➣</b>", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

@Client.on_message(filters.command('help'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('✅ 𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴 ✅', url='https://youtube.com/channel/UCf_dVNrilcT0V2R--HbYpMA')          
        ]
        ]
