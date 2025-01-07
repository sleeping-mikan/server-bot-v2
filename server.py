

#--------------------

"""
各種必要なパッケージを呼び出す
"""
import discord 
from discord import app_commands 
from discord.ext import tasks
import waitress.server

from enum import Enum
from datetime import datetime, timedelta
from collections import deque
import subprocess
import threading
import asyncio
import platform
import os
from shutil import copystat,Error,copy2,copytree,rmtree,move as shutil_move
import sys
import logging
import requests
import aiohttp
import json
from copy import deepcopy
import importlib
import uuid

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response, flash
from ansi2html import Ansi2HTMLConverter
import waitress
import io
import zipfile
#--------------------


# 基本的な変数の読み込み

#--------------------

"""
処理に必要な定数を宣言する
"""

__version__ = "2.1.0"

repository = {
    "user": "sleeping-mikan",
    "name": "server-bot-v2",
    "branch": "main",#!debug else main
}


intents = discord.Intents.default() 
intents.message_content = True
client = discord.Client(intents=intents) 
tree = app_commands.CommandTree(client)

use_flask_server = True

#プロンプトを送る
print()

#サーバープロセス
process = None

#起動した時刻
time = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

#外部変数
token = None
temp_path = None 

#現在のディレクトリ
now_path = "/".join(__file__.replace("\\","/").split("/")[:-1])
# 相対パス
if now_path == "": now_path = "."
now_path = os.path.abspath(now_path)
#現在のファイル(server.py)
now_file = __file__.replace("\\","/").split("/")[-1]
WEB_TOKEN_FILE = '/mikanassets/web/usr/tokens.json'

#asyncioの制限を回避
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#/cmdに関する定数
cmd_logs = deque(maxlen=100)


status_lock = threading.Lock()
discord_terminal_item = deque()
discord_terminal_send_length = 0
discord_loop_is_run = False

# 濃い目の黄色
bot_color = discord.Color.from_rgb(255, 242, 145)
embed_under_line_url = "https://www.dropbox.com/scl/fi/70b9ckjwrfilds65gbs11/gradient_bar.png?rlkey=922kwpi4t17lk0ju4ztbq6ofc&st=nb9saec1&dl=1"



# 権限データ
COMMAND_PERMISSION = {
    "stop":1,
    "start":1,
    "exit":2,
    "cmd serverin":1,
    "cmd stdin mk":3,
    "cmd stdin rm":2,
    "cmd stdin mkdir":2,
    "cmd stdin rmdir":2,
    "cmd stdin ls":2,
    "cmd stdin mv":3,
    "cmd stdin send-discord":2,
    "cmd stdin wget":3,
    "help":0,
    "backup":1,
    "replace":4,
    "ip":0,
    "logs":1,
    "permission view":0,
    "permission change":4,
    "lang":2,
    "tokengen":1,
    "terminal":1,
    "update":3,
}

USER_PERMISSION_MAX = max(COMMAND_PERMISSION.values())

unti_GC_obj = deque()
#--------------------


#--------------------


#ログをdiscordにも返す可能性がある
is_back_discord = False
#--------------------


# エラー時の処理

#--------------------

def wait_for_keypress():
    print("please press any key to continue...")
    if platform.system() == "Windows":
        import msvcrt
        while True:
            if msvcrt.kbhit():
                msvcrt.getch()
                break
        exit()
    else:
        import sys
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            exit()
#--------------------


# ロガー作成前なので最小限

#--------------------

"""
configの読み込みと最小限の変数へのロードを行う
"""


config_file_place = now_path + "/" + ".config"

def make_config():
    if not os.path.exists(config_file_place):
        file = open(config_file_place,"w")
        server_path = now_path
        default_backup_path = server_path + "/../backup/" + server_path.replace("\\","/").split("/")[-1]
        if not os.path.exists(default_backup_path):
            os.makedirs(default_backup_path)
        default_backup_path = os.path.realpath(default_backup_path) + "/"
        print("default backup path: " + default_backup_path)
        config_dict = {\
                            "allow":{"ip":True,"replace":False},\
                            "auto_update":True,\
                            "server_path":now_path + "/",\
                            
                            "server_name":"bedrock_server.exe",\
                            "log":{"server":True,"all":False},\
                            
                            "mc":True,\
                            "web":{"secret_key":"YOURSECRETKEY","port":80},\
                            "discord_commands":{\
                                "cmd":{\
                                    "serverin":{\
                                        "allow_mccmd":["list","whitelist","tellraw","w","tell"]\
                                    }\
                                },\
                                "terminal":{"discord":False,"capacity":"inf"},\
                                "stop":{"submit":"stop"},\
                                "backup":{"path": default_backup_path,},\
                                "admin":{"members":{}},\
                                "lang":"en",\
                            },\
                        }
        json.dump(config_dict,file,indent=4)
        config_changed = True
    else:
        try:
            config_dict = json.load(open(now_path + "/"  + ".config","r"))
        except json.decoder.JSONDecodeError:
            print("config file is broken. please delete .config and try again.")
            wait_for_keypress()
        #要素がそろっているかのチェック
        def check(cfg):
            if "allow" not in cfg:
                cfg["allow"] = {"ip":True,"replace":False}
            if "ip" not in cfg["allow"]:
                cfg["allow"]["ip"] = True
            if "replace" not in cfg["allow"]:
                cfg["allow"]["replace"] = False

            if "auto_update" not in cfg:
                cfg["auto_update"] = True
            elif "ip" not in cfg["allow"]:
                cfg["allow"]["ip"] = True
            if "server_path" not in cfg:
                cfg["server_path"] = now_path + "/"
            if "discord_commands" not in cfg:
                cfg["discord_commands"] = {}
            if "cmd" not in cfg["discord_commands"]:
                cfg["discord_commands"]["cmd"] = {}
            if "serverin" not in cfg["discord_commands"]["cmd"]:
                cfg["discord_commands"]["cmd"]["serverin"] = {}
            if "allow_mccmd" not in cfg["discord_commands"]["cmd"]["serverin"]:
                cfg["discord_commands"]["cmd"]["serverin"]["allow_mccmd"] = ["list","whitelist","tellraw","w","tell"]
            if "terminal" not in cfg["discord_commands"]:
                cfg["discord_commands"]["terminal"] = {"discord":False,"capacity":"inf"}
            if "discord" not in cfg["discord_commands"]["terminal"]:
                cfg["discord_commands"]["terminal"]["discord"] = False
            if "capacity" not in cfg["discord_commands"]["terminal"]:
                cfg["discord_commands"]["terminal"]["capacity"] = "inf"
            if "stop" not in cfg["discord_commands"]:
                cfg["discord_commands"]["stop"] = {"submit":"stop"}
            elif "submit" not in cfg["discord_commands"]["stop"]:
                cfg["discord_commands"]["stop"]["submit"] = "stop"
            if "admin" not in cfg["discord_commands"]:
                cfg["discord_commands"]["admin"] = {"members":{}}
            elif "members" not in cfg["discord_commands"]["admin"]:
                cfg["discord_commands"]["admin"]["members"] = {}
            if "lang" not in cfg["discord_commands"]:
                cfg["discord_commands"]["lang"] = "en"
            if "mc" not in cfg:
                cfg["mc"] = True
            if "server_name" not in cfg:
                cfg["server_name"] = "bedrock_server.exe"
            if "log" not in cfg:
                cfg["log"] = {"server":True,"all":False}
            else:
                if "server" not in cfg["log"]:
                    cfg["log"]["server"] = True
                if "all" not in cfg["log"]:
                    cfg["log"]["all"] = False
            if "backup" not in cfg["discord_commands"]:
                try:
                    server_name = cfg["server_path"].replace("\\","/").split("/")[-2]
                except IndexError:
                    print(f"server_path is broken. please check config file and try again.\ninput : {cfg['server_path']}")
                    wait_for_keypress()
                if server_name == "":
                    print("server_path is broken. please check config file and try again.")
                    wait_for_keypress()
                cfg["discord_commands"]["backup"] = {}
                cfg["discord_commands"]["backup"]["path"] = cfg["server_path"] + "../backup/" + server_name
                cfg["discord_commands"]["backup"]["path"] = os.path.realpath(cfg["discord_commands"]["backup"]["path"]) + "/"
                if not os.path.exists(cfg["discord_commands"]["backup"]["path"]):
                    os.makedirs(cfg["discord_commands"]["backup"]["path"])
            if "mc" not in cfg:
                cfg["mc"] = True
            if "web" not in cfg:
                cfg["web"] = {"secret_key":"YOURSECRETKEY","port":80}
            if "port" not in cfg["web"]:
                cfg["web"]["port"] = 80
            if "secret_key" not in cfg["web"]:
                cfg["web"]["secret_key"] = "YOURSECRETKEY"
            # バージョン移行処理
            # v2.0.0までは、admin.membersがlistで管理されていた(当時の権限レベルは現在の1に該当する。)
            if type(cfg["discord_commands"]["admin"]["members"]) == list:
                users = {}
                for user in cfg["discord_commands"]["admin"]["members"]:
                    users[str(user)] = 1
                cfg["discord_commands"]["admin"]["members"] = users
                print("admin.members is list. format changed to dict.(this version isv2.1.0 or later)")
            return cfg
        checked_config = check(deepcopy(config_dict))
        if config_dict != checked_config:
            config_dict = checked_config
            file = open(now_path + "/"  + ".config","w")
            #ログ
            config_changed = True
            json.dump(config_dict,file,indent=4)
            file.close()
            print("config file is changed.")
        else: config_changed = False
    return config_dict,config_changed
def to_config_safe(config):
    #"force_admin"に重複があれば削除する
    save = False
    if save:
        file = open(config_file_place,"w")
        json.dump(config,file,indent=4)
        file.close()

config,config_changed = make_config()
#整合性チェック
to_config_safe(config)
#ロガー作成前なので最小限の読み込み
try:
    log = config["log"]
    server_path = config["server_path"]
    if not os.path.exists(server_path):
        print("not exist server_path dir")
        wait_for_keypress()
    #ログファイルの作成
    def make_logs_file():
        #./logsが存在しなければlogsを作成する
        if not os.path.exists(now_path + "/" + "logs"):
            os.makedirs(now_path + "/" + "logs")
        if not os.path.exists(server_path + "logs"):
            os.makedirs(server_path + "logs")
    make_logs_file()
except KeyError:
    print("(log or server_path) in config file is broken. please input true or false and try again.")
    wait_for_keypress()
#--------------------


# Colorクラスの定義

#--------------------


#--------------------------------------------------------------------------------------------ログ関連
class Color(Enum):
    BLACK          = '\033[30m'#(文字)黒
    RED            = '\033[31m'#(文字)赤
    GREEN          = '\033[32m'#(文字)緑
    YELLOW         = '\033[33m'#(文字)黄
    BLUE           = '\033[34m'#(文字)青
    MAGENTA        = '\033[35m'#(文字)マゼンタ
    CYAN           = '\033[36m'#(文字)シアン
    WHITE          = '\033[37m'#(文字)白
    COLOR_DEFAULT  = '\033[39m'#文字色をデフォルトに戻す
    BOLD           = '\033[1m'#太字
    UNDERLINE      = '\033[4m'#下線
    INVISIBLE      = '\033[08m'#不可視
    REVERCE        = '\033[07m'#文字色と背景色を反転
    BG_BLACK       = '\033[40m'#(背景)黒
    BG_RED         = '\033[41m'#(背景)赤
    BG_GREEN       = '\033[42m'#(背景)緑
    BG_YELLOW      = '\033[43m'#(背景)黄
    BG_BLUE        = '\033[44m'#(背景)青
    BG_MAGENTA     = '\033[45m'#(背景)マゼンタ
    BG_CYAN        = '\033[46m'#(背景)シアン
    BG_WHITE       = '\033[47m'#(背景)白
    BG_DEFAULT     = '\033[49m'#背景色をデフォルトに戻す
    RESET          = '\033[0m'#全てリセット
    def __add__(self, other):
        if isinstance(other, Color):
            return self.value + other.value
        elif isinstance(other, str):
            return self.value + other
        else:
            raise NotImplementedError
    def __radd__(self, other):
        if isinstance(other, Color):
            return other.value + self.value
        elif isinstance(other, str):
            return other + self.value
        else:
            raise NotImplementedError
#--------------------


# ログのフォーマットクラス作成

#--------------------

"""
loggerで用いるフォーマッタの定義
"""

