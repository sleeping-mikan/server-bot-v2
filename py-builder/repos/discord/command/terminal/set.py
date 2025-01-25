#!ignore
from ....imports import *
from ....constant import *
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
from .common import *
#!end-ignore

terminal_set_logger = terminal_logger.getChild("set")

#/terminal
@command_group_terminal.command(name="set",description=COMMAND_DESCRIPTION[lang]["terminal"])
async def terminal_set(interaction: discord.Interaction, channel:discord.TextChannel = None):
    global where_terminal
    await print_user(terminal_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/terminal set {channel}")
    # 権限レベルが足りていないなら
    if await user_permission(interaction.user) < COMMAND_PERMISSION["terminal"]:
        await not_enough_permission(interaction,terminal_logger)
        return
    #発言したチャンネルをwhere_terminalに登録
    await change_terminal_ch(channel.id)
    embed.add_field(name="",value=RESPONSE_MSG["terminal"]["success"].format(where_terminal),inline=False)
    await interaction.response.send_message(embed=embed)