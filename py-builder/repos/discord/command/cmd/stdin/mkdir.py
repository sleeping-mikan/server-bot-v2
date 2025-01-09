#!ignore
from .common import *
#!end-ignore

stdin_mkdir_logger = stdin_logger.getChild("mkdir")

@command_group_cmd_stdin.command(name="mkdir",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mkdir"])
async def mkdir(interaction: discord.Interaction, dir_path: str):
    await print_user(stdin_mkdir_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/cmd stdin mkdir {dir_path}")
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin mkdir"]:
        await not_enough_permission(interaction,stdin_mkdir_logger)
        return
    # server_path + file_path のパスを作成
    dir_path = os.path.abspath(os.path.join(server_path,dir_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(dir_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mkdir_logger.info("invalid path -> " + dir_path)
        return
    # 既に存在するか確認
    if os.path.exists(dir_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mkdir"]["exists"].format(dir_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mkdir_logger.info("directory already exists -> " + dir_path)
        return
    # ディレクトリを作成
    os.makedirs(dir_path)
    stdin_mkdir_logger.info("create directory -> " + dir_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mkdir"]["success"].format(dir_path),inline=False)
    await interaction.response.send_message(embed=embed)