class Formatter():
    levelname_size = 8
    name_size = 10
    class ColoredFormatter(logging.Formatter):
        # ANSI escape codes for colors
        COLORS = {
            'DEBUG': Color.BOLD + Color.WHITE,   # White
            'INFO': Color.BOLD + Color.BLUE,    # Blue
            'WARNING': Color.BOLD + Color.YELLOW, # Yellow
            'ERROR': Color.BOLD + Color.RED,   # Red
            'CRITICAL': Color.BOLD + Color.MAGENTA # Red background
        }
        RESET = '\033[0m'  # Reset color
        BOLD_BLACK = Color.BOLD + Color.BLACK  # Bold Black

        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            bold_black_asctime = f"{self.BOLD_BLACK}{record.asctime}{self.RESET}"
            
            # Adjust level name to be 8 characters long
            original_levelname = record.levelname
            padded_levelname = original_levelname.ljust(Formatter.levelname_size)
            original_name = record.name
            padded_name = original_name.ljust(Formatter.name_size)
            
            # Apply color to the level name only
            color = self.COLORS.get(original_levelname, self.RESET)
            colored_levelname = f"{color}{padded_levelname}{self.RESET}"
            
            # Get the formatted message
            message = record.getMessage()
            
            # Create the final formatted message
            formatted_message = f"{bold_black_asctime} {colored_levelname} {padded_name}: {message}"
            
            return formatted_message

    class MinecraftFormatter(logging.Formatter):
        
        # ANSI escape codes for colors
        COLORS = {
            'SERVER': Color.BOLD + Color.GREEN,   # Green
        }
        RESET = '\033[0m'  # Reset color
        BOLD_BLACK = Color.BOLD + Color.BLACK  # Bold Black

        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            bold_black_asctime = f"{self.BOLD_BLACK}{record.asctime}{self.RESET}"
            
            # Apply color to the level name only
            color = self.COLORS["SERVER"]
            colored_levelname = f"{color}SERVER  {self.RESET}"
            
            # Get the formatted message
            message = record.getMessage()
            # msg_type = message.split()
            # if len(msg_type) > 2:
            #     msg_type = msg_type[2][:-1]
            # if msg_type == "INFO":
            #     msg_color = Color.CYAN
            # elif msg_type == "ERROR":
            #     msg_color = Color.RED
            # else:
            #     msg_color = Color.RESET
            what_type = message.upper()
            if "INFO" in what_type:
                msg_color = Color.CYAN
            elif "ERROR" in what_type:
                msg_color = Color.RED
            elif "WARN" in what_type:
                msg_color = Color.YELLOW
            else:
                msg_color = Color.RESET

            message = msg_color + message + Color.RESET
            
            # Create the final formatted message
            formatted_message = f"{bold_black_asctime} {colored_levelname} {message}"
            
            return formatted_message
    class FlaskFormatter(logging.Formatter):
        COLORS = {
            'FLASK': Color.BOLD + Color.CYAN,   # Green
        }
        RESET = '\033[0m'  # Reset color
        BOLD_BLACK = Color.BOLD + Color.BLACK  # Bold Black

        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            bold_black_asctime = f"{self.BOLD_BLACK}{record.asctime}{self.RESET}"
            
            # Apply color to the level name only
            color = self.COLORS["FLASK"]
            colored_levelname = f"{color}FLASK   {self.RESET}"
            
            # Get the formatted message
            message = record.getMessage()

            message = message + Color.RESET
            
            # Create the final formatted message
            formatted_message = f"{bold_black_asctime} {colored_levelname} {message}"
            
            return formatted_message

    class DefaultConsoleFormatter(logging.Formatter):
        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            
            # Adjust level name to be 8 characters long
            original_levelname = record.levelname
            padded_levelname = original_levelname.ljust(Formatter.levelname_size)
            original_name = record.name
            padded_name = original_name.ljust(Formatter.name_size)
            
            
            # Get the formatted message
            message = record.getMessage()
            
            # Create the final formatted message
            formatted_message = f"{record.asctime} {padded_levelname} {padded_name}: {message}"
            
            return formatted_message
        
    class MinecraftConsoleFormatter(logging.Formatter):
        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            
            padded_levelname = "SERVER".ljust(Formatter.levelname_size)
            
            
            # Get the formatted message
            message = record.getMessage()
            
            # Create the final formatted message
            formatted_message = f"{record.asctime} {padded_levelname} {message}"
            
            return formatted_message
    class FlaskConsoleFormatter(logging.Formatter):
        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            
            padded_levelname = "FLASK".ljust(Formatter.levelname_size)
            
            
            # Get the formatted message
            message = record.getMessage()
            
            # Create the final formatted message
            formatted_message = f"{record.asctime} {padded_levelname} {message}"
            
            return formatted_message


#logger
dt_fmt = '%Y-%m-%d %H:%M:%S'
console_formatter = Formatter.ColoredFormatter(f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt)
file_formatter = Formatter.DefaultConsoleFormatter('%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt)

#--------------------


# ロガーの作成および設定

#--------------------

"""
ロガーの作成および設定を行う
"""

#/log用のログ保管場所
log_msg = deque(maxlen=19)
#discord送信用のログ
discord_log_msg = deque() 
def create_logger(name,console_formatter=console_formatter,file_formatter=file_formatter):
    class DequeHandler(logging.Handler):
        def __init__(self, deque):
            super().__init__()
            self.deque = deque

        def emit(self, record):
            log_entry = self.format(record)
            self.deque.append(log_entry)
    class DiscordHandler(logging.Handler):
        def __init__(self,deque):
            super().__init__()
            self.deque = deque
        def emit(self, record):
            log_entry = self.format(record)
            self.deque.append(log_entry)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(console_formatter)
    logger.addHandler(console)
    if log["all"]:
        f = time + ".log"
        file = logging.FileHandler(now_path + "/logs/all " + f,encoding="utf-8")
        file.setLevel(logging.DEBUG)
        file.setFormatter(file_formatter)
        logger.addHandler(file)
    deque_handler = DequeHandler(log_msg)
    deque_handler.setLevel(logging.DEBUG)
    deque_handler.setFormatter(console_formatter)  # フォーマットは任意で設定
    discord_handler = DiscordHandler(discord_log_msg)
    discord_handler.setLevel(logging.DEBUG)
    discord_handler.setFormatter(console_formatter)  # フォーマットは任意で設定
    logger.addHandler(deque_handler)
    logger.addHandler(discord_handler)
    return logger

#ロガーの作成
logger_name = ["stop", "start", "exit", "ready", "cmd", "help", "backup", "replace", "ip", "sys"]

stop_logger = create_logger("stop")
start_logger = create_logger("start")
exit_logger = create_logger("exit")
ready_logger = create_logger("ready")
cmd_logger = create_logger("cmd")
help_logger = create_logger("help")
backup_logger = create_logger("backup")
replace_logger = create_logger("replace")
ip_logger = create_logger("ip")
sys_logger = create_logger("sys")
log_logger = create_logger("log")
permission_logger = create_logger("permission")
admin_logger = create_logger("admin")
lang_logger = create_logger("lang")
token_logger = create_logger("token")
terminal_logger = create_logger("terminal")
base_extension_logger = create_logger("extension")
update_logger = create_logger("update")
minecraft_logger = create_logger("minecraft",Formatter.MinecraftFormatter(f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt),Formatter.MinecraftConsoleFormatter('%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt))

#--------------------


# 残りのconfig読み出し

#--------------------


#configの読み込み
try:
    allow_cmd = set(config["discord_commands"]["cmd"]["serverin"]["allow_mccmd"])
    server_name = config["server_name"]
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
    is_auto_update = config["auto_update"]
    if config["discord_commands"]["terminal"]["capacity"] == "inf":
        terminal_capacity = float("inf")
    else:
        terminal_capacity = config["discord_commands"]["terminal"]["capacity"]
except KeyError:
    sys_logger.error("config file is broken. please delete .config and try again.")
    wait_for_keypress()
#--------------------


# ファイルの作成/修正/アップデート

#--------------------


def get_self_commit_id():
    repos = f"{repository['user']}/{repository['name']}"
    branch = repository["branch"]
    url = "https://api.github.com/repos/" + repos + "/commits/" + branch

    response = requests.get(url)
    if response.status_code != 200:
        sys_logger.error("github api error. status code: " + str(response.status_code))
        return None
    commit_id = response.json()["sha"]
    return commit_id

args = sys.argv[1:]
do_init = False

#引数を処理する。
for i in args:
    arg = i.split("=")
    if arg[0] == "-init":
        do_init = True
        # pass

is_first_run = False

# mikanassets/extensionフォルダを作成
if not os.path.exists(now_path + "/mikanassets/extension"):
    # 最初の起動の場合にはフラグを立てておく
    is_first_run = True
    os.makedirs(now_path + "/mikanassets/extension")

#updateプログラムが存在しなければdropboxから./update.pyにコピーする
if not os.path.exists(now_path + "/mikanassets"):
    os.makedirs(now_path + "/mikanassets")
if not os.path.exists(now_path + "/mikanassets/" + "update.py") or do_init:
    url='https://www.dropbox.com/scl/fi/zo824cfk88uj52sospwo6/update_v2.2.py?rlkey=vwkh78smhdbm2pnfyegyxjpgf&st=6wdv9o5w&dl=1'
    filename= now_path + '/mikanassets/' + 'update.py'

    urlData = requests.get(url).content

    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)
def save_mikanassets_dat():
    if not os.path.exists(now_path + "/mikanassets"):
        os.makedirs(now_path + "/mikanassets")
    if not os.path.exists(os.path.join(now_path, "mikanassets", ".dat")):
        # 存在しなければデータファイルを作成する(現状 commit id 保管用)
        file = open(os.path.join(now_path, "mikanassets", ".dat"), "w")
        file.write('{"commit_id":' + f'"{get_self_commit_id()}"' + '}')
        file.close()
save_mikanassets_dat()
    #os.system("curl https://www.dropbox.com/scl/fi/w93o5sndwaiuie0otorm4/update.py?rlkey=gh3gqbt39iwg4afey11p99okp&st=2i9a9dzp&dl=1 -o ./update.py")
if not os.path.exists(now_path + "/mikanassets/web"):
    os.makedirs(now_path + "/mikanassets/web")
if not os.path.exists(now_path + "/mikanassets/web/index.html") or do_init:
    url='https://www.dropbox.com/scl/fi/04to7yrstmgdz9j09ljy2/index.html?rlkey=7q8eu0nooj8zy34dguwwsbkjd&st=4cb6y9sr&dl=1'
    filename= now_path + '/mikanassets/web/index.html'
    urlData = requests.get(url).content
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)
if not os.path.exists(now_path + "/mikanassets/web/login.html") or do_init:
    url='https://www.dropbox.com/scl/fi/6yuq2dhqozxeh8vxj8wgy/login.html?rlkey=9w9tbevra7r9vwjeofslb8j0x&st=sxtayji2&dl=1'
    filename= now_path + '/mikanassets/web/login.html'
    urlData = requests.get(url).content
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)
#mikanassets/web/usr/tokens.jsonを作成
if not os.path.exists(now_path + "/mikanassets/web/usr"):
    os.makedirs(now_path + "/mikanassets/web/usr")
if not os.path.exists(now_path + "/mikanassets/web/usr/tokens.json"):
    #ファイルを作成
    tokenfile_items = {"tokens":[]}
    file = open(now_path + "/mikanassets/web/usr/tokens.json","w",encoding="utf-8")
    file.write(json.dumps(tokenfile_items,indent=4))
    file.close()
    del tokenfile_items
if not os.path.exists(now_path + "/mikanassets/web/pictures"):
    os.makedirs(now_path + "/mikanassets/web/pictures")
if not os.path.exists(now_path + "/mikanassets/web/pictures/icon.png") or do_init:
    url = 'https://www.dropbox.com/scl/fi/cr6uejk7s2vk4zevm8zc6/boticon.png?rlkey=szuisf29w1rnynz9xs9ucr24l&st=a8kuy1fd&dl=1'
    filename= now_path + '/mikanassets/web/pictures/icon.png'
    urlData = requests.get(url).content
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)

def read_web_tokens():
    file = open(now_path + "/mikanassets/web/usr/tokens.json","r",encoding="utf-8")
    tokens = json.load(file)["tokens"]
    file.close()
    return tokens

web_tokens = read_web_tokens()

def make_token_file():
    global token
    #./.tokenが存在しなければ.tokenを作成する
    if not os.path.exists(now_path + "/" + ".token"):
        file = open(now_path + "/" + ".token","w",encoding="utf-8")
        file.write("ここにtokenを入力")
        file.close()
        sys_logger.error("please write token in" + now_path + "/" +".token")
        #ブロッキングする
        wait_for_keypress()
    #存在するならtokenを読み込む(json形式)
    else:
        token = open(now_path + "/" + ".token","r",encoding="utf-8").read()

def make_temp():
    global temp_path
    #tempファイルの作成場所
    if platform.system() == 'Windows':
        # %temp%/mcserver を作成
        temp_path = os.environ.get('TEMP') + "/mcserver"
    else:
        # /tmp/mcserver を作成
        temp_path = "/tmp/mcserver"

    #tempファイルの作成
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

