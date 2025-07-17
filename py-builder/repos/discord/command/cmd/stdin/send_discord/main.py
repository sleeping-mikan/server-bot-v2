#!ignore
from ..common import *
from .fileio import *
from .selfserver import *
from ._header import *
#!end-ignore

@command_group_cmd_stdin.command(name="send-discord",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["send-discord"])
async def send_discord(interaction: discord.Interaction, path: str):
    await print_user(stdin_send_discord_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/cmd stdin send-discord {path}")
    file_path = os.path.abspath(os.path.join(server_path,path))  # ファイルのパス
    file_name = os.path.basename(file_path)
    file_size_limit = 9 * 1024 * 1024  # 9MB
    file_size_limit_web = send_discord_bits_capacity  # 2GBを超えた場合file.ioでも無理なのでエラー
    # 権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin send-discord"]:
        await not_enough_permission(interaction,stdin_send_discord_logger)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_not_found"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_send_discord_logger.info("file not found -> " + file_path)
        return
    # パスが許可されているかを確認 or .tokenなら常に拒否
    if not is_path_within_scope(file_path) or os.path.basename(file_path) == ".token":
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_send_discord_logger.info("invalid path -> " + file_path)
        return
    # if send_discord_mode == "fileio":
    #     await send_discord_fileio(interaction, embed, stdin_send_discord_logger, file_size_limit_web, file_size_limit,file_path, file_name)
    link = await SendDiscordSelfServer.register_download(file_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["send_myserver_link"].format(interaction.user.id, link, file_path),inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)