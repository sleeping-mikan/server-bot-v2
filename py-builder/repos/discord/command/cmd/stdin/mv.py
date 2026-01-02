#!ignore
from .common import *
#!end-ignore

stdin_mv_logger = stdin_logger.getChild("mv")

@command_group_cmd_stdin.command(name="mv",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mv"])
async def cmd_stdin_mv(interaction: discord.Interaction, path: str, dest: str):
    await print_user(stdin_mv_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/cmd stdin mv {path} {dest} ")
    # 権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin mv"]:
        await not_enough_permission(interaction,stdin_mv_logger)
        return
    #サーバー起動確認
    if is_running_server(stdin_mv_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("server is running")
        return
    # server_path + path のパスを作成
    path = os.path.abspath(os.path.join(server_path,path))
    # server_path + dest のパスを作成
    dest = os.path.abspath(os.path.join(server_path,dest))
    # 操作可能なパスか確認
    if not is_path_within_scope(path) or not is_path_within_scope(dest):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(path,dest),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("invalid path -> " + path + " or " + dest)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mv"]["file_not_found"].format(path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("file not found -> " + path)
        return
    # 該当のアイテムがファイルかディレクトリ
    if not os.path.isfile(path) and not os.path.isdir(path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["not_file_or_directory"].format(path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("not file -> " + path)
        return
    # 移動先がディレクトリではない
    if not os.path.isdir(os.path.dirname(dest)):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["not_directory"].format(dest),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("not directory -> " + dest)
        return
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if (not await is_administrator(interaction.user) or not enable_advanced_features) and (await is_important_bot_file(path) or await is_important_bot_file(dest)):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mv_logger.info("permission denied -> " + path + " or " + dest)
        return
    # ファイルを移動
    shutil_move(path,dest)
    stdin_mv_logger.info("move file -> " + path + " -> " + dest)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mv"]["success"].format(path,dest),inline=False)
    await interaction.response.send_message(embed=embed)