async def update_self_if_commit_changed(interaction: discord.Interaction | None = None,embed: discord.Embed | None = None, text_pack: dict | None = None, sender = None):
    # ファイルが存在しなければ作る
    if not os.path.exists(os.path.join(now_path, "mikanassets", ".dat")):
        save_mikanassets_dat()
    file = open(os.path.join(now_path, "mikanassets", ".dat"))
    # 現在のserver.pyのコミットidを取り出す
    try:
        data = json.load(file)
        commit = data["commit_id"]
    except:
        if interaction is not None and embed is not None:
            embed.add_field(name="error", value="json load error (mikanassets/.dat). delete file.", inline=False)
            await sender(interaction=interaction,embed=embed)
        update_logger.error("json load error (mikanassets/.dat). delete file.")
    file.close()
    # github/mainのコミットidを取り出す
    github_commit = get_self_commit_id()
    update_logger.info("github commit -> " + github_commit)
    update_logger.info(" local commit -> " + commit)
    # 戻り値が正常でない場合
    if github_commit == None:
        if interaction is not None and embed is not None:
            embed.add_field(name="error", value="github response error.", inline=False)
            await sender(interaction=interaction,embed=embed)
        update_logger.error("github commit is None.")
    # コミットid出力
    if interaction is not None and embed is not None:
        embed.add_field(name="github commit", value=github_commit, inline=False)
        embed.add_field(name="local commit", value=commit, inline=False)
        await sender(interaction=interaction,embed=embed)
    # 更新がない場合
    if commit == github_commit: 
        if interaction is not None and embed is not None:
            embed.add_field(name="", value=text_pack["same"], inline=False)
            await sender(interaction=interaction,embed=embed)
        update_logger.info("commit is same. no update.")
        return
    # ファイルに新しいcommit id を書き込む
    data["commit_id"] = github_commit
    file = open(os.path.join(now_path, "mikanassets", ".dat"), "w")
    json.dump(data, file)
    file.close()
    # ローカルとgithubのコードが違ったことを出力
    if interaction is not None and embed is not None:
        embed.add_field(name="", value=text_pack["different"], inline=False)
        await sender(interaction=interaction,embed=embed)
    update_logger.info("commit changed. update self.")
    # コードを要求
    url='https://raw.githubusercontent.com/' + repository['user'] + '/' + repository['name'] + '/' + repository['branch'] + "/" + "server.py"
    # temp_path + "/new_source.py にダウンロード
    response = requests.get(url)
    if response.status_code != 200:
        sys_logger.error("response error. status_code : " + str(response.status_code))
        if interaction is not None and embed is not None:
            embed.add_field(name="error : raw.githubusercontent.com response error", value="", inline=False)
            await sender(interaction=interaction,embed=embed)
        return
    # temp_path + "/new_source.py に書き換え予定ファイル(新しいserver.py)を作成
    with open(temp_path + "/new_source.py", "w", encoding="utf-8") as f:
        f.write(response.content.decode('utf-8').replace("\r\n","\n"))
    # discordにコードを置き換える
    msg_id = str(0)
    channel_id = str(0)
    if interaction is not None and embed is not None:
        msg_id = str((await interaction.original_response()).id)
        channel_id = str(interaction.channel_id)
        embed.add_field(name="", value=text_pack["replace"].format(channel_id,msg_id), inline=False)
        await sender(interaction=interaction,embed=embed)
    replace_logger.info("call update.py")
    replace_logger.info('replace args : ' + msg_id + " " + channel_id)
    os.execv(sys.executable,["python3",now_path + "/mikanassets/" + "update.py",temp_path + "/new_source.py",msg_id,channel_id,now_file])



make_token_file()
make_temp()
if is_auto_update:
    asyncio.run(update_self_if_commit_changed())
#--------------------


# mcサーバー用properties読み込み

#--------------------



#java properties の読み込み
def properties_to_dict(filename):
    properties = {}
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith(' ') or line.startswith('\t'):
                        line = line[1:]
                    key, value = line.split('=', 1)
                    properties[key] = value
        return properties
    except Exception as e:#ファイルが存在しなければ存在しないことを出力して終了
        sys_logger.error(e)
        sys_logger.info("not exist server.properties file in " + server_path + ". if you are not using a minecraft server, please set mc to false in .config .if not, restart it and server.properties should be generated in the server hierarchy.")
        return {}

#minecraftサーバーであればpropertiesを読み込む
if config["mc"]:
    properties = properties_to_dict(server_path + "server.properties")
    sys_logger.info("read properties file -> " + server_path + "server.properties")

#コマンド利用ログ
use_stop = False
#--------------------


# テキスト関連データの作成

#--------------------



async def get_text_dat():
    global HELP_MSG, COMMAND_DESCRIPTION, send_help, RESPONSE_MSG, ACTIVITY_NAME 
# テキストデータ領域-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#help
    HELP_MSG = {
        "ja":{
            "/stop             ":"サーバーを停止します。但し起動していない場合にはエラーメッセージを返します。",
            "/start            ":"サーバーを起動します。但し起動している場合にはエラーメッセージを返します。",
            "/exit             ":"botを終了します。サーバーを停止してから実行してください。終了していない場合にはエラーメッセージを返します。\nまたこのコマンドを実行した場合次にbotが起動するまですべてのコマンドが無効になります。",
            "/cmd serverin     ":f"/cmd <mcコマンド> を用いてサーバーコンソール上でコマンドを実行できます。使用できるコマンドは{allow_cmd}です。",
            "/cmd stdin        ":"/cmd stdin <ls|rm|mk|rmdir|mkdir>を用いて、ファイル確認/削除/作成/フォルダ作成/フォルダ削除を実行できます。例えばサーバーディレクトリ直下にa.txtを作成する場合は/cmd stdin mk a.txtと入力します。",
            "/backup           ":"/backup [ワールド名] でワールドデータをバックアップします。ワールド名を省略した場合worldsをコピーします。サーバーを停止した状態で実行してください",
            "/replace          ":"/replace <py file> によってbotのコードを置き換えます。",
            "/ip               ":"サーバーのIPアドレスを表示します。",
            "/logs             ":"サーバーのログを表示します。引数を与えた場合にはそのファイルを、与えられなければ動作中に得られたログから最新の10件を返します。",
            "/permission change":"/permission change <level> <user> で、userのbot操作権利を変更できます。必要な権限レベルは/permission viewで確認できます。",
            "/permission view  ":"/permission view <user> で、userのbot操作権利を表示します。",
            "/lang             ":"/lang <lang> で、botの言語を変更します。",
            "/tokengen         ":"/tokengen で、webでログインするためのトークンを生成します。",
            "/terminal         ":"/terminal で、サーバーのコンソールを実行したチャンネルに紐づけます。",
        },
        "en":{
            "/stop             ":"Stop the server. If the server is not running, an error message will be returned.",
            "/start            ":"Start the server. If the server is running, an error message will be returned.",
            "/exit             ":"Exit the bot. Stop the server first and then run the command. If the server is not running, an error message will be returned.\n",
            "/cmd serverin     ":f"/cmd <mc command> can be used to execute commands in the server console. The available commands are {allow_cmd}.",
            "/cmd stdin        ":"/cmd stdin <ls|rm|mk|rmdir|mkdir> can be used to check/erase/creat/create a folder. For example, if you want to create a file a.txt in the server directory, enter /cmd stdin mk a.txt.",
            "/backup           ":"/backup [world name] copies the world data. If no world name is given, the worlds will be copied.",
            "/replace          ":"/replace <py file> replaces the bot's code.",
            "/ip               ":"The server's IP address will be displayed to discord.",
            "/logs             ":"Display the server's logs. If an argument is given, that file will be returned. If no argument is given, the latest 10 logs will be returned.",
            "/permission change":"/permission change <level> <user> changes the user's bot operation rights. The required permission level can be checked by /permission view.",
            "/permission view  ":"/permission view <user> displays the user's bot operation rights.",
            "/lang             ":"/lang <lang> changes the bot's language.",
            "/tokengen         ":"/tokengen generates a token for login to the web.",
            "/terminal         ":"/terminal connects the server's console to a channel.",
        },
    }
        

    COMMAND_DESCRIPTION = {
        "ja":{
            "stop":"サーバーを停止します。",
            "start":"サーバーを起動します。",
            "exit":"botを終了します。",
            "cmd":{
                "serverin":"サーバーにマインクラフトコマンドを送信します。",
                "stdin": {
                    "main": "サーバーディレクトリ以下に対するコマンドをサーバーの外側から実行します。",
                    "mk": "指定した相対パスを渡されたファイルまたは空にします。",
                    "rm": "指定した相対パスに完全一致するファイルを削除します。",
                    "ls": "指定したサーバーからの相対パスに存在するファイルを表示します。",
                    "mkdir": "指定した相対パスに新しいディレクトリを作成します。",
                    "rmdir": "指定した相対パスのディレクトリを再帰的に削除します。",
                    "mv": "指定したパスにあるファイルを別のパスに移動します。",
                    "send-discord": "discordにファイルを送信します。",
                    "wget": "urlからファイルをダウンロードします。",
                },
            },
            "backup":"ワールドデータをバックアップします。引数にはワールドファイルの名前を指定します。入力しない場合worldsが選択されます。",
            "replace":"<非推奨> このbotのコードを<py file>に置き換えます。このコマンドはbotを破壊する可能性があります。",
            "ip":"サーバーのIPアドレスを表示します。",
            "logs":"サーバーのログを表示します。引数にはファイル名を指定します。入力しない場合は最新の10件のログを返します。",
            "help":"このbotのコマンド一覧を表示します。",
            "permission":{
                "change":"選択したユーザに対してbotをdiscord管理者と同等の権限で操作できるようにします。",
                "view":"選択したユーザに対してbot操作権限を表示します。",
            },
            "lang":"botの言語を変更します。引数には言語コードを指定します。",
            "tokengen":"webにログインするためのトークンを生成します。",
            "terminal":"サーバーのコンソールを実行したチャンネルに紐づけます。",
            "update":"botを更新します。非推奨となった/replaceの後継コマンドです。",
        },
        "en":{
            "stop":"Stop the server.",
            "start":"Start the server.",
            "exit":"Exit the bot.",
            "cmd":{
                "serverin":"Send a Minecraft command to the server.",
                "stdin":{
                    "main":"Execute the command in the server's directory outside the server.",
                    "mk":"Set the file specified by the relative path from the server.",
                    "rm":"Delete the file specified by the relative path from the server.",
                    "ls":"Display the file specified by the relative path from the server.",
                    "mkdir":"Create a new directory specified by the relative path from the server.",
                    "rmdir":"Recursively delete the directory specified by the relative path from the server.",
                    "mv":"Move the file specified by the path to another path.",
                    "send-discord":"Send a file to discord.",
                    "wget":"Download a file from a url.",
                },
            },
            "backup":"Copy the world data. If no argument is given, the worlds will be copied.",
            "replace":"<Not recommended> Replace the bot's code with <py file>.",
            "ip":"The server's IP address will be displayed to discord.",
            "logs":"Display server logs. With an argument, return that file. Without, return the latest 10 logs.",
            "help":"Display this bot's command list.",
            "permission":{
                "view": "Display the bot operation rights of the selected user.",
                "change":"Force the selected user to have the same permissions as the bot, as discord administrator.",
            },
            "lang":"Change the bot's language. With an argument, specify the language code.",
            "tokengen":"Generate a token for login to the web.",
            "terminal":"Connect the server's console to a channel.",
            "update":"Update the bot. This is a successor command of /replace.",
        },
    }

    #今後も大きくなることが予想されるので、ここで条件分岐する
    if lang == "ja":
        send_help = "詳細なHelpはこちらを参照してください\n<https://github.com/sleeping-mikan/server-bot-v2/blob/main/README.md>\n"
        RESPONSE_MSG = {
            "other":{
                "no_permission":"管理者権限を持っていないため実行できません",
                "is_running":"サーバーが起動しているため実行できません",
                "is_not_running":"サーバーが起動していないため実行できません",
            },
            "stop":{
                "success":"サーバーを停止します",
            },
            "start":{
                "success":"サーバーを起動します",
            },
            "cmd":{
                "serverin":{
                    "skipped_cmd":"コマンドが存在しない、または許可されないコマンドです",
                },
                "stdin":{
                    "invalid_path": "パス`{}`は不正/操作不可能な領域です",
                    "not_file": "`{}`はファイルではありません",
                    "permission_denied":"`{}`を操作する権限がありません",
                    "file_size_limit":"サイズ`{}`は制限`{}`を超えている可能性があるためFile.ioにアップロードします\nアップロード後に再度メンションで通知します",
                    "file_size_limit_web":"サイズ`{}`は制限`{}`を超えているのでアップロードできません",
                    "mk":{
                        "success":"ファイル`{}`を作成または上書きしました",
                        "is_link":"`{}`はシンボリックリンクであるため書き込めません",
                    },
                    "rm":{
                        "success":"`{}`を削除しました",
                        "file_not_found":"`{}`は見つかりません",
                    },
                    "ls":{
                        "not_directory":"`{}`はディレクトリではありません",
                        "file_not_found":"`{}`は見つかりません",
                        "success":"`{}`\n```ansi\n{}```\n",
                        "to_long": "内容が2000文字を超えたためファイルに変換します。",
                    },
                    "mkdir":{
                        "success":"ディレクトリ`{}`を作成しました",
                        "exists":"`{}`は既に存在します",
                    },
                    "rmdir":{
                        "success":"ディレクトリ`{}`を削除しました",
                        "not_directory":"`{}`はディレクトリではありません",
                        "not_exists":"`{}`は見つかりません",
                    },
                    "mv":{
                        "success":"`{}`を`{}`に移動しました",
                        "not_exists":"`{}`は見つかりません",
                    },
                    "send-discord":{
                        "success":"<@{}> {} にファイルを送信しました",
                        "file_io_error":"<@{}> File.ioへのアップロードに失敗しました status -> `{}` , reason -> `{}` :: `{}`",
                        "file_not_found":"`{}`は見つかりません",
                        "not_file":"`{}`はファイルではありません",
                        "is_zip":"`{}`はディレクトリであるためzipで圧縮します",
                        "is_file":"`{}`はファイルであるため送信します",
                        "timeout":"<@{}> {} 秒を超えたため、送信を中断しました",
                        "raise_error":"<@{}> 送信中にエラーが発生しました\n```ansi\n{}```",
                    },
                    "wget":{
                        "download_failed":"`{}`からファイルをダウンロードできません",
                        "download_success":"`{}`からファイルを{}にダウンロードしました",
                        "already_exists":"`{}`は既に存在します",
                    },
                }
            },
            "backup":{
                "now_backup":"バックアップ中・・・",
                "data_not_found":"データが見つかりません",
                "success":"バックアップが完了しました！",
                "path_not_allowed":"不正なパス",
            },
            "replace":{
                "not_allow":{"name":"このコマンドはconfigにより実行を拒否されました","value":"/replaceは現在のバージョンでは非推奨です\nautoupdate機能による起動時自動更新と/updateによる更新を使用してください"},
                "progress":"更新プログラムの適応中・・・",
            },
            "ip":{
                "not_allow":"このコマンドはconfigにより実行を拒否されました",
                "get_ip_failed":"IPアドレスを取得できません",
                "msg_startwith":"サーバーIP : "
            },
            "logs":{
                "cant_access_other_dir":"他のディレクトリにアクセスすることはできません。この操作はログに記録されます。",
                "not_found":"指定されたファイルが見つかりません。この操作はログに記録されます。",
            },
            "exit":{
                "success":"botを終了します...",
            },
            "error":{
                "error_base":"エラーが発生しました。\n",
            },
            "permission":{
                "success":"{} の権限 : \ndiscord管理者権限 : {}\nbot管理者権限 : {}",
                "change":{
                    "already_added":"このユーザーはすでにbotの管理者権限を持っています",
                    "add_success":"`{}`にbotの管理者権限を与えました",
                    "remove_success":"`{}`からbotの管理者権限を剥奪しました",
                    "already_removed":"このユーザーはbotの管理者権限を持っていません",
                    "invalid_level":"権限レベルには削除(0)または1-{}の整数を指定してください。(指定された値 : `{}`)",
                },
            },
            "lang":{
                "success":"言語を{}に変更しました",
            },
            "tokengen":{
                "success":"生成したトークン(30日間有効) : {}",
            },
            "terminal":{
                "success":"サーバーのコンソールを{}に紐づけました",
            },
            "update":{
                "same":"存在するファイルは既に最新です",
                "different":"コミットidが異なるため更新を行います",
                "download_failed":"更新のダウンロードに失敗しました",
                "replace":"ch_id {}\nmsg_id {}",
            }
        }
        ACTIVITY_NAME = {
            "starting":"さーばーきどう",
            "running":"さーばーじっこう",
            "ending":"さーばーおしまい",
            "ended":"さーばーとじてる",
        }
    elif lang == "en":
        send_help = "Details on the help can be found here\n<https://github.com/sleeping-mikan/server-bot-v2/blob/main/README.md>\n"
        RESPONSE_MSG = {
            "other":{
                "no_permission":"Permission denied",
                "is_running":"Server is still running",
                "is_not_running":"Server is not running",
            },
            "stop":{
                "success":"The server has been stopped",
            },
            "start":{
                "success":"The server has been started",
            },
            "cmd":{
                "serverin":{
                    "skipped_cmd":"The command is not found or not allowed",
                },
                "stdin":{
                    "invalid_path": "`{}` is an invalid/operable area",
                    "not_file": "`{}` is not a file",
                    "permission_denied": "`{}` cannot be modified because it is an important file",
                    "file_size_limit": "Upload to File.io because the file size of `{}` is over the limit of {} bytes\nmention to you if ended",
                    "file_size_limit_web" : "Cannot upload to File.io because the file size of `{}` is over the limit of {} bytes",
                    "mk":{
                        "success":"`{}` has been created or overwritten",
                        "is_link": "`{}` is a symbolic link and cannot be written",
                    },
                    "rm":{
                        "success":"`{}` has been deleted",
                        "file_not_found":"`{}` not found",
                    },
                    "ls":{
                        "not_directory":"`{}` is not a directory",
                        "file_not_found":"`{}` not found",
                        "success":"`{}`\n```ansi\n{}```\n",
                        "to_long": "The content is over 2000 characters and will be converted to a file.",
                    },
                    "mkdir":{
                        "success":"Directory `{}` has been created",
                        "exists":"`{}` already exists",
                    },
                    "rmdir":{
                        "success":"Directory `{}` has been deleted",
                        "not_directory":"`{}` is not a directory",
                        "not_exists":"`{}` not found",
                    },
                    "mv":{
                        "success":"`{}` has been moved to `{}`",
                        "file_not_found":"`{}` not found",
                    },
                    "send-discord":{
                        "success":"<@{}> Sent to {} a file",
                        "file_io_error":"<@{}> File.io upload failed status -> `{}` , reason -> `{}` :: `{}`",
                        "not_file":"`{}` is not a file",
                        "file_not_found":"`{}` not found",
                        "is_zip":"`{}` is a directory, so it will be compressed and sent to discord",
                        "is_file":"`{}` is a file, so it will be sent to discord",
                    },
                    "wget":{
                        "download_failed":"Download failed url:{}",
                        "download_success":"Download complete url:{} path:{}",
                        "already_exists":"`{}` already exists",
                    }
                }
            },
            "backup":{
                "now_backup":"Backup in progress",
                "data_not_found":"Data not found",
                "success":"Backup complete!",
                "path_not_allowed":"Path not allowed",
            },
            "replace":{
                "not_allow":{"name":"This command is denied by config","value":"/replace is not recommended in now version. Please use auto update in config and /update"},
                "progress":"Applying update program",
            },
            "ip":{
                "not_allow":"This command is denied by config",
                "get_ip_failed":"Failed to get IP address",
                "msg_startwith":"Server IP : "
            },
            "logs":{
                "cant_access_other_dir":"Cannot access other directory. This operation will be logged.",
                "not_found":"The specified file was not found. This operation will be logged.",
            },
            "exit":{
                "success":"The bot is exiting...",
            },
            "error":{
                "error_base":"An error has occurred.\n",
            },
            "permission":{
                "success":"{}'s permission : \ndiscord administrator permission : {}\nbot administrator permission : {}",
                "change":{
                    "already_added":"The user has already been added as an administrator",
                    "add_success":"Added as an administrator to {}",
                    "already_removed":"The user has already been removed as an administrator",
                    "remove_success":"Removed as an administrator from {}",
                    "invalid_level":"Please specify an integer between 0 and {} for the permission level. (specified value : `{}`)",
                },
            },
            "lang":{
                "success":"Language changed to {}",
            },
            "tokengen":{
                "success":"Generated token (valid for 30 days) : {}",
            },
            "terminal":{
                "success":"The terminal has been set to {}",
            },
            "update":{
                "same":"The same version is already installed",
                "different":"The commit id is different to update",
                "download_failed":"Download failed",
                "replace":"ch_id {}\nmsg_id {}",
            },
        }
        ACTIVITY_NAME = {
            "starting":"Server go!",
            "running":"Server whoosh!",
            "ending":"Server stopping!",
            "ended":"Server stop!",
        }
    def make_send_help():
        global send_help
        send_help += f"web : http://{requests.get('https://api.ipify.org').text}:{web_port}\n" 
        embed = discord.Embed(title="How to use this bot",color=bot_color)
        for key in HELP_MSG[lang]:
            embed.add_field(name=key,value=HELP_MSG[lang][key],inline=False)
        embed.add_field(name="detail",value=send_help,inline=False)
        embed.set_image(url = embed_under_line_url)
        send_help = embed
    make_send_help()


