#!ignore
from ....constant import *
from ....assets.text_dat import *
from ....assets.utils import *
from ....config.read_config_all import *
#!end-ignore

#/update
@tree.command(name="update",description=COMMAND_DESCRIPTION[lang]["update"])
async def update(interaction: discord.Interaction, is_force: bool = False):
    await print_user(update_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/update")
    embed.set_image(url = embed_under_line_url)
    #サーバー起動確認
    if is_running_server(update_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    #サーバー管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["update"]: 
        await not_enough_permission(interaction,update_logger)
        return
    #py_builder.pyを更新
    await update_self_if_commit_changed(interaction=interaction,embed=embed,text_pack=RESPONSE_MSG["update"],sender=send_discord_message_or_edit,is_force = is_force)