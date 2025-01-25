#!ignore
from ....imports import *
from ....constant import *
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
from .common import *
#!end-ignore

terminal_delete_logger = terminal_logger.getChild("delete")

#/terminal
@command_group_terminal.command(name="del",description=COMMAND_DESCRIPTION[lang]["terminal"]["set"])
async def terminal_set(interaction: discord.Interaction):
    global where_terminal
    await print_user(terminal_delete_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/terminal del")
    # 権限レベルが足りていないなら
    if await user_permission(interaction.user) < COMMAND_PERMISSION["terminal del"]:
        await not_enough_permission(interaction,terminal_delete_logger)
        return
    #発言したチャンネルをwhere_terminalに登録
    await change_terminal_ch(False, terminal_delete_logger)
    embed.add_field(name="",value=RESPONSE_MSG["terminal"]["success"].format(where_terminal),inline=False)
    await interaction.response.send_message(embed=embed)