get_text = asyncio.run(get_text_dat())
sys_logger.info('create text data')

#--------------------


# util関数のロード

#--------------------


async def not_enough_permission(interaction: discord.Interaction,logger: logging.Logger) -> bool:
    logger.error('permission denied')
    embed = discord.Embed(title=RESPONSE_MSG["other"]["no_permission"], color=0xff0000)
    embed.set_image(url = embed_under_line_url)
    await interaction.response.send_message(embed = embed,ephemeral = True)


async def is_administrator(user: discord.User) -> bool:
    if not user.guild_permissions.administrator:
        return False
    return True

async def is_force_administrator(user: discord.User) -> bool:
    #user idがforce_adminに含まれないなら
    if user.id not in config["discord_commands"]["admin"]["members"]:
        return False
    return True

#既にサーバが起動しているか
def is_running_server(logger: logging.Logger) -> bool:
    global process
    if process is not None:
        logger.error('server is still running')
        return True
    return False

#サーバーが閉まっている状態か
def is_stopped_server(logger: logging.Logger) -> bool:
    global process
    if process is None:
        logger.error('server is not running')
        return True
    return False

async def reload_config():
    import json
    with open(config_file_place, 'r') as f:
        global config
        config = json.load(f)
        #TODO
    

async def rewrite_config(config: dict) -> bool:
    try:
        with open(config_file_place, 'w') as f:
            import json
            json.dump(config, f,indent=4)
        return True
    except:
        return False


async def dircp_discord(src, dst, interaction: discord.Interaction, embed: discord.Embed, symlinks=False) -> None:
    global exist_files, copyed_files
    """
    src : コピー元dir
    dst : コピー先dir
    symlinks : リンクをコピーするか
    """
    #表示サイズ
    bar_width = 30
    #送信制限
    max_send = 20
    dst += datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    exist_files = 0
    for root, dirs, files in os.walk(top=src, topdown=False):
        exist_files += len(files)
    #何ファイルおきにdiscordへ送信するか(最大100回送信するようにする)
    send_sens = int(exist_files / max_send) if exist_files > max_send else 1
    copyed_files = 0
    async def copytree(src, dst, symlinks=False):
        global copyed_files
        names = os.listdir(src)
        os.makedirs(dst)
        errors = []
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    await copytree(srcname, dstname, symlinks)
                else:
                    copy2(srcname, dstname)
                    copyed_files += 1
                    if copyed_files % send_sens == 0 or copyed_files == exist_files:
                        now = RESPONSE_MSG["backup"]["now_backup"]
                        if copyed_files == exist_files:
                            now = RESPONSE_MSG["backup"]["success"]
                        embed.clear_fields()
                        embed.add_field(name = f"{now}",value=f"```{int((copyed_files / exist_files * bar_width) - 1) * '='}☆{((bar_width) - int(copyed_files / exist_files * bar_width)) * '-'}  ({'{: 5}'.format(copyed_files)} / {'{: 5}'.format(exist_files)}) {'{: 3.3f}'.format(copyed_files / exist_files * 100)}%```", inline = False)
                        await interaction.edit_original_response(embed=embed)
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error as err:
                errors.extend(err.args[0])
        try:
            copystat(src, dst)
        except OSError as why:
            # can't copy file access times on Windows
            if why.winerror is None:
                errors.extend((src, dst, str(why)))
        if errors:
            raise Error(errors)
    await copytree(src, dst, symlinks)
    
#logger thread
def server_logger(proc:subprocess.Popen,ret):
    global process,is_back_discord , use_stop
    if log["server"]:
        file = open(file = server_path + "logs/server " + datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + ".log",mode = "w")
    while True:
        try:
            logs = proc.stdout.readline()
        except Exception as e:
            sys_logger.error(e)
            continue
        # プロセスが終了している
        if logs == '': 
            if proc.poll() is not None:
                break
            continue
        #ログが\nのみであれば不要
        if logs == "\n":
            continue
        #後ろが\nなら削除
        logs = logs.rstrip("\n")
        minecraft_logger.info(logs)
        if log["server"]:
            file.write(logs + "\n")
            file.flush()
        if is_back_discord:
            cmd_logs.append(logs)
            is_back_discord = False
    #サーバーが終了したことをログに残す
    sys_logger.info('server is ended')
    #もし、stop命令が見当たらないなら、エラー出力をしておく
    if not use_stop:
        sys_logger.error('stop command is not found')
        use_stop = True
    #プロセスを終了させる
    process = None

async def print_user(logger: logging.Logger,user: discord.user):
    logger.info('command used by ' + str(user))

