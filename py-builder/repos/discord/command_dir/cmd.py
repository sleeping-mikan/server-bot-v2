#!ignore
from ...imports import *
from ...constant import *
from ...logger.logger_create import *
from ...minecraft.read_properties import *
from ...assets.text_dat import *
from ...assets.utils import *
#!end-ignore

# グループの設定
# root
command_group_cmd = app_commands.Group(name="cmd",description="cmd group")

@command_group_cmd.command(name="serverin",description=COMMAND_DESCRIPTION[lang]["cmd"]["serverin"])
async def cmd(interaction: discord.Interaction,command:str):
    await print_user(cmd_logger,interaction.user)
    global is_back_discord,cmd_logs
    #管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user): 
        await not_enough_permission(interaction,cmd_logger)
        return
    #サーバー起動確認
    if await is_stopped_server(interaction,cmd_logger): return
    #コマンドの利用許可確認
    if command.split()[0] not in allow_cmd:
        cmd_logger.error('unknown command : ' + command)
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["serverin"]["skipped_cmd"])
        return
    cmd_logger.info("run command : " + command)
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
        await interaction.response.send_message(cmd_logs.popleft())
        break

#サブグループstdinを作成
command_group_cmd_stdin = app_commands.Group(name="stdin",description="stdin group")
# サブグループを設定
command_group_cmd.add_command(command_group_cmd_stdin)


sys_files = [".config",".token","logs","mikanassets"]
important_bot_file = [
    os.path.abspath(os.path.join(os.path.dirname(__file__),i)) for i in sys_files
] 

# 操作可能なパスかを確認
async def is_path_within_scope(path):
    # 絶対パスを取得
    path = os.path.abspath(path)
    # server_path 以下にあるか確認
    if path.startswith(os.path.abspath(server_path)):
        return True
    cmd_logger.info("invalid path -> " + path + f"(server_path : {server_path})")
    return False

# 重要ファイルでないか(最高権限要求するようなファイルかを確認)
async def is_important_bot_file(path):
    # 絶対パスを取得
    path = os.path.abspath(path)
    # 重要ファイルの場合はTrueを返す
    for f in important_bot_file:
        if path.startswith(f):
            return True
    return False

# 以下のコマンドはserver_pathを起点としてそれ以下のファイルを操作する
# ファイル送信コマンドを追加
@command_group_cmd_stdin.command(name="mk",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mk"])
async def mk(interaction: discord.Interaction, file_path: str,file:discord.Attachment|None = None):
    await print_user(cmd_logger,interaction.user)
    # 管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user):
        await not_enough_permission(interaction,cmd_logger)
        return
    #サーバー起動確認
    if await is_running_server(interaction,cmd_logger): return
    # server_path + file_path にファイルを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not await is_path_within_scope(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        cmd_logger.info("invalid path -> " + file_path)
        return
    # ファイルがリンクであれば拒否
    if os.path.islink(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["mk"]["is_link"].format(file_path))
        cmd_logger.info("file is link -> " + file_path)
        return
    # ファイルをfile_pathに保存
    if file is not None:
        await file.save(file_path)
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if not await is_administrator(interaction.user) and await is_important_bot_file(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(file_path))
        cmd_logger.info("permission denied -> " + file_path)
        return
    else:
        # 空のファイルを作成
        open(file_path,"w").close()
    cmd_logger.info("create file -> " + file_path)
    await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["mk"]["success"].format(file_path))

@command_group_cmd_stdin.command(name="rm",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["rm"])
async def rm(interaction: discord.Interaction, file_path: str):
    await print_user(cmd_logger,interaction.user)
    # 管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user):
        await not_enough_permission(interaction,cmd_logger)
        return
    #サーバー起動確認
    if await is_running_server(interaction,cmd_logger): return
    # server_path + file_path のパスを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not await is_path_within_scope(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        cmd_logger.info("invalid path -> " + file_path)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["rm"]["file_not_found"].format(file_path))
        cmd_logger.info("file not found -> " + file_path)
        return
    # 該当のアイテムがファイルか
    if not os.path.isfile(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["not_file"].format(file_path))
        cmd_logger.info("not file -> " + file_path)
        return
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if not await is_administrator(interaction.user) and await is_important_bot_file(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(file_path))
        cmd_logger.info("permission denied -> " + file_path)
        return
    # ファイルを削除
    os.remove(file_path)
    cmd_logger.info("remove file -> " + file_path)
    await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["rm"]["success"].format(file_path))

