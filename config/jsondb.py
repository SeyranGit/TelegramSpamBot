import json


try:
    with open("config/config.json", "r") as jsonfile:
        config_json = json.load(jsonfile)

except (FileNotFoundError, json.decoder.JSONDecodeError):
    config_json = {
        "client": {
            "api_id": "Your api_id(int)",
            "api_hash": "Your api_hash",
            "phone": "Your phone"
        },
        "bot": {
            "token": "Bot Token",
            "key": "dsak32fsdklf4903[fdsdfsgdsWEEf5834jlksdjaflds",
            "set-key": False,
        },
        "announcements": {},
        "words-of-the-first-type": [],
        "words-of-the-second-type": [],
        "words-of-the-third-type": [],
        "groups": [],
        "clients-ids": [],
        "users-received-newsletter": {}
    }
    with open("config/config.json", "w") as jsonfile:
        json.dump(config_json, jsonfile)


translation = {
    'Ь': '', 'ь': '',
    'Ъ': '', 'ъ': '',
    'А': 'A', 'а': 'a',
    'Б': 'B', 'б': 'b',
    'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g',
    'Д': 'D', 'д': 'd',
    'Е': 'E', 'е': 'e',
    'Ё': 'E', 'ё': 'e',
    'Ж': 'J', 'ж': 'j',
    'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i',
    'Й': 'Y', 'й': 'y',
    'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm',
    'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o',
    'П': 'P', 'п': 'p',
    'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't',
    'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f',
    'Х': 'H', 'х': 'h',
    'Ц': 'C', 'ц': 'c',
    'Ч': 'Ch', 'ч': 'ch',
    'Ш': 'Sh', 'ш': 'sh',
    'Щ': 'Shch', 'щ': 'shch',
    'Ы': 'Y', 'ы': 'y',
    'Э': 'E', 'э': 'e',
    'Ю': 'Iu', 'ю': 'iu',
    'Я': 'Ya', 'я': 'ya'
}


def update_jsondb():
    with open("config/config.json", "w") as jsonfile:
        json.dump(config_json, jsonfile)
