
from fake_useragent import UserAgent
from config.jsondb import translation
from config.jsondb import update_jsondb

import aiohttp
import base64
import time
import os

from telethon.tl.functions.messages import GetHistoryRequest
from bs4 import BeautifulSoup


async def get_translated_word(word):
    try:
        return "".join(
            (translation[letter] for letter in word.lower()))

    except KeyError: return word


async def requestToGetallFormsWord(words: tuple | list) -> tuple[tuple]:
    ready_wrods, error_words = [], []
    async with aiohttp.ClientSession() as session:
        for word in words:
            response = await session.get(
                f"http://sklonenie-slova.ru/{await get_translated_word(word)}",
                headers={"user-agent": UserAgent().chrome})


            response = await response.text()
            beautifulSoup = BeautifulSoup(response, "html.parser")
            response_html = beautifulSoup.find_all("td")

            if response_html:
                for response_word in response_html:
                    response_word = response_word.get_text()
                    if (word[:3].lower() == response_word[:3].lower() and
                            response_word[-1] != "?"):

                        ready_wrods.append(response_word)
            else:
                error_words.append(word)

    _ready_words = []
    for word in ready_wrods:
        [
            _ready_words.append(_word)
            for _word in (word.lower(), word.title(), word.upper())
        ]

    return _ready_words, error_words



class MainFunctions:
    async def _message_analise(self, message):
        found_words_third_type: list[bool] = []
        found_words_second_type: list[bool] = []
        found_words_first_type: list[bool] = []

        for word in self.config_json.get("words-of-the-first-type"):
            if word in message:
                found_words_first_type.append(True)

        for word in self.config_json.get("words-of-the-second-type"):
            if word in message:
                found_words_second_type.append(True)

        for word in self.config_json.get("words-of-the-third-type"):
            if word in message:
                found_words_third_type.append(True)

        return (found_words_first_type,
                found_words_second_type, found_words_third_type)

    async def message_analise(self, message):
        if message:
            found_words_first_type, found_words_second_type,\
                found_words_third_type = await self._message_analise(message)

            if not found_words_third_type:
                if found_words_first_type and found_words_second_type:
                    return True


    async def startAnalysis(self, messageObject):
        for grouplink in self.config_json.get("groups"):
            group = await self.get_entity(grouplink)
            groupname = group.title

            await messageObject.answer(f"🤖Начинаю анализироовать группу {groupname}")
            messages_objects = await self(
                GetHistoryRequest(
                    peer=groupname, offset_id=0, offset_date=None,
                    add_offset=0, limit=500, max_id=0, min_id=0, hash=0
                )
            )
            for messages in messages_objects.messages:
                if (messages.from_id.user_id not in self.config_json["clients-ids"] and
                        await self.message_analise(messages.message)):

                    if not self.config_json[
                        "users-received-newsletter"].get(messages.from_id.user_id):

                        self.config_json["users-received-newsletter"][
                            messages.from_id.user_id] = []

        update_jsondb()
        await messageObject.answer("Операция завершена!")

    async def startMailing(self, messageObject):
        # print(time.time() - announcement.get("day"))
        for user_id, user_announcements in self.config_json[
            "users-received-newsletter"].items():

            user = await self.get_entity(int(user_id))
            announcements = await self.dynamicConversion(
                self.config_json["announcements"]
            )
            for announcement in announcements:
                if (announcement.get("day") <= time.time() and
                        announcement.get("announcement-name") not in user_announcements
                ):
                    self.config_json["users-received-newsletter"][
                        user_id].append(announcement.get("announcement-name"))

                    await self.send_file(int(user_id),
                                         file=announcement["images-paths"],
                                         caption=announcement["text"])


        update_jsondb()
        await self.removeimagefiles()
        await messageObject.answer("Операция завершена!")

    async def dynamicConversion(self, announcements):
        _announcements = []
        _file_count = 0

        for announcements_name, announcements_value in announcements.items():
            _imagespathnames = []
            for imagebase64 in announcements_value.get("photos"):
                _file_count += 1
                with open(f"photos/image_{_file_count}.jpg", "wb") as _imagefile:
                    _imagefile.write(base64.decodebytes(imagebase64.encode()))
                    _imagespathnames.append(f"photos/image_{_file_count}.jpg")

            _announcements.append(
                {
                    "announcement-name": announcements_name,
                    "images-paths": _imagespathnames,
                    "text": announcements_value.get("text"),
                    "day": announcements_value.get("day")
                }
            )

        return _announcements

    async def removeimagefiles(self):
        for image in os.listdir("photos"):
            if os.path.isfile("photos/" + image):
                try: os.remove("photos/" + image)
                except PermissionError: pass