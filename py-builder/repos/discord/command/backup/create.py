#!ignore
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
from ....constant import *
from ..cmd.stdin.common import *
from .common import *
#!end-ignore

backup_create_logger = backup_logger.getChild("create")

#/backup()
@command_group_backup.command(name="create",description=COMMAND_DESCRIPTION[lang]["backup"]["create"])
async def backup(interaction: discord.Interaction,path:str = "worlds"):
    from_backup = normalize_path(os.path.join(server_path,path))
    world_name = path
    await print_user(backup_logger,interaction.user)
    global exist_files, copyed_files
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/backup create {world_name}")
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["backup create"]:
        await not_enough_permission(interaction,backup_logger) 
        return
    #サーバー起動確認
    if is_running_server(backup_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # 操作可能パスかを判定
    if not is_path_within_scope(from_backup) or await is_important_bot_file(from_backup):
        backup_logger.error("path not allowed : " + from_backup)
        embed.add_field(name="",value = RESPONSE_MSG["backup"]["create"]["path_not_allowed"] + ":" + from_backup,inline=False)
        await interaction.response.send_message(embed=embed)
        return
    backup_logger.info('backup started')
    #server_path + world_namの存在確認
    if os.path.exists(from_backup):
        await interaction.response.send_message(embed=embed)
        # discordにcopyed_files / exist_filesをプログレスバーで
        await dircp_discord(from_backup,backup_path + "/",interaction,embed)
        backup_logger.info('backup done')
    else:
        backup_logger.error('data not found : ' + from_backup)
        embed.add_field(name="",value=RESPONSE_MSG["backup"]["create"]["data_not_found"] + ":" + from_backup,inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)