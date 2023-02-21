
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import executor

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors.rpcerrorlist import FloodWaitError

import aiogram
import config
import base64
import time
import os

from buttons.keyboardbuttons import InlineKeyboardMarkupInstance
from buttons.keyboardbuttons import ReplyKeyboardMarkupInstnace

from main_functions import requestToGetallFormsWord
from main_functions import MainFunctions

from config.jsondb import config_json
from config.jsondb import update_jsondb
from config.docs import docs


class ConnectToTelegramClient(TelegramClient):

    def __init__(self, config_data):
        self.config_json = config_data
        self.client_config_data = config_data.get("client")
        self.bot_config_data = config_data.get("bot")
        self._bot_activation_key = self.bot_config_data.get("key")
        self.active_action = ""

        self.bot = Bot(self.bot_config_data.get("token"))
        self.bot_dispatcher = Dispatcher(self.bot)

        TelegramClient.__init__(self,
                                session=self.client_config_data.get("phone"),
                                api_id=self.client_config_data.get("api_id"),
                                api_hash=self.client_config_data.get("api_hash"))


    def __start(self):
        self.start()
        executor.start_polling(self.bot_dispatcher,
                               skip_updates=True)


class CheckerActivationKey:
    inline_keyboard_markup = InlineKeyboardMarkupInstance(
        {
            "add_1": {
                "button-text": "Акивировать бота",
                "callback": "bot-activation-mathod"
            }
        }
    )
    def __init__(self, tested_method):
        self.tested_method = tested_method

    async def __call__(self, *args, **kwargs):
        callbackQuare, *_ = args
        if (self.instance.config_json["bot"].get("set-key") and
                callbackQuare.from_user.id in self.instance.config_json["clients-ids"]):

            try: await self.tested_method(*args)
            except TypeError:
                await self.tested_method(self.instance, *args)

            update_jsondb()
        else:
            await args[0].answer(
                config.docs.bot_not_activated_t,
                reply_markup=self.inline_keyboard_markup)



