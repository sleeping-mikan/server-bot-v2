"""
ロガーの作成および設定を行う
"""
#!ignore
from ..imports import *
from ..constant import *
from ..logger.logger_formatter import *
from ..config.read_config_minimum import *
#!end-ignore

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
send_logger = create_logger("send")
minecraft_logger = create_logger("minecraft",Formatter.MinecraftFormatter(f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt),Formatter.MinecraftConsoleFormatter('%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt))
