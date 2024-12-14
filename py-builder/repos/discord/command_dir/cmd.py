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

async def is_valid_path(path):
    # 絶対パスを取得
    path = os.path.abspath(path)
    # server_path 以下にあるか確認
    if path.startswith(os.path.abspath(server_path)):
        return True
    sys_logger.info("invalid path : " + path + f"(server_path : {server_path})")
    return False

# 以下のコマンドはserver_pathを起点としてそれ以下のファイルを操作する
# ファイル送信コマンドを追加
@command_group_cmd_stdin.command(name="mk",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mk"])
async def mk(interaction: discord.Interaction, file_path: str,file:discord.Attachment|None = None):
    # 管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user):
        await not_enough_permission(interaction,cmd_logger)
        return
    #サーバー起動確認
    if await is_running_server(interaction,cmd_logger): return
    # server_path + file_path にファイルを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    sys_logger.info(server_path)
    # 操作可能なパスか確認
    if not await is_valid_path(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        return
    # ファイルがリンクであれば拒否
    if os.path.islink(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["mk"]["is_link"].format(file_path))
        return
    # ファイルをfile_pathに保存
    if file is not None:
        await file.save(file_path)
    else:
        # 空のファイルを作成
        open(file_path,"w").close()
    await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["mk"]["success"].format(file_path))

@command_group_cmd_stdin.command(name="rm",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["rm"])
async def rm(interaction: discord.Interaction, file_path: str):
    # 管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user):
        await not_enough_permission(interaction,cmd_logger)
        return
    #サーバー起動確認
    if await is_running_server(interaction,cmd_logger): return
    # server_path + file_path のパスを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not await is_valid_path(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["rm"]["file_not_found"].format(file_path))
        return
    # 該当のアイテムがファイルか
    if not os.path.isfile(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["not_file"].format(file_path))
        return
    # ファイルを削除
    os.remove(file_path)
    await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["rm"]["success"].format(file_path))

@command_group_cmd_stdin.command(name="ls",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["ls"])
async def ls(interaction: discord.Interaction, file_path: str):
    # 管理者権限を要求
    if not await is_administrator(interaction.user) and not await is_force_administrator(interaction.user):
        await not_enough_permission(interaction,cmd_logger)
        return
    # server_path + file_path 閲覧パスの生成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not await is_valid_path(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        return
    # 対象が存在するか
    if not os.path.exists(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["ls"]["file_not_found"].format(file_path))
        return
    # 対象がディレクトリであるか
    if not os.path.isdir(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["ls"]["not_directory"].format(file_path))
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


# コマンドを追加
tree.add_command(command_group_cmd)