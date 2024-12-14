"""
処理に必要な定数を宣言する
"""
#!ignore
from .imports import *
#!end-ignore


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