class ServerBootException(Exception):pass

async def user_permission(user:discord.User):
    # ユーザが管理者なら
    if await is_administrator(user):
        return USER_PERMISSION_MAX
    # configに権限が書かれていないなら
    if str(user.id) not in config["discord_commands"]["admin"]["members"]:
        return 0
    return config["discord_commands"]["admin"]["members"][str(user.id)]

# 操作可能なパスかを確認
def is_path_within_scope(path):
    # 絶対パスを取得
    path = os.path.abspath(path)
    # server_path 以下にあるか確認
    if path.startswith(os.path.abspath(server_path)):
        return True
    sys_logger.info("invalid path -> " + path + f"(server_path : {server_path})")
    return False

async def create_zip_async(file_path: str) -> tuple[io.BytesIO, int]:
    """ディレクトリをZIP化し、非同期的に返す関数"""
    loop = asyncio.get_event_loop()
    zip_buffer = io.BytesIO()

    def zip_task():
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_STORED) as zipf:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    full_file_path = os.path.join(root, file)
                    zipf.write(full_file_path, os.path.relpath(full_file_path, file_path))
        zip_buffer.seek(0)
        return zip_buffer

    # 非同期スレッドでZIP作成を実行
    zip_buffer = await loop.run_in_executor(None, zip_task)
    file_size = zip_buffer.getbuffer().nbytes
    return zip_buffer, file_size

async def send_discord_message_or_followup(interaction: discord.Interaction, message: str = discord.utils.MISSING, file = discord.utils.MISSING):
    if interaction.response.is_done():
        await interaction.followup.send(message, file=file)
    else:
        await interaction.response.send_message(message, file=file)

async def send_discord_message_or_edit(interaction: discord.Interaction, message: str = discord.utils.MISSING, file = discord.utils.MISSING, embed = discord.utils.MISSING, ephemeral = False):
    if interaction.response.is_done():
        await interaction.edit_original_response(content=message, embed=embed, attachments=[file] if file is not discord.utils.MISSING else discord.utils.MISSING)
    else:
        await interaction.response.send_message(content=message, file=file, embed=embed, ephemeral=ephemeral)
#--------------------


# 読み込み結果の出力

#--------------------


#ローカルファイルの読み込み結果出力
sys_logger.info("bot instance root -> " + now_path)
sys_logger.info("server instance root -> " + server_path)
sys_logger.info("read token file -> " + now_path + "/" +".token")
sys_logger.info("read config file -> " + now_path + "/" +".config")
view_config = config.copy()
view_config["web"]["secret_key"] = "****"
sys_logger.info("config -> " + str(view_config))
if config_changed: sys_logger.info("added config because necessary elements were missing")
#--------------------


# 読み込み時関数/ループ関数/メッセージ受信時関数を定義

#--------------------

@tasks.loop(seconds=10)
async def update_loop():
    global discord_terminal_item, discord_terminal_send_length, discord_loop_is_run
    # discord_loop_is_runを確認(2回以上実行された場合は処理をしない)
    if discord_loop_is_run: return
    try:
        discord_loop_is_run = True
        with status_lock:
            if process is not None:
                await client.change_presence(activity=discord.Game(name=ACTIVITY_NAME["running"]))
            else:
                await client.change_presence(activity=discord.Game(name=ACTIVITY_NAME["ended"]))
            # discord_log_msgにデータがあれば送信
            # 送信が無効の場合
            if where_terminal == False:
                discord_log_msg.clear()
                discord_loop_is_run = False
                return
            pop_flg = False
            while len(discord_log_msg) > 0:
                while len(discord_log_msg) > terminal_capacity:
                    discord_log_msg.popleft()
                    pop_flg = True
                if pop_flg:
                    await client.get_channel(where_terminal).send(f"データ件数が{terminal_capacity}件を超えたため以前のデータを破棄しました。より多くのログを出力するには.config内のterminal.capacityを変更してください。")
                    pop_flg = False
                discord_terminal_send_length += len(discord_log_msg[0]) + 1
                if discord_terminal_send_length >= 1900:
                    # 送信処理(where_terminal chに送信)
                    await client.get_channel(where_terminal).send("```ansi\n" + ''.join(discord_terminal_item) + "\n```")
                    # discord_terminal_itemをリセット
                    discord_terminal_item = deque()
                    discord_terminal_send_length = len(discord_log_msg[0]) + 1
                    # 連投を避けるためにsleep
                    await asyncio.sleep(1)
                discord_terminal_item.append(discord_log_msg.popleft() + "\n")
            # 残っていれば送信
            if len(discord_terminal_item) > 0:
                await client.get_channel(where_terminal).send("```ansi\n" + ''.join(discord_terminal_item) + "\n```")
                discord_terminal_item = deque()
                discord_terminal_send_length = 0
        discord_loop_is_run = False
    except Exception as e:
        sys_logger.error(e)
        discord_loop_is_run = False

# メッセージが送信されたときの処理
@client.event
async def on_message(message: discord.Message):
    try:
        # ボット自身のメッセージは無視する
        if message.author == client.user:
            return
        # terminal ch以外のメッセージは無視
        if message.channel.id != where_terminal:
            return
        # 管理者以外をはじく
        if not await is_administrator(message.author) and not await is_force_administrator(message.author):
            await message.reply("permission denied")
            return
        # サーバーが閉じていたらはじく
        if process is None or process.poll() is not None:
            await message.reply("server is not running")
            return
        # コマンドを処理
        cmd_list = message.content.split(" ")
        # 許可されないコマンドをはじく
        if message.author.bot is True: pass
        elif cmd_list[0] not in allow_cmd:
            sys_logger.error('unknown command : ' + " ".join(cmd_list))
            await message.reply("this command is not allowed")
            return
        else:
            process.stdin.write(message.content + "\n")
            process.stdin.flush()
    except Exception as e:
        sys_logger.error(e)

@client.event
async def on_ready():
    global process
    ready_logger.info('discord bot logging on')
    update_loop.start()
    try:
        #サーバーの起動
        await client.change_presence(activity=discord.Game(ACTIVITY_NAME["starting"]))
        if process is  None:
            #server を実行する
            process = subprocess.Popen([server_path + server_name],cwd=server_path,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,encoding="utf-8")
            threading.Thread(target=server_logger,args=(process,deque())).start()
            ready_logger.info('server starting')
        else:
            ready_logger.info('skip server starting because server already running')
        # アクティビティを設定 
        await client.change_presence(activity=discord.Game(ACTIVITY_NAME["running"])) 
        # スラッシュコマンドを同期 
        await tree.sync()
    except Exception as e:
        sys_logger.error(f"error on ready -> {e}")
#--------------------


# 機能関数読み込み

#--------------------



#--------------------





def core_stop() -> str:
    global process,use_stop
    if is_stopped_server(stop_logger):
        return RESPONSE_MSG["other"]["is_not_running"]
    use_stop = True
    stop_logger.info('server stopping')
    process.stdin.write(STOP + "\n")
    process.stdin.flush()
    return RESPONSE_MSG["stop"]["success"]

def core_start() -> str:
    global process,use_stop
    if is_running_server(start_logger):
        return RESPONSE_MSG["other"]["is_running"]
    start_logger.info('server starting')
    process = subprocess.Popen([server_path + server_name],cwd=server_path,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,encoding="utf-8")
    threading.Thread(target=server_logger,args=(process,deque())).start()
    return RESPONSE_MSG["start"]["success"]

#--------------------


#--------------------


# スラッシュコマンドを定義

#--------------------


#start
@tree.command(name="start",description=COMMAND_DESCRIPTION[lang]["start"])
async def start(interaction: discord.Interaction):
    await print_user(start_logger,interaction.user)
    if await user_permission(interaction.user) < COMMAND_PERMISSION["start"]: 
        await not_enough_permission(interaction,start_logger)
        return
    result = core_start()
    embed = discord.Embed(title = f"/start", color=bot_color)
    embed.add_field(name="",value=result,inline=False)
    embed.set_image(url = embed_under_line_url)
    await interaction.response.send_message(embed=embed)
    if result == RESPONSE_MSG["other"]["is_running"]:
        return
    await client.change_presence(activity=discord.Game(ACTIVITY_NAME["running"]))

#/stop
@tree.command(name="stop",description=COMMAND_DESCRIPTION[lang]["stop"])
async def stop(interaction: discord.Interaction):
    global use_stop
    await print_user(stop_logger,interaction.user)
    global process
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["stop"]: 
        #両方not(権限がないなら)
        await not_enough_permission(interaction,stop_logger)
        return
    result = core_stop()
    embed = discord.Embed(title = f"/stop", color=bot_color)
    embed.add_field(name="",value=result,inline=False)
    embed.set_image(url = embed_under_line_url)

    await interaction.response.send_message(embed=embed)
    if result == RESPONSE_MSG["other"]["is_not_running"]:
        return
    await client.change_presence(activity=discord.Game(ACTIVITY_NAME["ending"])) 
    while True:
        #終了するまで待つ
        if process is None:
            await client.change_presence(activity=discord.Game(ACTIVITY_NAME["ended"])) 
            break
        await asyncio.sleep(1)


#--------------------


# グループの設定
# root
command_group_permission = app_commands.Group(name="permission",description="permission group")

#/admin force <add/remove>
@command_group_permission.command(name="change",description=COMMAND_DESCRIPTION[lang]["permission"]["change"])
async def change(interaction: discord.Interaction,level: int,user:discord.User):
    await print_user(admin_logger,interaction.user)
    embed = discord.Embed(title = f"/permission change {level} {user}", color=bot_color)
    embed.set_image(url = embed_under_line_url)
    if await user_permission(interaction.user) < COMMAND_PERMISSION["permission change"]:
        await not_enough_permission(interaction,lang_logger)
        return
    async def read_force_admin():
        global bot_admin
        bot_admin = config["discord_commands"]["admin"]["members"]
    # 権限レベル1~4を付与
    if level >= 1 and level <= USER_PERMISSION_MAX:
        if user.id in config["discord_commands"]["admin"]["members"]:
            embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["already_added"],inline=False)
            await interaction.response.send_message(embed=embed)
            return
        config["discord_commands"]["admin"]["members"][str(user.id)] = level
        #configファイルを変更する
        await rewrite_config(config)
        await read_force_admin()
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["add_success"].format(user),inline=False)
        await interaction.response.send_message(embed=embed)
        admin_logger.info(f"exec force admin add {user}")
    elif level == 0:
        if user.id not in config["discord_commands"]["admin"]["members"]:
            embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["already_removed"],inline=False)
            await interaction.response.send_message(embed=embed)
            return
        config["discord_commands"]["admin"]["members"].pop(str(user.id))
        #configファイルを変更する
        await rewrite_config(config)
        await read_force_admin()
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["remove_success"].format(user),inline=False)
        await interaction.response.send_message(embed=embed)
        admin_logger.info(f"exec force admin remove {user}")
    else:
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["invalid_level"].format(USER_PERMISSION_MAX,level),inline=False)
        await interaction.response.send_message(embed=embed)
        admin_logger.info("invalid level")

#/permission <user>
@command_group_permission.command(name="view",description=COMMAND_DESCRIPTION[lang]["permission"]["view"])
async def view(interaction: discord.Interaction,user:discord.User,detail:bool):
    await print_user(permission_logger,interaction.user)
    embed = discord.Embed(title = f"/permission view {user} {detail}", color=bot_color)
    embed.set_image(url = embed_under_line_url)
    COMMAND_MAX_LENGTH = max([len(key) for key in COMMAND_PERMISSION])
    value = {"admin":"☐","force_admin":"☐"}
    if await is_administrator(user): value["admin"] = f"☑({USER_PERMISSION_MAX})"
    value["force_admin"] = await user_permission(user)
    if detail:
        my_perm_level = await user_permission(user)
        can_use_cmd = {f"{key}":("☑" if COMMAND_PERMISSION[key] <= my_perm_level else "☐") + f"({COMMAND_PERMISSION[key]})" for key in COMMAND_PERMISSION}
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["success"].format(user,value["admin"],value["force_admin"]) + "\n```\n"+"\n".join([f"{key.ljust(COMMAND_MAX_LENGTH)} : {value}" for key,value in can_use_cmd.items()]) + "\n```",inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["success"].format(user,value["admin"],value["force_admin"]),inline=False)
        await interaction.response.send_message(embed=embed)
    permission_logger.info("send permission info : " + str(user.id) + f"({user})")

tree.add_command(command_group_permission)
#--------------------



