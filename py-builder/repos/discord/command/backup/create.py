#!ignore
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
from .common import *
#!end-ignore

backup_create_logger = backup_logger.getChild("create")

#/backup()
@command_group_backup.command(name="create",description=COMMAND_DESCRIPTION[lang]["backup"]["create"])
async def backup(interaction: discord.Interaction,path:str = "worlds"):
    global exist_files, copyed_files
    await print_user(backup_logger,interaction.user)
    backup_path = os.path.join(server_path,path)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/backup {path}")
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
    if not is_path_within_scope(backup_path):
        backup_logger.error("path not allowed : " + backup_path)
        embed.add_field(name="",value = RESPONSE_MSG["backup"]["create"]["path_not_allowed"] + ":" + backup_path,inline=False)
        await interaction.response.send_message(embed=embed)
        return
    backup_logger.info('backup started')
    #server_path + world_nameの存在確認
    if os.path.exists(backup_path):
        await interaction.response.send_message(embed=embed)
        # discordにcopyed_files / exist_filesをプログレスバーで
        await dircp_discord(backup_path,backup_path + "/",interaction,embed)
        backup_logger.info('backup done')
    else:
        backup_logger.error('data not found : ' + backup_path)
        embed.add_field(name="",value=RESPONSE_MSG["backup"]["create"]["data_not_found"] + ":" + backup_path,inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)