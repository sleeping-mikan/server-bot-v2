#!ignore
from ..imports import *
from ..constant import *
from ..logger.logger_create import *
from ..config.read_config_minimum import *
from ..config.read_config_all import *
#!end-ignore

# 権限データ
COMMAND_PERMISSION = {
    "/stop       ":1,
    "/start      ":1,
    "/exit       ":1,
    "/cmd        ":1,
    "/help       ":0,
    "/backup     ":1,
    "/replace    ":2,
    "/ip         ":0,
    "/logs       ":1,
    "/force_admin":2,
    "/permission ":0,
    "/lang       ":2,
    "/tokengen   ":1,
    "/terminal   ":1,
}

async def get_text_dat():
    global HELP_MSG, COMMAND_DESCRIPTION, send_help, RESPONSE_MSG, ACTIVITY_NAME 
# テキストデータ領域-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#help
    HELP_MSG = {
        "ja":{
            "/stop       ":"サーバーを停止します。但し起動していない場合にはエラーメッセージを返します。",
            "/start      ":"サーバーを起動します。但し起動している場合にはエラーメッセージを返します。",
            "/exit       ":"botを終了します。サーバーを停止してから実行してください。終了していない場合にはエラーメッセージを返します。\nまたこのコマンドを実行した場合次にbotが起動するまですべてのコマンドが無効になります。",
            "/cmd        ":f"/cmd <mcコマンド> を用いてサーバーコンソール上でコマンドを実行できます。使用できるコマンドは{allow_cmd}です。",
            "/backup     ":"/backup [ワールド名] でワールドデータをバックアップします。ワールド名を省略した場合worldsをコピーします。サーバーを停止した状態で実行してください",
            "/replace    ":"/replace <py file> によってbotのコードを置き換えます。",
            "/ip         ":"サーバーのIPアドレスを表示します。",
            "/logs       ":"サーバーのログを表示します。引数を与えた場合にはそのファイルを、与えられなければ動作中に得られたログから最新の10件を返します。",
            "/force_admin":"/force_admin <add/remove> <user> で、userのbot操作権利を付与/剥奪することができます。",
            "/permission ":"/permission <user> で、userのbot操作権利を表示します。",
            "/lang       ":"/lang <lang> で、botの言語を変更します。",
            "/tokengen   ":"/tokengen で、webでログインするためのトークンを生成します。",
            "/terminal   ":"/terminal で、サーバーのコンソールを実行したチャンネルに紐づけます。",
        },
        "en":{
            "/stop       ":"Stop the server. If the server is not running, an error message will be returned.",
            "/start      ":"Start the server. If the server is running, an error message will be returned.",
            "/exit       ":"Exit the bot. Stop the server first and then run the command. If the server is not running, an error message will be returned.\n",
            "/cmd        ":f"/cmd <mc command> can be used to execute commands in the server console. The available commands are {allow_cmd}.",
            "/backup     ":"/backup [world name] copies the world data. If no world name is given, the worlds will be copied.",
            "/replace    ":"/replace <py file> replaces the bot's code.",
            "/ip         ":"The server's IP address will be displayed to discord.",
            "/logs       ":"Display the server's logs. If an argument is given, that file will be returned. If no argument is given, the latest 10 logs will be returned.",
            "/force_admin":"/force_admin <add/remove> <user> gives or removes user's bot operation rights.",
            "/permission ":"/permission <user> displays the user's bot operation rights.",
            "/lang       ":"/lang <lang> changes the bot's language.",
            "/tokengen   ":"/tokengen generates a token for login to the web.",
            "/terminal   ":"/terminal connects the server's console to a channel.",
        },
    }
        

    COMMAND_DESCRIPTION = {
        "ja":{
            "stop":"サーバーを停止します。",
            "start":"サーバーを起動します。",
            "exit":"botを終了します。",
            "cmd":"サーバーにマインクラフトコマンドを送信します。",
            "backup":"ワールドデータをバックアップします。引数にはワールドファイルの名前を指定します。入力しない場合worldsが選択されます。",
            "replace":"このbotのコードを<py file>に置き換えます。このコマンドはbotを破壊する可能性があります。",
            "ip":"サーバーのIPアドレスを表示します。",
            "logs":"サーバーのログを表示します。引数にはファイル名を指定します。入力しない場合は最新の10件のログを返します。",
            "help":"このbotのコマンド一覧を表示します。",
            "admin":{
                "force":"選択したユーザに対してbotをdiscord管理者と同等の権限で操作できるようにします。",
            },
            "permission":"選択したユーザに対してbot操作権限を表示します。",
            "lang":"botの言語を変更します。引数には言語コードを指定します。",
            "tokengen":"webにログインするためのトークンを生成します。",
            "terminal":"サーバーのコンソールを実行したチャンネルに紐づけます。",
        },
        "en":{
            "stop":"Stop the server.",
            "start":"Start the server.",
            "exit":"Exit the bot.",
            "cmd":"Send a Minecraft command to the server.",
            "backup":"Copy the world data. If no argument is given, the worlds will be copied.",
            "replace":"Replace the bot's code with <py file>.",
            "ip":"The server's IP address will be displayed to discord.",
            "logs":"Display server logs. With an argument, return that file. Without, return the latest 10 logs.",
            "help":"Display this bot's command list.",
            "admin":{
                "force":"Force the selected user to have the same permissions as the bot, as discord administrator.",
            },
            "permission":"Display the bot operation rights of the selected user.",
            "lang":"Change the bot's language. With an argument, specify the language code.",
            "tokengen":"Generate a token for login to the web.",
            "terminal":"Connect the server's console to a channel.",
        },
    }

    #今後も大きくなることが予想されるので、ここで条件分岐する
    if lang == "ja":
        send_help = "詳細なHelpはこちらを参照してください\n<https://github.com/mikatan-mikan/server-bot/blob/main/README.md#%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89%E4%B8%80%E8%A6%A7>\n"
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
                "skipped_cmd":"コマンドが存在しない、または許可されないコマンドです",
            },
            "backup":{
                "now_backup":"バックアップ中・・・",
                "data_not_found":"データが見つかりません",
                "success":"バックアップが完了しました！",
            },
            "replace":{
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
            "admin":{
                "force":{
                    "already_added":"このユーザーはすでにbotの管理者権限を持っています",
                    "add_success":"{}にbotの管理者権限を与えました",
                    "remove_success":"{}からbotの管理者権限を剥奪しました",
                    "already_removed":"このユーザーはbotの管理者権限を持っていません",
                },
            },
            "permission":{
                "success":"{} の権限 : \ndiscord管理者権限 : {}\nbot管理者権限 : {}",
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
        }
        ACTIVITY_NAME = {
            "starting":"さーばーきどう",
            "running":"さーばーじっこう",
            "ending":"さーばーおしまい",
            "ended":"さーばーとじてる",
        }
    elif lang == "en":
        send_help = "Details on the help can be found here\n<https://github.com/mikatan-mikan/server-bot/blob/main/README.md#%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89%E4%B8%80%E8%A6%A7>\n"
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
                "skipped_cmd":"The command is not found or not allowed",
            },
            "backup":{
                "now_backup":"Backup in progress",
                "data_not_found":"Data not found",
                "success":"Backup complete!",
            },
            "replace":{
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
            "admin":{
                "force":{
                    "already_added":"The user has already been added as an administrator",
                    "add_success":"Added as an administrator to {}",
                    "already_removed":"The user has already been removed as an administrator",
                    "remove_success":"Removed as an administrator from {}",
                },
            },
            "permission":{
                "success":"{}'s permission : \ndiscord administrator permission : {}\nbot administrator permission : {}",
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
        send_help += "```"
        for key in HELP_MSG[lang]:
            send_help += key + " " + HELP_MSG[lang][key] + "\n"
        send_help += "```"
    make_send_help()


get_text = asyncio.run(get_text_dat())
sys_logger.info('create text data')