class ClientRequestHandler(ConnectToTelegramClient, MainFunctions):
    control_buttons_markup = ReplyKeyboardMarkupInstnace(
        {
            "row_1": (
                config.docs.append_words_t,
                config.docs.remove_words_t, config.docs.show_words_t),

            "row_2": (
                config.docs.append_groups_t,
                config.docs.remove_groups_t, config.docs.show_groups_t),

            "row_3": (
                config.docs.append_announcement_t,
                config.docs.remove_announcement_t, config.docs.show_announcement_t
            ),

            "row_4": (
                config.docs.start_analysis_t,
                config.docs.start_mailing_t
            )
        }
    )
    word_options_buttons = InlineKeyboardMarkupInstance(
        {
            "add_1": {
                "button-text": "1",
                "callback": "word-option-1"
            },
            "add_2": {
                "button-text": "2",
                "callback": "word-option-2"
            },
            "add_3": {
                "button-text": "3",
                "callback": "word-option-3"
            }
        }
    )
    word_append_option = InlineKeyboardMarkupInstance(
        {
            "add_1": {
                "button-text": "Добавить все формы введенных слов",
                "callback": "all-word-forms"
            },
            "add_2": {
                "button-text": "Добавить слова в исходном виде",
                "callback": "original-word-form"
            }
        }
    )
    def __init__(self, client_config_data):
        optionConditionOne = lambda callback: callback.data == "word-option-1"
        optionConditionTwo = lambda callback: callback.data == "word-option-2"
        optionConditionThree = lambda callback: callback.data == "word-option-3"
        activationCondition = lambda callback: callback.data == "bot-activation-mathod"
        declinewordCondition = lambda callback: callback.data == "all-word-forms"
        originalwordCondition = lambda callback: callback.data == "original-word-form"

        self.wordonetype: list = []
        self.wordtwotype: list = []
        self.wordthreetype: list = []
        self.announcement_name = ""
        self.image_caption = None
        self.image_count = 0

        ConnectToTelegramClient.__init__(self, client_config_data)
        CheckerActivationKey.instance = self

        @self.bot_dispatcher.message_handler(commands=["start"])
        @CheckerActivationKey
        async def startCommandHandler(message: aiogram.types.Message):
            await message.answer(docs, reply_markup=self.control_buttons_markup)


        @self.bot_dispatcher.message_handler(commands=["help"])
        async def helpCommandHandler(message: aiogram.types.Message):
            await message.answer(
                docs, reply_markup=CheckerActivationKey.inline_keyboard_markup)


        @self.bot_dispatcher.callback_query_handler(activationCondition)
        async def activationCallbackHandler(
                callbackQuery: aiogram.types.CallbackQuery):

            if not self.config_json["bot"].get("set-key"):
                self.active_action = "active-action-set-key"
                await self.bot.send_message(
                    callbackQuery.from_user.id, "Введите ключь активации!")
            else:
                await self.bot.send_message(
                    callbackQuery.from_user.id, "Бот уже активирован!")

        @self.bot_dispatcher.callback_query_handler(optionConditionOne)
        async def wrodoptionone(callbackQuery: aiogram.types.CallbackQuery):
            self.active_action = "word-option-1"
            await self.bot.send_message(callbackQuery.from_user.id,
                                        config.docs.send_wrod_t)

        @self.bot_dispatcher.callback_query_handler(optionConditionTwo)
        async def wrodoptionone(callbackQuery: aiogram.types.CallbackQuery):
            self.active_action = "word-option-2"
            await self.bot.send_message(callbackQuery.from_user.id,
                                        config.docs.send_wrod_t)

        @self.bot_dispatcher.callback_query_handler(optionConditionThree)
        async def wrodoptionone(callbackQuery: aiogram.types.CallbackQuery):
            self.active_action = "word-option-3"
            await self.bot.send_message(callbackQuery.from_user.id,
                                        config.docs.send_wrod_t)

        @self.bot_dispatcher.callback_query_handler(declinewordCondition)
        @CheckerActivationKey
        async def appenddeclinewords(callbackQuery: aiogram.types.CallbackQuery):
            oneListWords = await requestToGetallFormsWord(self.wordonetype)
            twoListWords = await requestToGetallFormsWord(self.wordtwotype)
            threeListWords = await requestToGetallFormsWord(self.wordthreetype)

            wordinlist: bool = False

            for ready_words_list, jsondb_list_name in (
                (oneListWords[0], "words-of-the-first-type"),
                (twoListWords[0], "words-of-the-second-type"),
                (threeListWords[0], "words-of-the-third-type")):

                for word in ready_words_list:
                    if (word not in self.config_json["words-of-the-first-type"] and
                            word not in self.config_json["words-of-the-second-type"] and
                            word not in self.config_json["words-of-the-third-type"]):

                        self.config_json[jsondb_list_name].append(word)


            for words in oneListWords[1], twoListWords[1], threeListWords[1]:
                if words:
                    await self.bot.send_message(
                        callbackQuery.from_user.id,
                        f"Нам не удалось обработать слово(а) {', '.join(words)}")

            self.wordonetype, self.wordtwotype, self.wordthreetype = [], [], []
            await self.bot.send_message(callbackQuery.from_user.id,
                                        "Операция завершена!")

        @self.bot_dispatcher.callback_query_handler(originalwordCondition)
        @CheckerActivationKey
        async def appendoriginalwords(callbackQuery: aiogram.types.CallbackQuery):
            for ready_words_list, jsondb_list_name in (
                    (self.wordonetype, "words-of-the-first-type"),
                    (self.wordtwotype, "words-of-the-second-type"),
                    (self.wordthreetype, "words-of-the-third-type")):

                for word in ready_words_list:
                    if (word not in self.config_json["words-of-the-first-type"] and
                            word not in self.config_json["words-of-the-second-type"] and
                            word not in self.config_json["words-of-the-third-type"]):

                        self.config_json[jsondb_list_name].append(word)

            self.wordonetype, self.wordtwotype, self.wordthreetype = [], [], []
            await self.bot.send_message(callbackQuery.from_user.id,
                                        "Операция завершена!")

        @self.bot_dispatcher.message_handler(content_types=['photo'])
        async def iamageHandler(message: aiogram.types.Message):
            if self.active_action == "append-announcement":
                image = await self.bot.get_file(message.photo[-1].file_id)
                image_ext = image.file_path.split('.')[-1]
                self.image_count += 1
                await self.bot.download_file(
                    image.file_path, f"photos/photos/image_{self.image_count}.{image_ext}")

                if not self.image_caption:
                    self.image_caption = message.caption

        @self.bot_dispatcher.message_handler(content_types=['text'])
        async def messageHandler(message: aiogram.types.Message):
            if (message.text == "0" and
                    self.active_action == "append-announcement"):

                for image in os.listdir("photos/photos"):
                    with open(f"photos/photos/{image}", "rb") as image_file:
                        encod_image = base64.encodebytes(image_file.read()).decode()
                        if not self.config_json["announcements"].get(self.announcement_name):
                            self.config_json["announcements"][self.announcement_name] = {
                                "photos": [encod_image],
                                "text": self.image_caption
                            }
                        else:
                            self.config_json["announcements"][
                                self.announcement_name]["photos"].append(encod_image)


                for image in os.listdir("photos/photos"):
                    try: os.remove("photos/photos/" + image)
                    except PermissionError: pass

                await message.answer("Через сколько дней после анализа "
                                     "отпрасить рассылочное объявление?")


                self.active_action = "set-send-date"
                self.image_caption = 0
                update_jsondb()
                # await message.answer("Операция завершена!")

            else:
                await self.messagehandler(message)


    async def messagehandler(self, message: aiogram.types.Message):
        match self.active_action:
            case "active-action-set-key":
                if message.text == self.config_json["bot"]["key"]:
                    self.config_json["bot"]["set-key"] = True
                    self.config_json["clients-ids"].append(message.chat.id)
                    self.active_action = ""

                    update_jsondb()
                    await message.answer("Ключь активирован!",
                                         reply_markup=self.control_buttons_markup)

                else:
                    await message.answer("Неправильный ключь!")

            case "word-option-1" | "word-option-2" | "word-option-3":
                if self.adduserMessageTheList(message.text):
                    self.active_action = ""
                    await message.answer("Выберите нужный вариант!",
                                         reply_markup=self.word_append_option)

            case "remove-words":
                if message.text != "0":
                    ready_words, error_words = await requestToGetallFormsWord(
                        [word.split()[0] for word in message.text.split()])

                    def remove_words(ready_words):
                        for word in ready_words:
                            for words_list, jsondb_list_name in (
                                    (self.config_json["words-of-the-first-type"],
                                     "words-of-the-first-type"),

                                    (self.config_json["words-of-the-second-type"],
                                     "words-of-the-second-type"),

                                    (self.config_json["words-of-the-third-type"],
                                     "words-of-the-third-type")):

                                if word in words_list:
                                    self.config_json[jsondb_list_name].remove(word)

                    remove_words(ready_words)
                    if error_words:
                        remove_words(error_words)

                else:
                    self.active_action = ""
                    await message.answer("Операция завершена!")

            case "append-groups":
                if message.text != "0":
                    for groupLink in message.text.split():
                        groupLink = groupLink.split()[0]
                        try:
                            response = await self.get_entity(groupLink)
                            group_name = response.title

                            if (response.to_dict().get("_") == "Channel" or
                                    response.to_dict().get("_") == "Chat"):
                                if groupLink not in self.config_json["groups"]:
                                    self.config_json["groups"].append(groupLink)

                                else: await message.answer(
                                    f"Группа {groupLink} уже добавлена!")
                            else:
                                await message.answer(
                                    f"Ссылка {groupLink} не указывает на группу!")

                        except ValueError:
                            await message.answer(f"Произошла ошибка!\n"
                                                 f"Скорее всего ссылка {groupLink} некорректна!")
                else:
                    update_jsondb()
                    self.active_action = ""
                    await message.answer("Операция завершена!")

            case "remove-groups":
                if message.text != "0":
                    for groupLink in message.text.split():
                        groupLink = groupLink.split()[0]
                        if groupLink in self.config_json["groups"]:
                            self.config_json["groups"].remove(groupLink)
                else:
                    update_jsondb()
                    self.active_action = ""
                    await message.answer("Операция завершена!")

            case "set-announcement-name":
                if len(message.text.split()) == 1:
                    if message.text not in self.config_json.get("announcements"):
                        self.active_action = "append-announcement"
                        self.announcement_name = message.text
                        await message.answer("Отправьте сюда объявление в той форме "
                                             "в который хотите его рассылать!")
                    else:
                        await message.answer("Объявление с таким название уже добавлено!")
                else:
                    await message.answer("Введите название объявления без пробелов!")

            case "remove-announcements":
                if message.text != "0":
                    for announcement_name in message.text.split():
                        announcement_name = announcement_name.split()[0]
                        if announcement_name in self.config_json["announcements"]:
                            self.config_json["announcements"].pop(announcement_name)
                        else:
                            await message.answer(f"Объявление {announcement_name} нет в списках!")
                else:
                    update_jsondb()
                    self.active_action = ""
                    await message.answer("Операция завершена!")

            case "set-send-date":
                async def setdispatchtime(dispatch_time):
                    try:
                        current_second = time.time()
                        self.config_json["announcements"][
                            self.announcement_name]["day"] = current_second + dispatch_time

                        print(self.config_json["announcements"][self.announcement_name])
                        update_jsondb()
                        self.active_action = ""
                        await message.answer("Операция завершена!")

                    except KeyError:
                        self.active_action = ""
                        await message.answer("Произошла ошибка!")

                try:
                    print(message.text)
                    dispatch_time = int(message.text) * 43200
                    await setdispatchtime(dispatch_time)

                except ValueError:
                    try:
                        dispatch_time = float(message.text) * 43200
                        current_second = time.time()
                        await setdispatchtime(dispatch_time)

                    except ValueError:
                        await message.answer("Введите число без лишних символов!")

            case "":
                await self.messageTextHandler(message)

    @CheckerActivationKey
    async def messageTextHandler(self, message: aiogram.types.Message):
        match message.text:
            case config.docs.append_words_t:
                await message.answer(config.docs.word_doc,
                                     reply_markup=self.word_options_buttons)

            case config.docs.remove_words_t:
                self.active_action = "remove-words"
                await message.answer(config.docs.remove_word_doc)

            case config.docs.show_words_t:
                showword = ""
                for wordslists, wordstype in (
                        (self.config_json["words-of-the-first-type"], "Слова первого типа:"),
                        (self.config_json["words-of-the-second-type"], "Слова второго типа:"),
                        (self.config_json["words-of-the-third-type"], "Слова третьего типа:")):

                    if wordslists:
                        showword += (wordstype + "\n\n")
                        showword += ", ".join(wordslists)
                        showword += "\n\n"

                    else:
                        showword += (wordstype + "\n\n")
                        showword += "Пусто\n\n"

                await message.answer(showword)

            case config.docs.append_groups_t:
                self.active_action = "append-groups"
                await message.answer(config.docs.append_group_doc)

            case config.docs.remove_groups_t:
                self.active_action = "remove-groups"
                await message.answer(config.docs.remove_group_doc)

            case config.docs.show_groups_t:
                showgroup = "Добавленные группы:\n\n"
                if self.config_json["groups"]:
                    for groupLink in self.config_json["groups"]:
                        showgroup += "-----------------------------------------\n"
                        showgroup += groupLink
                        showgroup += "\n"
                        showgroup += "-----------------------------------------\n\n"

                else:
                    showgroup += "Пусто"

                await message.answer(showgroup)

            case config.docs.append_announcement_t:
                self.active_action = "set-announcement-name" # "append-announcement"
                await message.answer("Отправьте название объявления!")

            case config.docs.remove_announcement_t:
                self.active_action = "remove-announcements"
                await message.answer(config.docs.remove_announcement_doc)

            case config.docs.show_announcement_t:
                announcements = await self.dynamicConversion(
                                      self.config_json["announcements"])

                if announcements:
                    for announcement in announcements:
                        image_paths = announcement.get("images-paths")
                        caption = announcement.get("text")
                        await message.answer(
                            f"Название объявления: {announcement.get('announcement-name')}")

                        try:
                            while image_paths:
                                media_count = 0
                                media = aiogram.types.MediaGroup()
                                for image_path in image_paths[:-1]:
                                    media_count += 1
                                    if media_count < 10:
                                        media.attach_photo(aiogram.types.InputFile(image_path))
                                        image_paths.remove(image_path)

                                media.attach_photo(
                                    aiogram.types.InputFile(
                                        image_paths[-1]), caption=caption
                                )
                                image_paths.pop(-1); caption = None
                                try:
                                    await message.answer_media_group(media=media)

                                except aiogram.utils.exceptions.ValidationError:
                                    await message.answer("Медиа группа переполнена, "
                                                     "мы не можем отобразить все объявление!")

                        except IndexError: pass

                    await self.removeimagefiles()

                else:
                    await message.answer("Список объявлений пуст!")

            case config.docs.start_analysis_t:
                await self.startAnalysis(message)

            case config.docs.start_mailing_t:
                await self.startMailing(message)

    def adduserMessageTheList(self, message: str):
        if message != "0":
            for word in message.split():
                word = word.split()[0]
                if self.active_action == "word-option-1":
                    self.wordonetype.append(word)

                elif self.active_action == "word-option-2":
                    self.wordtwotype.append(word)

                elif self.active_action == "word-option-3":
                    self.wordtwotype.append(word)

        else:
            return True



if __name__ == '__main__':
    instance = ClientRequestHandler(config_json)
    instance._ConnectToTelegramClient__start()