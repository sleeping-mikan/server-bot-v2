#!ignore
from .common import *
#!end-ignore


stdin_ls_logger = stdin_logger.getChild("ls")
@command_group_cmd_stdin.command(name="ls",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["ls"])
async def ls(interaction: discord.Interaction, file_path: str):
    await print_user(stdin_ls_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/cmd stdin ls {file_path}")
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
    if len(formatted_files) > 900:
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