#/lang <lang>
@tree.command(name="lang",description=COMMAND_DESCRIPTION[lang]["lang"])
@app_commands.choices(
    language = [
        app_commands.Choice(name="en",value="en"),
        app_commands.Choice(name="ja",value="ja"),
    ]
)
async def language(interaction: discord.Interaction,language:str):
    """
    config の lang を変更する
    permission : discord 管理者 (2)
    lang : str "en"/"ja"
    """
    await print_user(lang_logger,interaction.user)
    global lang
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["lang"]:
        await not_enough_permission(interaction,lang_logger)
        return
    #データの書き換え
    config["discord_commands"]["lang"] = language
    lang = config["discord_commands"]["lang"]
    #configファイルを変更する
    await rewrite_config(config)
    #textデータを再構築
    await get_text_dat()
    embed = discord.Embed(title = f"/lang {language}", color=bot_color)
    embed.add_field(name="",value=RESPONSE_MSG["lang"]["success"].format(language))
    embed.set_image(url = embed_under_line_url)
    await interaction.response.send_message(embed=embed)
    lang_logger.info("change lang to " + lang)

#/cmd serverin <server command>
#/cmd stdin 


#--------------------





#--------------------


# グループの設定
# root
command_group_cmd = app_commands.Group(name="cmd",description="cmd group")

serverin_logger = cmd_logger.getChild("serverin")
#--------------------



#--------------------




