#!ignore
from ..imports import *
from ..constant import *
from ..logger.logger_create import *
from ..config.read_config_minimum import *
from ..config.read_config_all import *
#!end-ignore


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
            "replace":"このbotのコードを<py file>に置き換えます。このコマンドはbotを破壊する可能性があります。",
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
            "replace":"Replace the bot's code with <py file>.",
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
                "serverin":{
                    "skipped_cmd":"コマンドが存在しない、または許可されないコマンドです",
                },
                "stdin":{
                    "invalid_path": "パス`{}`は不正/操作不可能な領域です",
                    "not_file": "`{}`はファイルではありません",
                    "permission_denied":"`{}`を操作する権限がありません",
                    "file_size_limit":"サイズ`{}`は制限`{}`を超えている可能性があるためFile.ioにアップロードします\nアップロード後に再度メンションで通知します",
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
                        "file_io_error":"<@{}> File.ioへのアップロードに失敗しました",
                        "file_not_found":"`{}`は見つかりません",
                        "not_file":"`{}`はファイルではありません",
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
                "serverin":{
                    "skipped_cmd":"The command is not found or not allowed",
                },
                "stdin":{
                    "invalid_path": "`{}` is an invalid/operable area",
                    "not_file": "`{}` is not a file",
                    "permission_denied": "`{}` cannot be modified because it is an important file",
                    "file_size_limit": "Upload to File.io because the file size of `{}` is over the limit of {} bytes\nmention to you if ended",
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
                        "file_io_error":"<@{}> File.io upload failed",
                        "not_file":"`{}` is not a file",
                        "file_not_found":"`{}` not found",
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
