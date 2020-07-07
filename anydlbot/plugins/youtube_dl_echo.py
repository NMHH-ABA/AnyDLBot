#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

import asyncio
import aiohttp
import json
import math
import os
import time
import shutil
from datetime import datetime

from anydlbot import(
        AUTH_USERS,
        HTTP_PROXY,
        DOWNLOAD_LOCATION,
        DEF_THUMB_NAIL_VID_S,
        TG_MAX_FILE_SIZE
)

# the Strings used for this "thing"
from translation import Translation

from pyrogram import(
        Client,
        Filters,
        InlineKeyboardButton,
        InlineKeyboardMarkup
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from anydlbot.helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from anydlbot.helper_funcs.help_uploadbot import DownLoadFile
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image
from anydlbot.helper_funcs.help_Nekmo_ffmpeg import generate_screen_shots

import random

@Client.on_message(Filters.regex(pattern=".*http.*"))
async def echo(bot, update):
    if update.from_user.id not in AUTH_USERS:
        await update.delete()
        return
    # LOGGER.info(update)
    # await bot.send_chat_action(
    #     chat_id=update.chat.id,
    #     action="typing"
    # )
    LOGGER.info(update.from_user)
    url = update.text
    if url.count("|") == 2:
        shomar = random.randint(1, 10000)
        # youtube_dl extractors
        youtube_dl_url, custom_file_name, youtube_dl_format = url.split(" | ")
        if ") FullHD" in custom_file_name:
            await bot.send_message(
                text=Translation.DOWNLOAD_START,
                chat_id=update.chat.id,
                reply_to_message_id=update.message_id,
            )
            description = "@BachehayeManoto FullHD"
            custom_file_name = custom_file_name + ".mp4"
            tmp_directory_for_each_user = DOWNLOAD_LOCATION + "/" + str(shomar)
            if not os.path.isdir(tmp_directory_for_each_user):
                os.makedirs(tmp_directory_for_each_user)
            download_directory = tmp_directory_for_each_user + "/" + custom_file_name
            command_to_exec = []
            # command_to_exec = ["youtube-dl", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
            command_to_exec = [
                "youtube-dl",
                "-c",
                "--max-filesize", str(TG_MAX_FILE_SIZE),
                "--embed-subs",
                "-f", youtube_dl_format,
                "--hls-prefer-ffmpeg", youtube_dl_url,
                "-o", download_directory
            ]
            command_to_exec.append("--no-warnings")
            # command_to_exec.append("--quiet")
            LOGGER.info(command_to_exec)
            start = datetime.now()
            process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                # stdout must a pipe to be accessible as process.stdout
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # Wait for the subprocess to finish
            stdout, stderr = await process.communicate()
            e_response = stderr.decode().strip()
            t_response = stdout.decode().strip()
            LOGGER.info(e_response)
            LOGGER.info(t_response)
            ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
            if e_response and ad_string_to_replace in e_response:
                error_message = e_response.replace(ad_string_to_replace, "")
                await update.edit_text(
                    caption=error_message
                )

                return False
            if t_response:
                # logger.info(t_response)
                end_one = datetime.now()
                time_taken_for_download = (end_one - start).seconds
                file_size = TG_MAX_FILE_SIZE + 1
                try:
                    file_size = os.stat(download_directory).st_size
                except FileNotFoundError as exc:
                    download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
                    # https://stackoverflow.com/a/678242/4723940
                    file_size = os.stat(download_directory).st_size
                if file_size > TG_MAX_FILE_SIZE:
                    await update.edit_text(
                        caption=Translation.RCHD_TG_API_LIMIT.format(
                            time_taken_for_download,
                            humanbytes(file_size)
                        )
                    )
                else:
                    is_w_f = False
                    images = await generate_screen_shots(
                        custom_file_name,
                        tmp_directory_for_each_user,
                        is_w_f,
                        "",
                        300,
                        9
                    )
                    LOGGER.info(images)
                    await update.edit_text(
                        caption=Translation.UPLOAD_START
                    )
                    # get the correct width, height, and duration for videos greater than 10MB
                    width = 0
                    height = 0
                    duration = 0
                    if tg_send_type != "file":
                        metadata = extractMetadata(createParser(custom_file_name))
                        if metadata is not None:
                            if metadata.has("duration"):
                                duration = metadata.get('duration').seconds
                    # get the correct width, height, and duration for videos greater than 10MB
                    if os.path.exists(thumb_image_path):
                        width = 0
                        height = 90

                        # resize image
                        # ref: https://t.me/PyrogramChat/44663
                        # https://stackoverflow.com/a/21669827/4723940
                        Image.open(thumb_image_path).convert(
                            "RGB").save(thumb_image_path)
                        img = Image.open(thumb_image_path)
                        # https://stackoverflow.com/a/37631799/4723940
                        # img.thumbnail((90, 90))
                        if tg_send_type == "file":
                            img.resize((320, height))
                        else:
                            img.resize((90, height))
                        img.save(thumb_image_path, "JPEG")
                        # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails

                        metadata = extractMetadata(createParser(thumb_image_path))
                        if metadata.has("width"):
                            width = metadata.get("width")
                        if metadata.has("height"):
                            height = metadata.get("height")
                        if tg_send_type == "vm":
                            height = width
                    else:
                        thumb_image_path = None
                    start_time = time.time()
                    # try to upload file
                    await bot.send_document(
                        chat_id=update.chat.id,
                        document=download_directory,
                        # thumb=thumb_image_path,
                        caption=description,
                        parse_mode="HTML",
                        # reply_markup=reply_markup,
                        reply_to_message_id=update.message_id + 1,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            Translation.UPLOAD_START,
                            update,
                            start_time
                        )
                    )
                    end_two = datetime.now()
                    time_taken_for_upload = (end_two - end_one).seconds
                    #
                    media_album_p = []
                    if images is not None:
                        i = 0
                        # caption = "© @AnyDLBot"
                        if is_w_f:
                            caption = "/upgrade to Plan D to remove the watermark\n© @AnyDLBot"
                        for image in images:
                            if os.path.exists(image):
                                if i == 0:
                                    media_album_p.append(
                                        InputMediaPhoto(
                                            media=image,
                                            caption=caption,
                                            parse_mode="html"
                                        )
                                    )
                                else:
                                    media_album_p.append(
                                        InputMediaPhoto(
                                            media=image
                                        )
                                    )
                                i = i + 1
                    await bot.send_media_group(
                        chat_id=update.chat.id,
                        disable_notification=True,
                        reply_to_message_id=update.message_id + 1,
                        media=media_album_p
                    )
                    #
                    try:
                        shutil.rmtree(tmp_directory_for_each_user)
                        os.remove(thumb_image_path)
                    except:
                        pass
                    await bot.edit_message_text(
                        text="Downloaded in {} seconds. \nUploaded in {} seconds.".format(time_taken_for_download,
                                                                                          time_taken_for_upload),
                        chat_id=update.chat.id,
                        message_id=update.message_id + 1,
                        disable_web_page_preview=True
                    )
    else:
        youtube_dl_username = None
        youtube_dl_password = None
        file_name = None
        if "|" in url:
            url_parts = url.split("|")
            if len(url_parts) == 2:
                url = url_parts[0]
                file_name = url_parts[1]
            elif len(url_parts) == 4:
                url = url_parts[0]
                file_name = url_parts[1]
                youtube_dl_username = url_parts[2]
                youtube_dl_password = url_parts[3]
            else:
                for entity in update.entities:
                    if entity.type == "text_link":
                        url = entity.url
                    elif entity.type == "url":
                        o = entity.offset
                        l = entity.length
                        url = url[o:o + l]
            if url is not None:
                url = url.strip()
            if file_name is not None:
                file_name = file_name.strip()
            # https://stackoverflow.com/a/761825/4723940
            if youtube_dl_username is not None:
                youtube_dl_username = youtube_dl_username.strip()
            if youtube_dl_password is not None:
                youtube_dl_password = youtube_dl_password.strip()
            LOGGER.info(url)
            LOGGER.info(file_name)
        else:
            for entity in update.entities:
                if entity.type == "text_link":
                    url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    url = url[o:o + l]
        if HTTP_PROXY is not None:
            command_to_exec = [
                "youtube-dl",
                "--no-warnings",
                "--youtube-skip-dash-manifest",
                "-j",
                url,
                "--proxy", HTTP_PROXY
            ]
        else:
            command_to_exec = [
                "youtube-dl",
                "--no-warnings",
                "--youtube-skip-dash-manifest",
                "-j",
                url
            ]
        if youtube_dl_username is not None:
            command_to_exec.append("--username")
            command_to_exec.append(youtube_dl_username)
        if youtube_dl_password is not None:
            command_to_exec.append("--password")
            command_to_exec.append(youtube_dl_password)
        # logger.info(command_to_exec)
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        # logger.info(e_response)
        t_response = stdout.decode().strip()
        # logger.info(t_response)
        # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
        if e_response and "nonnumeric port" not in e_response:
            # logger.warn("Status : FAIL", exc.returncode, exc.output)
            error_message = e_response.replace("please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
            if "This video is only available for registered users." in error_message:
                error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
            await update.reply_text(
                text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
                quote=True,
                parse_mode="html",
                disable_web_page_preview=True
            )
            return False
        if t_response:
            # logger.info(t_response)
            x_reponse = t_response
            if "\n" in x_reponse:
                x_reponse, _ = x_reponse.split("\n")
            response_json = json.loads(x_reponse)
            save_ytdl_json_path = DOWNLOAD_LOCATION + \
                "/" + str(update.from_user.id) + ".json"
            with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
                json.dump(response_json, outfile, ensure_ascii=False)
            # logger.info(response_json)
            inline_keyboard = []
            duration = None
            if "duration" in response_json:
                duration = response_json["duration"]
            if "formats" in response_json:
                for formats in response_json["formats"]:
                    format_id = formats.get("format_id")
                    format_string = formats.get("format_note")
                    if format_string is None:
                        format_string = formats.get("format")
                    format_ext = formats.get("ext")
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    cb_string_video = "{}-{}-{}".format(
                        "video", format_id, format_ext)
                    cb_string_file = "{}-{}-{}".format(
                        "file", format_id, format_ext)
                    if format_string is not None and not "audio only" in format_string:
                        ikeyboard = [
                            InlineKeyboardButton(
                                "S " + format_string + " video " + approx_file_size + " ",
                                callback_data=(cb_string_video).encode("UTF-8")
                            ),
                            InlineKeyboardButton(
                                "D " + format_ext + " " + approx_file_size + " ",
                                callback_data=(cb_string_file).encode("UTF-8")
                            )
                        ]
                        """if duration is not None:
                            cb_string_video_message = "{}|{}|{}".format(
                                "vm", format_id, format_ext)
                            ikeyboard.append(
                                pyrogram.InlineKeyboardButton(
                                    "VM",
                                    callback_data=(
                                        cb_string_video_message).encode("UTF-8")
                                )
                            )"""
                    else:
                        # special weird case :\
                        ikeyboard = [
                            InlineKeyboardButton(
                                "SVideo [" +
                                "] ( " +
                                approx_file_size + " )",
                                callback_data=(cb_string_video).encode("UTF-8")
                            ),
                            InlineKeyboardButton(
                                "DFile [" +
                                "] ( " +
                                approx_file_size + " )",
                                callback_data=(cb_string_file).encode("UTF-8")
                            )
                        ]
                    inline_keyboard.append(ikeyboard)
                if duration is not None:
                    cb_string_64 = "{}-{}-{}".format("audio", "64k", "mp3")
                    cb_string_128 = "{}-{}-{}".format("audio", "128k", "mp3")
                    cb_string = "{}-{}-{}".format("audio", "320k", "mp3")
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            "MP3 " + "(" + "64 kbps" + ")", callback_data=cb_string_64.encode("UTF-8")),
                        InlineKeyboardButton(
                            "MP3 " + "(" + "128 kbps" + ")", callback_data=cb_string_128.encode("UTF-8"))
                    ])
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            "MP3 " + "(" + "320 kbps" + ")", callback_data=cb_string.encode("UTF-8"))
                    ])
            else:
                format_id = response_json["format_id"]
                format_ext = response_json["ext"]
                cb_string_file = "{}-{}-{}".format(
                    "file", format_id, format_ext)
                cb_string_video = "{}-{}-{}".format(
                    "video", format_id, format_ext)
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "SVideo",
                        callback_data=(cb_string_video).encode("UTF-8")
                    ),
                    InlineKeyboardButton(
                        "DFile",
                        callback_data=(cb_string_file).encode("UTF-8")
                    )
                ])
                cb_string_file = "{}={}={}".format(
                    "file", format_id, format_ext)
                cb_string_video = "{}={}={}".format(
                    "video", format_id, format_ext)
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "video",
                        callback_data=(cb_string_video).encode("UTF-8")
                    ),
                    InlineKeyboardButton(
                        "file",
                        callback_data=(cb_string_file).encode("UTF-8")
                    )
                ])
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            # logger.info(reply_markup)
            thumbnail = DEF_THUMB_NAIL_VID_S
            thumbnail_image = DEF_THUMB_NAIL_VID_S
            if "thumbnail" in response_json:
                if response_json["thumbnail"] is not None:
                    thumbnail = response_json["thumbnail"]
                    thumbnail_image = response_json["thumbnail"]
            thumb_image_path = DownLoadFile(
                thumbnail_image,
                DOWNLOAD_LOCATION + "/" +
                str(update.from_user.id) + ".jpg",
                128,
                None,  # bot,
                Translation.DOWNLOAD_START,
                update.message_id,
                update.chat.id
            )
            await update.reply_photo(
                photo=thumb_image_path,
                quote=True,
                caption=Translation.FORMAT_SELECTION.format(thumbnail) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
                reply_markup=reply_markup,
                parse_mode="html"
            )
        else:
            # fallback for nonnumeric port a.k.a seedbox.io
            inline_keyboard = []
            cb_string_file = "{}={}={}".format(
                "file", "LFO", "NONE")
            cb_string_video = "{}={}={}".format(
                "video", "OFL", "ENON")
            inline_keyboard.append([
                InlineKeyboardButton(
                    "SVideo",
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                InlineKeyboardButton(
                    "DFile",
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            await update.reply_photo(
                photo=DEF_THUMB_NAIL_VID_S,
                quote=True,
                caption=Translation.FORMAT_SELECTION.format(""),
                reply_markup=reply_markup,
                parse_mode="html",
                reply_to_message_id=update.message_id
            )