@command_group_cmd_stdin.command(name="ls",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["ls"])
async def ls(interaction: discord.Interaction, file_path: str):
    await print_user(cmd_logger,interaction.user)
    # 管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user):
        await not_enough_permission(interaction,cmd_logger)
        return
    # server_path + file_path 閲覧パスの生成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not await is_path_within_scope(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        cmd_logger.info("invalid path -> " + file_path)
        return
    # 対象が存在するか
    if not os.path.exists(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["ls"]["file_not_found"].format(file_path))
        cmd_logger.info("file not found -> " + file_path)
        return
    # 対象がディレクトリであるか
    if not os.path.isdir(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["ls"]["not_directory"].format(file_path))
        cmd_logger.info("not directory -> " + file_path)
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
    cmd_logger.info("list directory -> " + file_path)
    if len(formatted_files) > 2000:
            with io.StringIO() as temp_file:
                temp_file.write("\n".join(files))
                temp_file.seek(0)
                # Discordファイルオブジェクトに変換して送信
                discord_file = discord.File(temp_file, filename="directory_list.txt")
                await interaction.response.send_message(
                    RESPONSE_MSG["cmd"]["stdin"]["ls"]["to_long"].format(file_path),
                    file=discord_file
                )
    else:
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["ls"]["success"].format(file_path,formatted_files))

@command_group_cmd_stdin.command(name="mkdir",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mkdir"])
async def mkdir(interaction: discord.Interaction, dir_path: str):
    await print_user(cmd_logger,interaction.user)
    # 管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user):
        await not_enough_permission(interaction,cmd_logger)
        return
    # server_path + file_path のパスを作成
    dir_path = os.path.abspath(os.path.join(server_path,dir_path))
    # 操作可能なパスか確認
    if not await is_path_within_scope(dir_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(dir_path))
        cmd_logger.info("invalid path -> " + dir_path)
        return
    # 既に存在するか確認
    if os.path.exists(dir_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["mkdir"]["exists"].format(dir_path))
        cmd_logger.info("directory already exists -> " + dir_path)
        return
    # ディレクトリを作成
    os.makedirs(dir_path)
    cmd_logger.info("create directory -> " + dir_path)
    await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["mkdir"]["success"].format(dir_path))

@command_group_cmd_stdin.command(name="rmdir",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["rmdir"])
async def rmdir(interaction: discord.Interaction, dir_path: str):
    await print_user(cmd_logger,interaction.user)
    # 管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user):
        await not_enough_permission(interaction,cmd_logger)
        return
    # server_path + file_path のパスを作成
    dir_path = os.path.abspath(os.path.join(server_path,dir_path))
    # 操作可能なパスか確認
    if not await is_path_within_scope(dir_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(dir_path))
        cmd_logger.info("invalid path -> " + dir_path)
        return
    # 既に存在するか確認
    if not os.path.exists(dir_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["rmdir"]["not_exists"].format(dir_path))
        cmd_logger.info("directory not exists -> " + dir_path)
        return
    # 全ての条件を満たすが、権限が足りず、対象が重要なディレクトリか確認
    if await is_important_bot_file(dir_path) and not await is_administrator(interaction.user):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(dir_path))
        cmd_logger.info("permission denied -> " + dir_path)
        return
    # ディレクトリを削除
    rmtree(dir_path)
    cmd_logger.info("remove directory -> " + dir_path)
    await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["rmdir"]["success"].format(dir_path))

# コマンドを追加
tree.add_command(command_group_cmd)