@command_group_cmd.command(name="serverin",description=COMMAND_DESCRIPTION[lang]["cmd"]["serverin"])
async def cmd(interaction: discord.Interaction,command:str):
    await print_user(serverin_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd serverin {command}")
    embed.set_image(url = embed_under_line_url)
    global is_back_discord,cmd_logs
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd serverin"]: 
        await not_enough_permission(interaction,serverin_logger)
        return
    #サーバー起動確認
    if is_stopped_server(serverin_logger): 
        serverin_logger.info("is not running")
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_not_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    #コマンドの利用許可確認
    if command.split()[0] not in allow_cmd:
        serverin_logger.error('unknown command : ' + command)
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["serverin"]["skipped_cmd"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    serverin_logger.info("run command : " + command)
    process.stdin.write(command + "\n")
    process.stdin.flush()
    #結果の返却を要求する
    is_back_discord = True
    #結果を送信できるまで待機
    while True:
        #何もなければ次を待つ
        if len(cmd_logs) == 0:
            await asyncio.sleep(0.1)
            continue
        embed.add_field(name="",value=cmd_logs.popleft(),inline=False)
        await interaction.response.send_message(embed=embed)
        break
#--------------------




#--------------------


stdin_logger = cmd_logger.getChild("stdin")

#サブグループstdinを作成
command_group_cmd_stdin = app_commands.Group(name="stdin",description="stdin group")
# サブグループを設定
command_group_cmd.add_command(command_group_cmd_stdin)


sys_files = [".config",".token","logs","mikanassets"]
important_bot_file = [
    os.path.abspath(os.path.join(os.path.dirname(__file__),i)) for i in sys_files
] + [
    os.path.join(server_path,i) for i in sys_files
]



# 重要ファイルでないか(最高権限要求するようなファイルかを確認)
async def is_important_bot_file(path):
    # 絶対パスを取得
    path = os.path.abspath(path)
    # 重要ファイルの場合はTrueを返す
    for f in important_bot_file:
        if path.startswith(f):
            return True
    return False
#--------------------


#--------------------



stdin_ls_logger = stdin_logger.getChild("ls")
@command_group_cmd_stdin.command(name="ls",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["ls"])
async def ls(interaction: discord.Interaction, file_path: str):
    await print_user(stdin_ls_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd stdin ls {file_path}")
    embed.set_image(url = embed_under_line_url)
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin ls"]:
        await not_enough_permission(interaction,stdin_ls_logger)
        return
    # server_path + file_path 閲覧パスの生成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_ls_logger.info("invalid path -> " + file_path)
        return
    # 対象が存在するか
    if not os.path.exists(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["ls"]["file_not_found"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_ls_logger.info("file not found -> " + file_path)
        return
    # 対象がディレクトリであるか
    if not os.path.isdir(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["ls"]["not_directory"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_ls_logger.info("not directory -> " + file_path)
        return
    # lsコマンドを実行
    files = os.listdir(file_path)

    colorized_files = deque()
    
    for f in files:
        full_path = os.path.join(file_path, f)
        if os.path.isdir(full_path):
            # ディレクトリは青色
            colorized_files.append(f"\033[34m{f}\033[0m")
        elif os.path.islink(full_path):
            # シンボリックリンクは紫
            colorized_files.append(f"\033[35m{f}\033[0m")
        else:
            # 通常ファイルは緑
            colorized_files.append(f"\033[32m{f}\033[0m")
    formatted_files = "\n".join(colorized_files)
    stdin_ls_logger.info("list directory -> " + file_path)
    if len(formatted_files) > 2000:
            with io.StringIO() as temp_file:
                temp_file.write("\n".join(files))
                temp_file.seek(0)
                # Discordファイルオブジェクトに変換して送信
                discord_file = discord.File(temp_file, filename="directory_list.txt")
                embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["ls"]["to_long"].format(file_path),inline=False)
                await interaction.response.send_message(
                    embed=embed,
                    file=discord_file
                )
    else:
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["ls"]["success"].format(file_path,formatted_files),inline=False)
        await interaction.response.send_message(embed=embed)

#--------------------


#--------------------


stdin_mk_logger = stdin_logger.getChild("mk")

# 以下のコマンドはserver_pathを起点としてそれ以下のファイルを操作する
# ファイル送信コマンドを追加
@command_group_cmd_stdin.command(name="mk",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mk"])
async def mk(interaction: discord.Interaction, file_path: str,file:discord.Attachment|None = None):
    await print_user(stdin_mk_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd stdin mk {file_path} {file.filename if file is not None else ''}")
    embed.set_image(url = embed_under_line_url)
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin mk"]:
        await not_enough_permission(interaction,stdin_mk_logger)
        return
    #サーバー起動確認
    if is_running_server(stdin_mk_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # server_path + file_path にファイルを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mk_logger.info("invalid path -> " + file_path)
        return
    # ファイルがリンクであれば拒否
    if os.path.islink(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mk"]["is_link"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mk_logger.info("file is link -> " + file_path)
        return
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if not await is_administrator(interaction.user) and await is_important_bot_file(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mk_logger.info("permission denied -> " + file_path)
        return
    else:
        # 空のファイルを作成
        open(file_path,"w").close()
        # ファイルをfile_pathに保存
        if file is not None:
            await file.save(file_path)
    stdin_mk_logger.info("create file -> " + file_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mk"]["success"].format(file_path),inline=False)
    await interaction.response.send_message(embed=embed)

#--------------------


#--------------------


stdin_rm_logger = stdin_logger.getChild("rm")

@command_group_cmd_stdin.command(name="rm",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["rm"])
async def rm(interaction: discord.Interaction, file_path: str):
    await print_user(stdin_rm_logger,interaction.user)
    embed = discord.Embed(title=f"/cmd stdin rm {file_path}",color=bot_color)
    embed.set_image(url = embed_under_line_url)
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin rm"]:
        await not_enough_permission(interaction,stdin_rm_logger)
        return
    #サーバー起動確認
    if is_running_server(stdin_rm_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # server_path + file_path のパスを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rm_logger.info("invalid path -> " + file_path)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["rm"]["file_not_found"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rm_logger.info("file not found -> " + file_path)
        return
    # 該当のアイテムがファイルか
    if not os.path.isfile(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["not_file"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rm_logger.info("not file -> " + file_path)
        return
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if not await is_administrator(interaction.user) and await is_important_bot_file(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rm_logger.info("permission denied -> " + file_path)
        return
    # ファイルを削除
    os.remove(file_path)
    stdin_rm_logger.info("remove file -> " + file_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["rm"]["success"].format(file_path),inline=False)
    await interaction.response.send_message(embed=embed)

#--------------------


#--------------------


stdin_mkdir_logger = stdin_logger.getChild("mkdir")

@command_group_cmd_stdin.command(name="mkdir",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mkdir"])
async def mkdir(interaction: discord.Interaction, dir_path: str):
    await print_user(stdin_mkdir_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd stdin mkdir {dir_path}")
    embed.set_image(url = embed_under_line_url)
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin mkdir"]:
        await not_enough_permission(interaction,stdin_mkdir_logger)
        return
    # server_path + file_path のパスを作成
    dir_path = os.path.abspath(os.path.join(server_path,dir_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(dir_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mkdir_logger.info("invalid path -> " + dir_path)
        return
    # 既に存在するか確認
    if os.path.exists(dir_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mkdir"]["exists"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mkdir_logger.info("directory already exists -> " + dir_path)
        return
    # ディレクトリを作成
    os.makedirs(dir_path)
    stdin_mkdir_logger.info("create directory -> " + dir_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mkdir"]["success"].format(dir_path),inline=False)
    await interaction.response.send_message(embed=embed)

#--------------------


#--------------------


stdin_rmdir_logger = stdin_logger.getChild("rmdir")

@command_group_cmd_stdin.command(name="rmdir",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["rmdir"])
async def rmdir(interaction: discord.Interaction, dir_path: str):
    await print_user(stdin_rmdir_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd stdin rmdir {dir_path}")
    embed.set_image(url = embed_under_line_url)
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin rmdir"]:
        await not_enough_permission(interaction,stdin_rmdir_logger)
        return
    #サーバー起動確認
    if is_running_server(stdin_rmdir_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # server_path + file_path のパスを作成
    dir_path = os.path.abspath(os.path.join(server_path,dir_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(dir_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rmdir_logger.info("invalid path -> " + dir_path)
        return
    # 既に存在するか確認
    if not os.path.exists(dir_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["rmdir"]["not_exists"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rmdir_logger.info("directory not exists -> " + dir_path)
        return
    # 全ての条件を満たすが、権限が足りず、対象が重要なディレクトリか確認
    if await is_important_bot_file(dir_path) and not await is_administrator(interaction.user):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rmdir_logger.info("permission denied -> " + dir_path)
        return
    # ディレクトリを削除
    rmtree(dir_path)
    stdin_rmdir_logger.info("remove directory -> " + dir_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["rmdir"]["success"].format(dir_path),inline=False)
    await interaction.response.send_message(embed=embed)

#--------------------


#--------------------


stdin_mv_logger = stdin_logger.getChild("mv")

@command_group_cmd_stdin.command(name="mv",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mv"])
async def cmd_stdin_mv(interaction: discord.Interaction, path: str, dest: str):
    await print_user(stdin_mv_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd stdin mv {path} {dest} ")
    embed.set_image(url = embed_under_line_url)
    # 権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin mv"]:
        await not_enough_permission(interaction,stdin_mv_logger)
        return
    #サーバー起動確認
    if is_running_server(stdin_mv_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("server is running")
        return
    # server_path + path のパスを作成
    path = os.path.abspath(os.path.join(server_path,path))
    # server_path + dest のパスを作成
    dest = os.path.abspath(os.path.join(server_path,dest))
    # 操作可能なパスか確認
    if not is_path_within_scope(path) or not is_path_within_scope(dest):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(path,dest),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("invalid path -> " + path + " or " + dest)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(path):
        embed.add_field(name="",velue=RESPONSE_MSG["cmd"]["stdin"]["mv"]["file_not_found"].format(path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("file not found -> " + path)
        return
    # 該当のアイテムがファイルか
    if not os.path.isfile(path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["not_file"].format(path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("not file -> " + path)
        return
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if not await is_administrator(interaction.user) and (await is_important_bot_file(path) or await is_important_bot_file(dest)):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("permission denied -> " + path + " or " + dest)
        return
    # ファイルを移動
    shutil_move(path,dest)
    stdin_mv_logger.info("move file -> " + path + " -> " + dest)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mv"]["success"].format(path,dest),inline=False)
    await interaction.response.send_message(embed=embed)
#--------------------


#--------------------


stdin_send_discord_logger = stdin_logger.getChild("send-discord")


discord_multi_thread_return_dict = {}
def send_file_io(_id, file_obj, file_name) -> requests.Response:
    response = requests.post("https://file.io/", files={"file": (file_name, file_obj)})
    discord_multi_thread_return_dict[_id] = response
    

send_discord_timeout_sec = 60 * 25

@command_group_cmd_stdin.command(name="send-discord",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["send-discord"])
async def send_discord(interaction: discord.Interaction, path: str):
    await print_user(stdin_send_discord_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd stdin send-discord {path}")
    embed.set_image(url = embed_under_line_url)
    file_path = os.path.abspath(os.path.join(server_path,path))  # ファイルのパス
    file_name = os.path.basename(file_path)
    file_size_limit = 9 * 1024 * 1024  # 9MB
    file_size_limit_web = 2 * 1024 * 1024 * 1024  # 2GBを超えた場合file.ioでも無理なのでエラー
    # 権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin send-discord"]:
        await not_enough_permission(interaction,stdin_send_discord_logger)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_not_found"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_send_discord_logger.info("file not found -> " + file_path)
        return
    # パスが許可されているかを確認
    if not is_path_within_scope(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_send_discord_logger.info("invalid path -> " + file_path)
        return
    # 該当のアイテムがディレクトリならzip圧縮をする
    if os.path.isdir(file_path):
        # とりあえずdiscordに送っておく
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["is_zip"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)
        stdin_send_discord_logger.info("make zip -> " + str(file_path))
        zip_buffer,file_size = await create_zip_async(file_path)
        base_file_path = file_path
        file_path = zip_buffer
        file_path.seek(0)
        stdin_send_discord_logger.info("zip -> " + str(file_path) + f"({base_file_path})" + " : " + str(file_size))
        file_name = file_name + ".zip"
        file_obj = file_path
    else:
        # ファイルサイズをチェック
        file_size = os.path.getsize(file_path)
        stdin_send_discord_logger.info("file -> " + str(file_path))
        # ファイルを開く
        file_obj = open(file_path, "rb")
    if file_size > file_size_limit_web:
        stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit_web"].format(file_size,file_size_limit_web),inline=False)
        await send_discord_message_or_edit(interaction=interaction,embed=embed,ephemeral=True)
    if file_size > file_size_limit: # なぜか400errの時async loopが落ちてしまうっぽい問題が解決できなさそうな雰囲気なので一旦削除
        stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit"].format(file_size,file_size_limit),inline=False)
        await send_discord_message_or_edit(interaction=interaction,embed=embed,ephemeral=True)
        # file.ioにアップロード
        try:
            timeout_sec = send_discord_timeout_sec
            # uuidを使って、POSTするスレッドの戻り値を待機する
            discord_dict_id = uuid.uuid4()
            io_thread = threading.Thread(target=send_file_io,args=(discord_dict_id,file_obj,file_name),daemon=True)
            io_thread.start()
            # discord_multi_thread_return_dict[discord_dict_id]にPOSTスレッドがresponseをセットするまで繰り返し
            while discord_dict_id not in discord_multi_thread_return_dict:
                await asyncio.sleep(1)
                timeout_sec -= 1
                if timeout_sec <= 0:
                    raise asyncio.TimeoutError
            if discord_multi_thread_return_dict[discord_dict_id].status_code != 200:
                status = discord_multi_thread_return_dict[discord_dict_id].status_code
                reason = discord_multi_thread_return_dict[discord_dict_id].reason
                text = discord_multi_thread_return_dict[discord_dict_id].text
                stdin_send_discord_logger.error("upload to file.io failed -> " + str(file_path) + " ,status -> " + str(status) + " , " + str(reason) + " :: " + str(text))
                embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_io_error"].format(interaction.user.id,status,reason,text),inline=False)
                await send_discord_message_or_edit(interaction=interaction,embed=embed)
                return
            response = discord_multi_thread_return_dict[discord_dict_id]
            link = response.json()["link"]
            stdin_send_discord_logger.info("upload to file.io -> " + str(file_path) + " : " + str(response.status_code))
            embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["success"].format(interaction.user.id,link),inline=False)
            await send_discord_message_or_edit(interaction=interaction,embed=embed)
        except Exception as e:
            if isinstance(e, asyncio.TimeoutError) or isinstance(e,aiohttp.ClientError):
                stdin_send_discord_logger.error("upload to file.io failed (timeout) -> " + str(file_path))
                embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["timeout"].format(interaction.user.id,send_discord_timeout_sec),inline=False)
                await send_discord_message_or_edit(interaction=interaction,embed=embed)
            else:
                import traceback
                stdin_send_discord_logger.error(traceback.format_exc())
                stdin_send_discord_logger.error("raise upload to file.io failed")
                embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["raise_error"].format(interaction.user.id,traceback.format_exc()),inline=False)
                await send_discord_message_or_edit(interaction=interaction,embed=embed)
        finally:
            # file_objが開いていたら閉じる(file_objはopen() or io.BytesIO()で開いたもの)
            file_obj.close()
            stdin_send_discord_logger.info("close file -> " + str(file_path))
    else:
        # Discordで直接送信
        stdin_send_discord_logger.info("send to discord -> " + str(file_path))
        await send_discord_message_or_edit(interaction=interaction,file=discord.File(file_path,filename=file_name),embed=embed,ephemeral=True)


#--------------------


#--------------------


stdin_wget_logger = stdin_logger.getChild("wget")

@command_group_cmd_stdin.command(name="wget",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["wget"])
async def wget(interaction: discord.Interaction,url:str,path:str = "mi_dl_file.tmp"):
    await print_user(stdin_wget_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd stdin wget {url} {path} ")
    embed.set_image(url = embed_under_line_url)
    # 権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin wget"]: 
        await not_enough_permission(interaction,stdin_wget_logger)
        return
    save_path = os.path.abspath(os.path.join(server_path,path))
    # 既にファイルが存在しているか確認
    if os.path.exists(save_path):
        stdin_wget_logger.info("file already exists -> " + save_path)
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["wget"]["already_exists"].format(path),inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # pathが操作可能か確認
    if not is_path_within_scope(save_path):
        stdin_wget_logger.info("invalid path -> " + save_path)
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(save_path),inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # 管理者権限を持っていなくて、重要ファイルをダウンロードする場合は拒否
    if not await is_administrator(interaction.user) and await is_important_bot_file(save_path):
        stdin_wget_logger.info("permission denied -> " + save_path)
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(save_path),inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # URLからファイルをダウンロード
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    stdin_wget_logger.info("download failed -> " + url)
                    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["wget"]["download_failed"].format(url),inline=False)
                    await interaction.response.send_message(embed=embed)
                    return

                # ファイルを保存
                with open(save_path, 'wb') as file:
                    file.write(await response.read())
        except Exception as e:
            stdin_wget_logger.info("download failed -> " + url + f"({e})")
            embed.add_field(name="",value=f"invalid url -> ({e})",inline=False)
            await interaction.response.send_message(embed=embed)
            return
    stdin_wget_logger.info("download success -> " + url + " to " + save_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["wget"]["download_success"].format(url,save_path),inline=False)
    await interaction.response.send_message(embed=embed)
#--------------------



#--------------------


# コマンドを追加
tree.add_command(command_group_cmd)
#--------------------


#--------------------


#/backup()
@tree.command(name="backup",description=COMMAND_DESCRIPTION[lang]["backup"])
async def backup(interaction: discord.Interaction,world_name:str = "worlds"):
    await print_user(backup_logger,interaction.user)
    global exist_files, copyed_files
    embed = discord.Embed(color=bot_color,title= f"/backup {world_name}")
    embed.set_image(url = embed_under_line_url)
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["backup"]:
        await not_enough_permission(interaction,backup_logger) 
        return
    #サーバー起動確認
    if is_running_server(backup_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["backup"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # 操作可能パスかを判定
    if not is_path_within_scope(server_path + world_name):
        backup_logger.error("path not allowed : " + server_path + world_name)
        embed.add_field(name="",value = RESPONSE_MSG["backup"]["path_not_allowed"] + ":" + server_path + world_name,inline=False)
        await interaction.response.send_message(embed=embed)
        return
    backup_logger.info('backup started')
    #server_path + world_namの存在確認
    if os.path.exists(server_path + world_name):
        await interaction.response.send_message(embed=embed)
        # discordにcopyed_files / exist_filesをプログレスバーで
        await dircp_discord(server_path + world_name,backup_path + "/",interaction,embed)
        backup_logger.info('backup done')
    else:
        backup_logger.error('data not found : ' + server_path + world_name)
        embed.add_field(name="",value=RESPONSE_MSG["backup"]["data_not_found"] + ":" + server_path + world_name,inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)


#--------------------


#/update
@tree.command(name="update",description=COMMAND_DESCRIPTION[lang]["update"])
async def update(interaction: discord.Interaction):
    await print_user(update_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/update")
    embed.set_image(url = embed_under_line_url)
    #サーバー起動確認
    if is_running_server(update_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    #サーバー管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["update"]: 
        await not_enough_permission(interaction,update_logger)
        return
    #py_builder.pyを更新
    await update_self_if_commit_changed(interaction=interaction,embed=embed,text_pack=RESPONSE_MSG["update"],sender=send_discord_message_or_edit)
#--------------------


#/replace <py file>
@tree.command(name="replace",description=COMMAND_DESCRIPTION[lang]["replace"])
async def replace(interaction: discord.Interaction,py_file:discord.Attachment):
    await print_user(replace_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/replace {py_file.filename}")
    embed.set_image(url = embed_under_line_url)
    #デフォルトでコマンドを無効に
    if not allow["replace"]:
        embed.add_field(name="",value=RESPONSE_MSG["replace"]["not_allow"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["replace"]:
        await not_enough_permission(interaction,replace_logger)
        return
    #サーバー起動確認
    if is_running_server(replace_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    replace_logger.info('replace started')
    # ファイルをすべて読み込む
    with open(temp_path + "/new_source.py","w",encoding="utf-8") as f:
        f.write((await py_file.read()).decode("utf-8").replace("\r\n","\n"))
    # discordにコードを置き換える
    replace_logger.info('replace done')
    embed.add_field(name="",value=RESPONSE_MSG["replace"]["progress"],inline=False)
    await interaction.response.send_message(embed=embed)
    response = await interaction.original_response()
    #interaction id を保存
    msg_id = str(response.id)
    channel_id = str(interaction.channel_id)
    replace_logger.info("call update.py")
    replace_logger.info('replace args : ' + msg_id + " " + channel_id)
    os.execv(sys.executable,["python3",now_path + "/mikanassets/" + "update.py",temp_path + "/new_source.py",msg_id,channel_id,now_file])

#/ip
@tree.command(name="ip",description=COMMAND_DESCRIPTION[lang]["ip"])
async def ip(interaction: discord.Interaction):
    await print_user(ip_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/ip")
    embed.set_image(url = embed_under_line_url)
    if await user_permission(interaction.user) < COMMAND_PERMISSION["ip"]:
        await not_enough_permission(interaction,ip_logger)
        return
    if not allow["ip"]:
        embed.add_field(name="",value=RESPONSE_MSG["ip"]["not_allow"],inline=False)
        await interaction.response.send_message(embed=embed)
        ip_logger.error('ip is not allowed')
        return
    # ipをget
    try:
        addr = requests.get("https://api.ipify.org")
    except:
        ip_logger.error('get ip failed')
        embed.add_field(name="",value=RESPONSE_MSG["ip"]["get_ip_failed"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    if config["mc"]:
        ip_logger.info('get ip : ' + addr.text + ":" + properties["server-port"])
        embed.add_field(name=RESPONSE_MSG["ip"]["msg_startwith"] + addr.text + ":" + properties["server-port"],value=f"(ip:{addr.text} port(ポート):{properties['server-port']})",inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        ip_logger.info('get ip : ' + addr.text)
        embed.add_field(name="",value=RESPONSE_MSG["ip"]["msg_startwith"] + addr.text,inline=False)
        await interaction.response.send_message(embed=embed)


async def get_log_files_choice_format(interaction: discord.Interaction, current: str):
    current = current.translate(str.maketrans("/\\:","--_"))
    #全てのファイルを取得
    s_logfiles = os.listdir(server_path + "logs/")
    a_logfiles = os.listdir(now_path + "/logs/")
    logfiles = (s_logfiles + a_logfiles)
    # current と一致するものを返す & logファイル & 25個制限を実装
    logfiles = [i for i in logfiles if current in i and i.endswith(".log")][-25:]
    # open("./tmp.txt","w").write("\n".join(logfiles))
    return [
        app_commands.Choice(name = i,value = i) for i in logfiles
    ]


#/log <filename>
# filename : ログファイル名
# filename == None -> 最新のログ10件
# filename != None -> server_path + "logs/" または now_path + "logs/"の中を候補表示する
@tree.command(name="logs",description=COMMAND_DESCRIPTION[lang]["logs"])
@app_commands.autocomplete(filename = get_log_files_choice_format)
async def logs(interaction: discord.Interaction,filename:str = None):
    await print_user(log_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/logs {filename}")
    embed.set_image(url = embed_under_line_url)
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["logs"]: 
        await not_enough_permission(interaction,log_logger)
        return
    # discordにログを送信
    if filename is None:
        # 2000文字こ超えない最長のログを取得
        send_msg = []
        send_length = 0
        for i in log_msg:
            send_length += len(i)
            send_msg.append(i)
            while True:
                if send_length > 1900:
                    delete = send_msg.pop(0)
                    send_length -= len(delete)
                else:
                    break
        # embed.add_field(name="",value="```ansi\n" + "\n".join(send_msg) + "\n```",inline=False)
        await interaction.response.send_message("```ansi\n" + "\n".join(send_msg) + "\n```")
    else:
        if "/" in filename or "\\" in filename or "%" in filename:
            log_logger.error('invalid filename : ' + filename + "\n" + f"interaction user / id：{interaction.user} {interaction.user.id}")
            embed.add_field(name="",value=RESPONSE_MSG["logs"]["cant_access_other_dir"],inline=False)
            await interaction.response.send_message(embed=embed)
            return
        elif not filename.endswith(".log"):
            log_logger.error('invalid filename : ' + filename + "\n" + f"interaction user / id：{interaction.user} {interaction.user.id}")
            embed.add_field(name="",value=RESPONSE_MSG["logs"]["not_found"],inline=False)
            await interaction.response.send_message(embed=embed)
            return
        elif filename.startswith("server"):
            filename = server_path + "logs/" + filename
        elif filename.startswith("all"):
            filename = now_path + "/logs/" + filename
        else:
            filename = server_path + "logs/" + filename
            if not os.path.exists(filename):
                if os.path.exists(now_path + "/logs/" + filename):
                    filename = now_path + "/logs/" + filename
                else:
                    log_logger.error('invalid filename : ' + filename + "\n" + f"interaction user / id：{interaction.user} {interaction.user.id}")
                    embed.add_field(name="",value=RESPONSE_MSG["logs"]["not_found"],inline=False)
                    await interaction.response.send_message(embed=embed)
                    return
        #ファイルを返却
        await interaction.response.send_message(file=discord.File(filename))
    log_ = "Server logs" if filename is None else filename
    log_logger.info(f"sended logs -> {log_}")


def gen_web_token():
    from random import choices
    from string import ascii_letters, digits
    return ''.join(choices(ascii_letters + digits, k=12))

#/tokengen トークンを生成する
@tree.command(name="tokengen",description=COMMAND_DESCRIPTION[lang]["tokengen"])
async def tokengen(interaction: discord.Interaction):
    await print_user(token_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/tokengen")
    embed.set_image(url = embed_under_line_url)
    #権限レベルを確認
    if await user_permission(interaction.user) < COMMAND_PERMISSION["tokengen"]:
        await not_enough_permission(interaction,token_logger)
        return
    new_token = gen_web_token()
    embed.add_field(name=RESPONSE_MSG["tokengen"]["success"].format(""),value=new_token,inline=False)
    await interaction.response.send_message(embed=embed,ephemeral=True)
    token_logger.info('token sent')
    #トークンをファイルに書き込む
    dat_token = {"token":new_token, "deadline":(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")}
    web_tokens.append(dat_token)
    with open(now_path + "/mikanassets/web/usr/tokens.json","r",encoding="utf-8") as f:
        item = json.load(f)
        item["tokens"].append(dat_token)
    with open(now_path + "/mikanassets/web/usr/tokens.json","w",encoding="utf-8") as f:
        json.dump(item,f,indent=4,ensure_ascii=False)
    token_logger.info('token added : ' + str(dat_token))

#/terminal
@tree.command(name="terminal",description=COMMAND_DESCRIPTION[lang]["terminal"])
async def terminal(interaction: discord.Interaction):
    global where_terminal
    await print_user(terminal_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/terminal")
    embed.set_image(url = embed_under_line_url)
    # 権限レベルが足りていないなら
    if await user_permission(interaction.user) < COMMAND_PERMISSION["terminal"]:
        await not_enough_permission(interaction,terminal_logger)
        return
    #発言したチャンネルをwhere_terminalに登録
    where_terminal = interaction.channel_id
    config["discord_commands"]["terminal"]["discord"] = where_terminal
    terminal_logger.info(f"terminal setting -> {where_terminal}")
    #configを書き換え
    with open(now_path + "/.config","w") as f:
        json.dump(config,f,indent=4,ensure_ascii=False)
    embed.add_field(name="",value=RESPONSE_MSG["terminal"]["success"].format(where_terminal),inline=False)
    await interaction.response.send_message(embed=embed)


#/help
@tree.command(name="help",description=COMMAND_DESCRIPTION[lang]["help"])
async def help(interaction: discord.Interaction):
    await print_user(help_logger,interaction.user)
    await interaction.response.send_message(embed=send_help)
    help_logger.info('help sent')

#/exit
@tree.command(name="exit",description=COMMAND_DESCRIPTION[lang]["exit"])
async def exit(interaction: discord.Interaction):
    await print_user(exit_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/exit")
    embed.set_image(url = embed_under_line_url)
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["exit"]: 
        await not_enough_permission(interaction,exit_logger)
        return
    #サーバが動いているなら終了
    if is_running_server(exit_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    embed.add_field(name="",value=RESPONSE_MSG["exit"]["success"],inline=False)
    await interaction.response.send_message(embed=embed)
    exit_logger.info('exit')
    await client.close()
    #waitressサーバーを終了

    sys.exit()

# 拡張コマンドを読み込む

#--------------------

base_extension_logger.info("search extension commands")
extension_commands_group = None
extension_logger = None
def read_extension_commands():
    global extension_commands_group,extension_logger
    extension_commands_groups = deque()
    sys_logger.info("read extension commands ->" + now_path + "/mikanassets/extension")
    # 拡張moduleに追加コマンドが存在すればするだけ読み込む(mikanassets/extension/<拡張名>/commands.py)
    for file in os.listdir(now_path + "/mikanassets/extension"):
        if os.path.isdir(now_path + "/mikanassets/extension/" + file):
            sys_logger.info("read extension commands ->" + now_path + "/mikanassets/extension/" + file)
            if os.path.exists(now_path + "/mikanassets/extension/" + file + "/commands.py"):
                # <拡張名>コマンドグループを作成
                extension_commands_group = app_commands.Group(name="extension-" + file,description="This commands group is extention.\nUse this code at your own risk." + file)
                extension_commands_groups.append(extension_commands_group)
                # 拡張moduleが/mikanassets/extension/<拡張名>/commans.pyにある場合は読み込む
                try:
                    extension_logger = base_extension_logger.getChild(file)
                    importlib.import_module("mikanassets.extension." + file + ".commands")
                    # コマンドを追加
                    tree.add_command(extension_commands_group)
                    sys_logger.info("read extension commands success -> " + now_path + "/mikanassets/extension/" + file + "/commands.py")
                except Exception as e:
                    sys_logger.info("cannot read extension commands " + now_path + "/mikanassets/extension/" + file + "/commands.py" + f"({e})")
            else:
                sys_logger.info("not exist extension commands file in " + now_path + "/mikanassets/extension/" + file + "/commands.py")
        else:
            sys_logger.info("not directory -> " + now_path + "/mikanassets/extension/" + file)

    unti_GC_obj.append(extension_commands_groups)

# mikanassets/extension/<extension_dir>にディレクトリが存在すれば
if os.path.exists(now_path + "/mikanassets/extension"):
    if len(os.listdir(now_path + "/mikanassets/extension")) > 0:
        # 拡張コマンドを読み込む
        read_extension_commands()
    else:
        sys_logger.info("no extension commands in " + now_path + "/mikanassets/extension")
del extension_commands_group


#--------------------


import traceback

#コマンドがエラーの場合
@tree.error
async def on_error(interaction: discord.Interaction, error: Exception):
    sys_logger.error(error)
    sys_logger.error(traceback.format_exc())
    await interaction.response.send_message(RESPONSE_MSG["error"]["error_base"] + str(error))

#--------------------


# flask関連コードの読み込み

#--------------------



app = Flask(__name__,template_folder="mikanassets/web",static_folder="mikanassets/web")
app.secret_key = flask_secret_key
flask_logger = create_logger("werkzeug",Formatter.FlaskFormatter(f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt),Formatter.FlaskConsoleFormatter('%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt))

class LogIPMiddleware:
    def __init__(self, app):
        self.app = app
        # self.before_log = {"Client IP": "", "Method": "", "URL": "", "Query": ""}

    def __call__(self, environ, start_response):
        # クライアントのIPアドレスを取得
        client_ip = environ.get('REMOTE_ADDR', '')
        # リクエストされたURLを取得
        request_method = environ.get('REQUEST_METHOD', '')
        request_uri = environ.get('PATH_INFO', '')
        query_string = environ.get('QUERY_STRING', '')

        # ログに記録
        if request_uri != "/get_console_data":
            flask_logger.info(f"Client IP: {client_ip}, Method: {request_method}, URL: {request_uri}, Query: {query_string}")

        return self.app(environ, start_response)

# ミドルウェアをアプリに適用
app.wsgi_app = LogIPMiddleware(app.wsgi_app)


# トークンをロードする
def load_tokens():
    tokens = set()
    try:
        items = web_tokens
        now = datetime.now()
        for token in items:
            if datetime.strptime(token["deadline"], "%Y-%m-%d %H:%M:%S") > now:
                tokens.add(token["token"])
        return tokens
    except FileNotFoundError:
        flask_logger.info(f"Token file not found: {WEB_TOKEN_FILE}")
        return {}

# トークンを検証する
def is_valid_token(token):
    tokens = load_tokens()
    return token in tokens

def is_valid_session(token):
    if 'token' not in session:
        # ログアウトにリダイレクトするためのフラグを返す
        return False
    if not is_valid_token(session['token']):
        #ログアウト
        # ログアウトにリダイレクトするためのフラグを返す
        return False
    return True


# クッキーからトークンを取得し、セッションにセット
@app.before_request
def load_token_from_cookie():
    token = request.cookies.get('token')
    if token and is_valid_token(token):
        session['token'] = token

@app.route('/', methods=['GET', 'POST'])
def index():
    # セッションにトークンがある場合、ログイン済み
    if 'token' in session:
        if is_valid_token(session['token']):
            return render_template('index.html', logs = log_msg)

    # ログアウトさせられた場合理由を表示
    if 'logout_reason' in session:
        flash(session['logout_reason'])
        session.pop('logout_reason') 

    if request.method == 'POST':
        token = request.form['token']
        if is_valid_token(token):
            # トークンをセッションとクッキーに保存
            session['token'] = token
            resp = make_response(redirect(url_for('index')))
            
            # クッキーにトークンを保存、有効期限を30日間に設定
            expires = datetime.now() + timedelta(days=30)
            resp.set_cookie('token', token, expires=expires)

            return resp
        else:
            flash('Invalid token, please try again.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # セッションとクッキーからトークンを削除してログアウト
    session.pop('token', None)
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('token', '', expires=0)  # クッキーを無効化
    return resp

# @app.route('/')
# def index():
#     return render_template('index.html', logs = log_msg)

@app.route('/get_console_data')
def get_console_data():
    if not is_valid_session(session['token']):
        # ログアウト
        session["logout_reason"] = "This token has expired. create new token."
        return jsonify({"redirect": url_for('logout')})
    
    converter = Ansi2HTMLConverter()
    html_string = converter.convert("\n".join(log_msg))

    try:
        server_online = process.poll() is None#サーバーが起動している = True
    except:
        if process is not None:
            process.kill()
        server_online = False

    bot_online = True

    return jsonify({"html_string": html_string, "online_status": {"server": server_online, "bot": bot_online}})


@app.route('/flask_start_server', methods=['POST'])
def flask_start_server():
    if not is_valid_session(session['token']):
        # ログアウト
        session["logout_reason"] = "This token has expired. create new token."
        return jsonify({"redirect": url_for('logout')})
    result = core_start()
    if result == RESPONSE_MSG["other"]["is_running"]:
        return jsonify(RESPONSE_MSG["other"]["is_running"])
    return jsonify(result)

@app.route('/flask_backup_server', methods=['POST'])
def flask_backup_server():
    if not is_valid_session(session['token']):
        # ログアウト
        session["logout_reason"] = "This token has expired. create new token."
        return jsonify({"redirect": url_for('logout')})
    world_name = request.form['fileName']
    if "\\" in world_name or "/" in world_name:
        return jsonify(RESPONSE_MSG["backup"]["not_allowed_path"] + ":" + server_path + world_name)
    if process is None:
        if os.path.exists(server_path + world_name):
            backup_logger.info("backup server")
            to = backup_path + "/" + datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
            copytree(server_path + world_name,to)
            backup_logger.info("backuped server to " + to)
            return jsonify("backuped server!! " + to)
        else:
            backup_logger.info('data not found : ' + server_path + world_name)
            return jsonify(RESPONSE_MSG["backup"]["data_not_found"] + ":" + server_path + world_name)
    else:
        return jsonify(RESPONSE_MSG["other"]["is_running"])

@app.route('/submit_data', methods=['POST'])
def submit_data():
    global use_stop
    if not is_valid_session(session['token']):
        # ログアウト
        session["logout_reason"] = "This token has expired. create new token."
        return jsonify({"redirect": url_for('logout')})
    user_input = request.form['userInput']
    #サーバーが起きてるかを確認
    if process is None:
        return jsonify("server is not running")
    #ifに引っかからない = サーバーが起動している

    #もし入力されたコマンドがstopだったら
    if user_input == STOP:
        use_stop = True

    #サーバーの標準入力に入力
    process.stdin.write(user_input + "\n")
    process.stdin.flush()

    # データを処理し、結果を返す（例: メッセージを返す）
    return jsonify(f"result: {user_input}")

def run_web():
    waitress.serve(app, host='0.0.0.0', port=web_port, _quiet=True)

    
if use_flask_server:
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
#--------------------


# discordロガーの設定

#--------------------


# discord.py用のロガーを取得して設定
discord_logger = logging.getLogger('discord')
if log["all"]:
    file_handler = logging.FileHandler(now_path + "/logs/all " + time + ".log")
    file_handler.setFormatter(file_formatter)
    discord_logger.addHandler(file_handler)
#--------------------



# 事実上のエントリポイント(client.runを実行)
client.run(token, log_formatter=console_formatter)
