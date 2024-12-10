#!ignore
from ..imports import *
from ..constant import *
from ..logger.logger_create import *
#!end-ignore

# discord.py用のロガーを取得して設定
discord_logger = logging.getLogger('discord')
if log["all"]:
    file_handler = logging.FileHandler(now_path + "/logs/all " + time + ".log")
    file_handler.setFormatter(file_formatter)
    discord_logger.addHandler(file_handler)