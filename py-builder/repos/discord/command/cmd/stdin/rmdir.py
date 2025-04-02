#!ignore
from .common import *
#!end-ignore

stdin_rmdir_logger = stdin_logger.getChild("rmdir")

@command_group_cmd_stdin.command(name="rmdir",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["rmdir"])
async def rmdir(interaction: discord.Interaction, dir_path: str):
    await print_user(stdin_rmdir_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/cmd stdin rmdir {dir_path}")
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin rmdir"]:
        await not_enough_permission(interaction,stdin_rmdir_logger)
        return
    #サーバー起動確認
    if is_running_server(stdin_rmdir_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # server_path + file_path のパスを作成
    dir_path = os.path.abspath(os.path.join(server_path,dir_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(dir_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rmdir_logger.info("invalid path -> " + dir_path)
        return
    # 既に存在するか確認
    if not os.path.exists(dir_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["rmdir"]["not_exists"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rmdir_logger.info("directory not exists -> " + dir_path)
        return
    # 全ての条件を満たすが、権限が足りず、対象が重要なディレクトリか確認
    if await is_important_bot_file(dir_path) and (not enable_advanced_features or (not await is_administrator(interaction.user))):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rmdir_logger.info("permission denied -> " + dir_path)
        return
    # ディレクトリを削除
    rmtree(dir_path)
    stdin_rmdir_logger.info("remove directory -> " + dir_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["rmdir"]["success"].format(dir_path),inline=False)
    await interaction.response.send_message(embed=embed)
