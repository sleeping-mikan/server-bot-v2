#!ignore
from ...imports import *
from ...constant import *
from ...logger.logger_create import *
from ...assets.text_dat import *
from ...assets.utils import *
from ...minecraft.read_properties import *
from ...files.create import *
#!end-ignore

#start
@tree.command(name="start",description=COMMAND_DESCRIPTION[lang]["start"])
async def start(interaction: discord.Interaction):
    await print_user(start_logger,interaction.user)
    if await user_permission(interaction.user) < COMMAND_PERMISSION["start"]: 
        await not_enough_permission(interaction,start_logger)
        return
    global process
    if await is_running_server(interaction,start_logger): return
    start_logger.info('server starting')
    process = subprocess.Popen([server_path + server_name],cwd=server_path,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,encoding="utf-8")
    await interaction.response.send_message(RESPONSE_MSG["start"]["success"])
    threading.Thread(target=server_logger,args=(process,deque())).start()
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
    #サーバー起動確認
    if await is_stopped_server(interaction,stop_logger): return
    use_stop = True
    stop_logger.info('server stopping')
    await interaction.response.send_message(RESPONSE_MSG["stop"]["success"])
    process.stdin.write(STOP + "\n")
    process.stdin.flush()
    await client.change_presence(activity=discord.Game(ACTIVITY_NAME["ending"])) 
    while True:
        #終了するまで待つ
        if process is None:
            await client.change_presence(activity=discord.Game(ACTIVITY_NAME["ended"])) 
            break
        await asyncio.sleep(1)

#!open ./repos/discord/command/permission.py
#!ignore
from .permission import *
#!end-ignore


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
    await interaction.response.send_message(RESPONSE_MSG["lang"]["success"].format(language))
    lang_logger.info("change lang to " + lang)

#/cmd serverin <server command>
#/cmd stdin 

#!open ./repos/discord/command/cmd.py
#!ignore
from .cmd import *
#!end-ignore

#/backup()
@tree.command(name="backup",description=COMMAND_DESCRIPTION[lang]["backup"])
async def backup(interaction: discord.Interaction,world_name:str = "worlds"):
    await print_user(backup_logger,interaction.user)
    global exist_files, copyed_files
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["backup"]:
        await not_enough_permission(interaction,backup_logger) 
        return
    #サーバー起動確認
    if await is_running_server(interaction,backup_logger): return
    backup_logger.info('backup started')
    #server_path + world_namの存在確認
    if os.path.exists(server_path + world_name):
        await interaction.response.send_message("progress...\n")
        # discordにcopyed_files / exist_filesをプログレスバーで
        await dircp_discord(server_path + world_name,backup_path + "/",interaction)
        backup_logger.info('backup done')
    else:
        backup_logger.error('data not found : ' + server_path + world_name)
        await interaction.response.send_message(RESPONSE_MSG["backup"]["data_not_found"] + ":" + server_path + world_name)

#/replace <py file>
@tree.command(name="replace",description=COMMAND_DESCRIPTION[lang]["replace"])
async def replace(interaction: discord.Interaction,py_file:discord.Attachment):
    await print_user(replace_logger,interaction.user)
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["replace"]:
        await not_enough_permission(interaction,replace_logger)
        return
    #サーバー起動確認
    if await is_running_server(interaction,replace_logger): return
    replace_logger.info('replace started')
    # ファイルをすべて読み込む
    with open(temp_path + "/new_source.py","w",encoding="utf-8") as f:
        f.write((await py_file.read()).decode("utf-8").replace("\r\n","\n"))
    # discordにコードを置き換える
    replace_logger.info('replace done')
    await interaction.response.send_message(RESPONSE_MSG["replace"]["progress"])
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
    if await user_permission(interaction.user) < COMMAND_PERMISSION["ip"]:
        await not_enough_permission(interaction,ip_logger)
        return
    if not allow["ip"]:
        await interaction.response.send_message(RESPONSE_MSG["ip"]["not_allow"])
        ip_logger.error('ip is not allowed')
        return
    # ipをget
    try:
        addr = requests.get("https://api.ipify.org")
    except:
        ip_logger.error('get ip failed')
        await interaction.response.send_message(RESPONSE_MSG["ip"]["get_ip_failed"])
        return
    if config["mc"]:
        ip_logger.info('get ip : ' + addr.text + ":" + properties["server-port"])
        await interaction.response.send_message(RESPONSE_MSG["ip"]["msg_startwith"] + addr.text + ":" + properties["server-port"] + "\n" + f"(ip:{addr.text} port(ポート):{properties['server-port']})")
    else:
        ip_logger.info('get ip : ' + addr.text)
        await interaction.response.send_message(RESPONSE_MSG["ip"]["msg_startwith"] + addr.text)


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
            if send_length < 1900:
                send_msg.append(i)
            else:
                break
        await interaction.response.send_message("```ansi\n" + "\n".join(send_msg) + "\n```")
    else:
        if "/" in filename or "\\" in filename or "%" in filename:
            log_logger.error('invalid filename : ' + filename + "\n" + f"interaction user / id：{interaction.user} {interaction.user.id}")
            await interaction.response.send_message(RESPONSE_MSG["logs"]["cant_access_other_dir"])
            return
        elif not filename.endswith(".log"):
            log_logger.error('invalid filename : ' + filename + "\n" + f"interaction user / id：{interaction.user} {interaction.user.id}")
            await interaction.response.send_message(RESPONSE_MSG["logs"]["not_found"])
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
                    await interaction.response.send_message(RESPONSE_MSG["logs"]["not_found"])
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
    #権限レベルを確認
    if await user_permission(interaction.user) < COMMAND_PERMISSION["tokengen"]:
        await not_enough_permission(interaction,token_logger)
        return
    new_token = gen_web_token()
    await interaction.response.send_message(RESPONSE_MSG["tokengen"]["success"].format(new_token),ephemeral=True)
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
    await interaction.response.send_message(RESPONSE_MSG["terminal"]["success"].format(where_terminal))


#/help
@tree.command(name="help",description=COMMAND_DESCRIPTION[lang]["help"])
async def help(interaction: discord.Interaction):
    await print_user(help_logger,interaction.user)
    await interaction.response.send_message(send_help)
    help_logger.info('help sent')

#/exit
@tree.command(name="exit",description=COMMAND_DESCRIPTION[lang]["exit"])
async def exit(interaction: discord.Interaction):
    await print_user(exit_logger,interaction.user)
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["exit"]: 
        await not_enough_permission(interaction,exit_logger)
        return
    #サーバが動いているなら終了
    if await is_running_server(interaction,exit_logger): return
    await interaction.response.send_message(RESPONSE_MSG["exit"]["success"])
    exit_logger.info('exit')
    await client.close()
    #waitressサーバーを終了

    sys.exit()

# 拡張コマンドを読み込む
#!open ./repos/discord/command/extension/read.py



#コマンドがエラーの場合
@tree.error
async def on_error(interaction: discord.Interaction, error: Exception):
    sys_logger.error(error)
    await interaction.response.send_message(RESPONSE_MSG["error"]["error_base"] + str(error))
