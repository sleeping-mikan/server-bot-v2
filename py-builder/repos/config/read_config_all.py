#!ignore
from ..imports import *
from ..constant import *
from ..wait_for_keypress import *
from ..logger.logger_create import *
#!end-ignore

#configの読み込み
try:
    allow_cmd = set(config["discord_commands"]["cmd"]["serverin"]["allow_mccmd"])
    server_name = config["server_name"]
    server_args = config["server_args"].split(" ")
    if not os.path.exists(server_path + server_name):
        sys_logger.error("not exist " + server_path + server_name + " file. please check your config.")
        wait_for_keypress()
    allow = {"ip":config["allow"]["ip"],"replace":config["allow"]["replace"]}
    log = config["log"]
    now_dir = server_path.replace("\\","/").split("/")[-2]
    backup_path = config["discord_commands"]["backup"]["path"]
    lang = config["discord_commands"]["lang"]
    bot_admin = config["discord_commands"]["admin"]["members"]
    flask_secret_key = config["web"]["secret_key"]
    web_port = config["web"]["port"]
    STOP = config["discord_commands"]["stop"]["submit"]
    where_terminal = config["discord_commands"]["terminal"]["discord"]
    is_auto_update = config["update"]["auto"]
    update_branch = config["update"]["branch"]
    enable_advanced_features = config["enable_advanced_features"]
    sys_files = config["discord_commands"]["cmd"]["stdin"]["sys_files"]
    if config["discord_commands"]["terminal"]["capacity"] == "inf":
        terminal_capacity = float("inf")
    else:
        terminal_capacity = config["discord_commands"]["terminal"]["capacity"]
    
except KeyError:
    sys_logger.error("config file is broken. please delete .config and try again.")
    wait_for_keypress()

sys_logger.info("advanced features -> " + str(enable_advanced_features))