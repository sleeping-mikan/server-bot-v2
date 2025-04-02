#!ignore
from .common import *
#!end-ignore

stdin_rm_logger = stdin_logger.getChild("rm")

@command_group_cmd_stdin.command(name="rm",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["rm"])
async def rm(interaction: discord.Interaction, file_path: str):
    await print_user(stdin_rm_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title=f"/cmd stdin rm {file_path}")
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin rm"]:
        await not_enough_permission(interaction,stdin_rm_logger)
        return
    #サーバー起動確認
    if is_running_server(stdin_rm_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # server_path + file_path のパスを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rm_logger.info("invalid path -> " + file_path)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["rm"]["file_not_found"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rm_logger.info("file not found -> " + file_path)
        return
    # 該当のアイテムがファイルか
    if not os.path.isfile(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["not_file"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rm_logger.info("not file -> " + file_path)
        return
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if (not await is_administrator(interaction.user) or not enable_advanced_features) and await is_important_bot_file(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_rm_logger.info("permission denied -> " + file_path)
        return
    # ファイルを削除
    os.remove(file_path)
    stdin_rm_logger.info("remove file -> " + file_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["rm"]["success"].format(file_path),inline=False)
    await interaction.response.send_message(embed=embed)
