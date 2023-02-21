from aiogram.types import KeyboardButton
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton



class InlineKeyboardMarkupInstance(InlineKeyboardMarkup):

    def __init__(self, buttons: dict):
        InlineKeyboardMarkup.__init__(self)

        for way_to_add, button_content in buttons.items():
            way_to_add = way_to_add.split("_")[0]

            if way_to_add == "add":
                self.add(
                    InlineKeyboardButton(
                        button_content.get("button-text"),
                        callback_data=button_content.get("callback")
                    )
                )


class ReplyKeyboardMarkupInstnace(ReplyKeyboardMarkup):

    def __init__(self, buttons): # rows=(), adds=()
        ReplyKeyboardMarkup.__init__(self)

        for way_to_add, button_names in buttons.items():
            way_to_add = way_to_add.split("_")[0]
            if way_to_add == "row":
                self.row(*(KeyboardButton(button_name)
                           for button_name in button_names))

            elif way_to_add == "add":
                self.add(*(KeyboardButton(button_name)
                           for button_name in button_names))

        # for row_button_names in rows:
        #     self.row(*(KeyboardButton(button_name)
        #                for button_name in row_button_names))
        #
        # for add_button_names in adds:
        #     print(add_button_names)


