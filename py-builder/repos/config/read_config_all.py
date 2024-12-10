#!ignore
from ..imports import *
from ..constant import *
from ..wait_for_keypress import *
from ..logger.logger_create import *
#!end-ignore

#configの読み込み
try:
    allow_cmd = set(config["allow_mccmd"])
    server_name = config["server_name"]
    if not os.path.exists(server_path + server_name):
        sys_logger.error("not exist " + server_path + server_name + " file. please check your config.")
        wait_for_keypress()
    allow = {"ip":config["allow"]["ip"]}
    log = config["log"]
    now_dir = server_path.replace("\\","/").split("/")[-2]
    backup_path = config["backup_path"]
    lang = config["lang"]
    bot_admin = set(config["force_admin"])
    flask_secret_key = config["web"]["secret_key"]
    web_port = config["web"]["port"]
    STOP = config["stop"]["submit"]
    where_terminal = config["terminal"]["discord"]
    if config["terminal"]["capacity"] == "inf":
        terminal_capacity = float("inf")
    else:
        terminal_capacity = config["terminal"]["capacity"]
except KeyError:
    sys_logger.error("config file is broken. please delete .config and try again.")
    wait_for_keypress()