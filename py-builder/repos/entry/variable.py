"""
処理に必要な定数を宣言する
"""
#!ignore
from .standard_imports import *
from .thirdparty_imports import *
#!end-ignore

__version__ = "2.4.11"

def get_version():
    return __version__


intents = discord.Intents.default() 
intents.message_content = True
client = discord.Client(intents=intents) 
tree = app_commands.CommandTree(client)



#プロンプトを送る
print()

#サーバープロセス
process = None

#起動した時刻
start_time = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

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
embed_thumbnail_url = "https://www.dropbox.com/scl/fi/a21ptajqddfkhilx1e4st/mi-2025.png?rlkey=29x0wvk1np17a3nvddth0jnyk&st=s6r4f2kr&dl=1"



# 権限データ
INITIAL_COMMAND_PERMISSION = {
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
    "backup create":1,
    "backup apply":3,
    # "replace":4,
    "ip":0,
    "logs":1,
    "permission view":0,
    "permission change":4,
    "lang":2,
    "tokengen":1,
    "terminal set":1,
    "terminal del":1,
    "update":3,
    "announce embed":4,
    "status":0,
}



unti_GC_obj = deque()

# 拡張機能から読み込むdiscord.tasks
extension_tasks_func = []
