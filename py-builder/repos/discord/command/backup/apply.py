#!ignore
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
from ..cmd.stdin.common import *
from .common import *
#!end-ignore


backup_apply_logger = backup_logger.getChild("apply")

async def server_backup_list(interaction: discord.Interaction, current: str):
    current = current.translate(str.maketrans("/\\:","--_"))
    #全てのファイルを取得
    backups = os.listdir(backup_path)
    # current と一致するものを返す & logファイル & 25個制限を実装
    logfiles = [i for i in backups if current in i][-25:]
    # open("./tmp.txt","w").write("\n".join(logfiles))
    return [
        app_commands.Choice(name = i,value = i) for i in logfiles
    ]

@command_group_backup.command(name="apply",description="apply backup")
@app_commands.autocomplete(witch=server_backup_list)
async def backup_apply(interaction:discord.Interaction, witch:str, path:str = ""):
    await print_user(backup_apply_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/backup apply {witch} {path}")
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["backup apply"]: 
        await not_enough_permission(interaction,backup_apply_logger)
        return
    #サーバー起動確認
    if is_running_server(backup_apply_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # dirの存在確認
    if not os.path.exists(os.path.join(server_path,path)):
        backup_apply_logger.error('data not found : ' + os.path.join(server_path,path))
        embed.add_field(name="",value = RESPONSE_MSG["backup"]["apply"]["path_not_found"] + ":" + os.path.join(server_path,path),inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # 操作可能パスかを判定
    if not is_path_within_scope(os.path.join(server_path,path)) or await is_important_bot_file(os.path.join(server_path,path)):
        backup_logger.error("path not allowed : " + os.path.join(server_path,path))
        embed.add_field(name="",value = RESPONSE_MSG["backup"]["apply"]["path_not_allowed"] + ":" + os.path.join(server_path,path),inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # 移動先がdirectoryか
    if not os.path.isdir(os.path.join(server_path,path)):
        backup_logger.error("path not directory : " + os.path.join(server_path,path))
        embed.add_field(name="",value = RESPONSE_MSG["backup"]["apply"]["path_not_directory"] + ":" + os.path.join(server_path,path),inline=False)
        await interaction.response.send_message(embed=embed)
        return
    backup_apply_logger.info('backup apply started' + " -> " + witch + " to " + os.path.join(server_path,path,witch))
    await interaction.response.send_message(embed=embed)
    # dircp_discordを用いて進捗を出しつつ、コピーする
    await dircp_discord(os.path.join(backup_path,witch),os.path.join(server_path,path),interaction,embed)
    backup_apply_logger.info('backup apply done')
    