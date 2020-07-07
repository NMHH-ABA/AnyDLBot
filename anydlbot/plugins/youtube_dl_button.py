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
import shutil
import time
from datetime import datetime

from anydlbot import(
        DOWNLOAD_LOCATION,
        TG_MAX_FILE_SIZE,
        HTTP_PROXY
)

# the Strings used for this "thing"
from translation import Translation

from pyrogram import InputMediaPhoto
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from anydlbot.helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from anydlbot.helper_funcs.help_uploadbot import DownLoadFile
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image
from anydlbot.helper_funcs.help_Nekmo_ffmpeg import generate_screen_shots

from urllib.request import urlopen
from urllib.request import urlretrieve
import random


async def youtube_dl_call_back(bot, update):
    shomar = random.randint(1, 10000)
    cb_data = update.data
    if "|" in cb_data:
        tg_send_type, vttype, clipid = cb_data.split("|")
        thumb_image_path = DOWNLOAD_LOCATION + \
                           "/" + str(shomar) + ".jpg"
        if vttype == "hls":
            link = "https://dak1vd5vmi7x6.cloudfront.net/api/v1/publicrole/showmodule/episodedetails?id=" + clipid
            f = urlopen(link)
            myfile = f.read()
            jconv = json.loads(myfile)
            details = jconv["details"]
            description = "@BachehayeManoto پنج دقیقه ابتدایی\n" + details["episodeDescription"]
            if len(description) > 1024:
                description = "@BachehayeManoto پنج دقیقه ابتدایی\n" + details["episodeShareDescription"]
            videoCliplandscapeImgIxUrl = details["episodelandscapeImgIxUrl"]
            custom_file_name = "@BachehayeManoto " + details["formattedEpisodeTitle"] + ".mp4"
            durationInMinutes = details["durationInMinutes"]
            durationhls = durationInMinutes * 60
            youtube_dl_url_org = details["videoM3u8Url"]
            youtube_dl_url = youtube_dl_url_org.replace(".m3u8", "_750.m3u8")
        if vttype == "full":
            link = "https://dak1vd5vmi7x6.cloudfront.net/api/v1/publicrole/showmodule/episodedetails?id=" + clipid
            f = urlopen(link)
            myfile = f.read()
            jconv = json.loads(myfile)
            details = jconv["details"]
            description = "@BachehayeManoto\n" + details["episodeDescription"]
            if len(description) > 1024:
                description = "@BachehayeManoto\n" + details["episodeShareDescription"]
            videoCliplandscapeImgIxUrl = details["episodelandscapeImgIxUrl"]
            custom_file_name = "@BachehayeManoto " + details["formattedEpisodeTitle"] + ".mp4"
            durationInMinutes = details["durationInMinutes"]
            durationhls = durationInMinutes * 60
            youtube_dl_url = details["videoM3u8Url"]
        if vttype == "news":
            link = "https://dr905zevbmkvz.cloudfront.net/api/v1/publicrole/newsmodule/banner"
            f = urlopen(link)
            myfile = f.read()
            jconv = json.loads(myfile)
            details = jconv["details"]
            description = "@BachehayeManoto\n" + details["headline"] + details["strapline1"]
            custom_file_name = "@BachehayeManoto " + details["headline"] + " " + details["strapline1"] + ".mp3"
            videoCliplandscapeImgIxUrl = details["landscapeImgIxUrl"]

            link2 = "https://dak1vd5vmi7x6.cloudfront.net/api/v1/publicrole/newsmodule/newsvideo"
            f2 = urlopen(link2)
            myfile2 = f2.read()
            jconv2 = json.loads(myfile2)
            details2 = jconv2["details"]
            youtube_dl_url = details2["videoDownloadUrl"]
            durationInMinutes = details2["durationInMinutes"]
            duration = durationInMinutes * 60
            performer = details["headline"] + details["strapline1"]
            BachehayeManoto = "@BachehayeManoto"
        try:
            urlretrieve(videoCliplandscapeImgIxUrl,
                        thumb_image_path)
        except:
            pass
        await update.message.edit_caption(
            caption="در حال دانلود ..."
        )
        tmp_directory_for_each_user = DOWNLOAD_LOCATION + "/" + str(shomar)
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        download_directory = tmp_directory_for_each_user + "/" + custom_file_name
        command_to_exec = []
        if tg_send_type == "audio":
            command_to_exec = [
                "ffmpeg",
                "-i", youtube_dl_url,
                "-vn",
                "-ar", "44100",
                "-ac", "2",
                "-ab", "96",
                "-f", "mp3",
                download_directory,
            ]
        elif tg_send_type == "file":
            command_to_exec = [
                "youtube-dl",
                "-c",
                "-f", "best[height=720]",
                "--hls-prefer-ffmpeg", youtube_dl_url,
                "-o", download_directory
            ]
        else:
            command_to_exec = [
                "ffmpeg",
                "-i", youtube_dl_url,
                "-ss", "00:00:00",
                "-codec", "copy",
                "-t", "300",
                download_directory
            ]
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
            await update.message.edit_caption(
                caption=error_message
            )
            return False
        else:
            # logger.info(t_response)
            end_one = datetime.now()
            time_taken_for_download = (end_one - start).seconds
            try:
                file_size = os.stat(download_directory).st_size
            except FileNotFoundError as exc:
                youtube_dl_url = youtube_dl_url_org.replace(".m3u8", "_750_.m3u8")
                command_to_exec = [
                    "ffmpeg",
                    "-i", youtube_dl_url,
                    "-ss", "00:00:00",
                    "-codec", "copy",
                    "-t", "300",
                    download_directory
                ]
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
                try:
                    file_size = os.stat(download_directory).st_size
                except FileNotFoundError as exc:
                    await update.message.edit_caption(
                        caption="متاسفانه فایل در دسترس نیست!"
                    )
            if file_size > TG_MAX_FILE_SIZE:
                await update.message.edit_caption(
                    caption=Translation.RCHD_TG_API_LIMIT.format(
                        time_taken_for_download,
                        humanbytes(file_size)
                    )
                )
            else:
                await update.message.edit_caption(
                    caption="در حال آپلود ..."
                )
                # get the correct width, height, and duration for videos greater than 10MB
                # ref: message from @BotSupport
                width = 0
                height = 0
                # get the correct width, height, and duration for videos greater than 10MB
                if os.path.exists(thumb_image_path):
                    width = 0
                    height = 0
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    if tg_send_type == "vm":
                        height = width
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
                else:
                    thumb_image_path = None
                start_time = time.time()
                # try to upload file
                if tg_send_type == "audio":
                    await bot.send_audio(
                        chat_id=update.message.chat.id,
                        audio=download_directory,
                        caption=description,
                        parse_mode="HTML",
                        duration=duration,
                        performer=performer,
                        title=BachehayeManoto,
                        # reply_markup=reply_markup,
                        thumb=thumb_image_path,
                        reply_to_message_id=update.message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "در حال آپلود ...",
                            update.message,
                            start_time
                        )
                    )
                elif tg_send_type == "file":
                    await bot.send_document(
                        chat_id=update.message.chat.id,
                        document=download_directory,
                        thumb=thumb_image_path,
                        caption=description,
                        parse_mode="HTML",
                        # reply_markup=reply_markup,
                        reply_to_message_id=update.message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "در حال آپلود ...",
                            update.message,
                            start_time
                        )
                    )
                elif tg_send_type == "video":
                    await bot.send_video(
                        chat_id=update.message.chat.id,
                        video=download_directory,
                        caption=description,
                        parse_mode="HTML",
                        duration=300,
                        width=width,
                        height=height,
                        supports_streaming=True,
                        # reply_markup=reply_markup,
                        thumb=thumb_image_path,
                        reply_to_message_id=update.message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "در حال آپلود ...",
                            update.message,
                            start_time
                        )
                    )
                else:
                    logger.info("Did this happen? :\\")
                end_two = datetime.now()
                time_taken_for_upload = (end_two - end_one).seconds
                try:
                    shutil.rmtree(tmp_directory_for_each_user)
                    os.remove(thumb_image_path)
                except:
                    pass
                await bot.edit_message_text(
                    text="Downloaded in {} seconds. \nUploaded in {} seconds.".format(time_taken_for_download,
                                                                                      time_taken_for_upload),
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id,
                    disable_web_page_preview=True
                )
    if "-" in cb_data:
        # youtube_dl extractors
        tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("-")
        thumb_image_path = DOWNLOAD_LOCATION + \
                           "/" + str(update.from_user.id) + ".jpg"
        save_ytdl_json_path = DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        try:
            with open(save_ytdl_json_path, "r", encoding="utf8") as f:
                response_json = json.load(f)
        except (FileNotFoundError) as e:
            await update.message.delete()
            return False
        youtube_dl_url = update.message.reply_to_message.text
        custom_file_name = str(response_json.get("title")) + \
            "_" + youtube_dl_format + "." + youtube_dl_ext
        youtube_dl_username = None
        youtube_dl_password = None
        if "|" in youtube_dl_url:
            url_parts = youtube_dl_url.split("|")
            if len(url_parts) == 2:
                youtube_dl_url = url_parts[0]
                custom_file_name = url_parts[1]
                if len(custom_file_name) > 64:
                    await update.message.reply_text(
                        Translation.IFLONG_FILE_NAME.format(
                            alimit="64",
                            num=len(custom_file_name)
                        )
                    )
                    return
            elif len(url_parts) == 4:
                youtube_dl_url = url_parts[0]
                custom_file_name = url_parts[1]
                youtube_dl_username = url_parts[2]
                youtube_dl_password = url_parts[3]
            else:
                for entity in update.message.reply_to_message.entities:
                    if entity.type == "text_link":
                        youtube_dl_url = entity.url
                    elif entity.type == "url":
                        o = entity.offset
                        l = entity.length
                        youtube_dl_url = youtube_dl_url[o:o + l]
            if youtube_dl_url is not None:
                youtube_dl_url = youtube_dl_url.strip()
            if custom_file_name is not None:
                custom_file_name = custom_file_name.strip()
            # https://stackoverflow.com/a/761825/4723940
            if youtube_dl_username is not None:
                youtube_dl_username = youtube_dl_username.strip()
            if youtube_dl_password is not None:
                youtube_dl_password = youtube_dl_password.strip()
            LOGGER.info(youtube_dl_url)
            LOGGER.info(custom_file_name)
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    youtube_dl_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
        await update.message.edit_caption(
            caption=Translation.DOWNLOAD_START
        )
        description = "@BachehayeManoto"
        custom_file_name = custom_file_name + ".mp4"
        if ") FullHD" in custom_file_name:
            description = "@BachehayeManoto FullHD"
        if ") HD." in custom_file_name:
            description = "@BachehayeManoto HD"
        if ") Mobile." in custom_file_name:
            description = "@BachehayeManoto\nنسخه کم حجم مناسب موبایل"
        tmp_directory_for_each_user = DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        download_directory = tmp_directory_for_each_user + "/" + custom_file_name
        command_to_exec = []
        if tg_send_type == "audio":
            command_to_exec = [
                "youtube-dl",
                "-c",
                "--max-filesize", str(TG_MAX_FILE_SIZE),
                "--prefer-ffmpeg",
                "--extract-audio",
                "--audio-format", youtube_dl_ext,
                "--audio-quality", youtube_dl_format,
                youtube_dl_url,
                "-o", download_directory
            ]
        else:
            # command_to_exec = ["youtube-dl", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
            minus_f_format = youtube_dl_format
            if "youtu" in youtube_dl_url:
                minus_f_format = youtube_dl_format + "+bestaudio"
                command_to_exec = [
                    "youtube-dl",
                    "-f", minus_f_format,
                    "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url,
                    "-o", download_directory
                ]
            else:
                command_to_exec = [
                    "youtube-dl",
                    "-c",
                    "--max-filesize", str(TG_MAX_FILE_SIZE),
                    "--embed-subs",
                    "-f", minus_f_format,
                    "--hls-prefer-ffmpeg", youtube_dl_url,
                    "-o", download_directory
                ]
        command_to_exec.append("--no-warnings")
        # command_to_exec.append("--quiet")
        command_to_exec.append("--restrict-filenames")
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
            await update.message.edit_caption(
                caption=error_message
            )
            return False
        if t_response:
            LOGGER.info(t_response)
            end_one = datetime.now()
            time_taken_for_download = (end_one -start).seconds
            file_size = TG_MAX_FILE_SIZE + 1
            download_directory_dirname = os.path.dirname(download_directory)
            download_directory_contents = os.listdir(download_directory_dirname)
            for download_directory_c in download_directory_contents:
                current_file_name = os.path.join(
                    download_directory_dirname,
                    download_directory_c
                )
                file_size = os.stat(current_file_name).st_size

                if file_size > TG_MAX_FILE_SIZE:
                    await update.message.edit_caption(
                        caption=Translation.RCHD_TG_API_LIMIT.format(
                            time_taken_for_download,
                            humanbytes(file_size)
                        )
                    )
                else:
                    is_w_f = False
                    await update.message.edit_caption(
                        caption=Translation.UPLOAD_START
                    )
                    # get the correct width, height, and duration for videos greater than 10MB
                    # ref: message from @BotSupport
                    width = 0
                    height = 0
                    duration = 0
                    if tg_send_type != "file":
                        metadata = extractMetadata(createParser(current_file_name))
                        if metadata is not None:
                            if metadata.has("duration"):
                                duration = metadata.get('duration').seconds
                    # get the correct width, height, and duration for videos greater than 10MB
                    if os.path.exists(thumb_image_path):
                        width = 0
                        height = 90

                        # resize image
                        # ref: https://t.me/PyrogramChat/44663
                         #https://stackoverflow.com/a/21669827/4723940
                        Image.open(thumb_image_path).convert(
                            "RGB").save(thumb_image_path)
                        img = Image.open(thumb_image_path)
                        # https://stackoverflow.com/a/37631799/4723940
                        #img.thumbnail((90, 90))
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
                    if tg_send_type == "audio":
                        await bot.send_audio(
                            chat_id=update.message.chat.id,
                            audio=download_directory,
                            caption=description,
                            parse_mode="HTML",
                            duration=duration,
                            # performer=response_json["uploader"],
                            # title=response_json["title"],
                            # reply_markup=reply_markup,
                            thumb=thumb_image_path,
                            reply_to_message_id=update.message.reply_to_message.message_id,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                Translation.UPLOAD_START,
                                update.message,
                                start_time
                            )
                        )
                    elif tg_send_type == "file":
                        await bot.send_document(
                            chat_id=update.message.chat.id,
                            document=download_directory,
                            thumb=thumb_image_path,
                            caption=description,
                            parse_mode="HTML",
                            # reply_markup=reply_markup,
                            reply_to_message_id=update.message.reply_to_message.message_id,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                Translation.UPLOAD_START,
                                update.message,
                                start_time
                            )
                        )
                    elif tg_send_type == "vm":
                        await bot.send_video_note(
                            chat_id=update.message.chat.id,
                            video_note=download_directory,
                            duration=duration,
                            length=width,
                            thumb=thumb_image_path,
                            reply_to_message_id=update.message.reply_to_message.message_id,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                Translation.UPLOAD_START,
                                update.message,
                                start_time
                            )
                        )
                    elif tg_send_type == "video":
                        await bot.send_video(
                            chat_id=update.message.chat.id,
                            video=download_directory,
                            #caption=description,
                            parse_mode="HTML",
                            duration=duration,
                            width=width,
                            height=height,
                            supports_streaming=True,
                            # reply_markup=reply_markup,
                            thumb=thumb_image_path,
                            reply_to_message_id=update.message.reply_to_message.message_id,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                Translation.UPLOAD_START,
                                update.message,
                                start_time
                            )
                        )
                        await bot.send_photo(
                            chat_id=update.message.chat.id,
                            photo=thumb_image_path,
                        )
                    else:
                        LOGGER.info("Did this happen? :\\")
                    end_two = datetime.now()
                    time_taken_for_upload = (end_two - end_one).seconds
                try:
                    shutil.rmtree(tmp_directory_for_each_user)
                    os.remove(thumb_image_path)
                    os.remove(save_ytdl_json_path)
                except:
                    pass
                await bot.edit_message_text(
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id,
                    disable_web_page_preview=True
                )
