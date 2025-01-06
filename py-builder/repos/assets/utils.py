#!ignore
from ..imports import *
from ..constant import *
from ..config.read_config_minimum import *
from .text_dat import *
#!end-ignore

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


async def dircp_discord(src, dst, interaction: discord.Interaction, symlinks=False) -> None:
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
                        await interaction.edit_original_response(content=f"{now}\n```{int((copyed_files / exist_files * bar_width) - 1) * '='}☆{((bar_width) - int(copyed_files / exist_files * bar_width)) * '-'}  ({'{: 5}'.format(copyed_files)} / {'{: 5}'.format(exist_files)}) {'{: 3.3f}'.format(copyed_files / exist_files * 100)}%```")
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