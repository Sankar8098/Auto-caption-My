import re
import os
import time

id_pattern = re.compile(r'^.\d+$') 

class Rkn_Bots(object):
    # Rkn client config
    API_ID = os.environ.get("API_ID", "23990433")
    API_HASH = os.environ.get("API_HASH", "e6c4b6ee1933711bc4da9d7d17e1eb20")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "6750957059:AAFvd3mez21vumWuV8jMaG3aOBW55_eGTKM")

    # start_pic
    RKN_PIC = os.environ.get("RKN_PIC", "https://telegra.ph/file/462b0bbd3623b54672f75.jpg")

    # web response configuration
    BOT_UPTIME = time.time()
    PORT = int(os.environ.get("PORT", "8080"))
    FORCE_SUB = os.environ.get("FORCE_SUB", "SK_MoviesOffl") 

    # database config
    DB_NAME = os.environ.get("DB_NAME", "AutoCaption_Bot")     
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://sankar:sankar@sankar.lldcdsx.mongodb.net/?retryWrites=true&w=majority")

    # caption
    DEF_CAP = os.environ.get(
        "DEF_CAP",
        "<b><a href='telegram.me/SK_MoviesOffl'>{file_caption}</a></b>"
    )

    # sticker Id
    STICKER_ID = os.environ.get("STICKER_ID", "CAACAgIAAxkBAAELFqBllhB70i13m-woXeIWDXU6BD2j7wAC9gcAAkb7rAR7xdjVOS5ziTQE")

    # admin id
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5821871362').split()]
