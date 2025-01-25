#!ignore
from ....imports import *
from ....constant import *
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
from .common import *
#!end-ignore



#/terminal
@tree.command(name="terminal",description=COMMAND_DESCRIPTION[lang]["terminal"])
async def terminal(interaction: discord.Interaction):
    global where_terminal
    await print_user(terminal_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/terminal")
    # 権限レベルが足りていないなら
    if await user_permission(interaction.user) < COMMAND_PERMISSION["terminal"]:
        await not_enough_permission(interaction,terminal_logger)
        return
    #発言したチャンネルをwhere_terminalに登録
    where_terminal = interaction.channel_id
    config["discord_commands"]["terminal"]["discord"] = where_terminal
    terminal_logger.info(f"terminal setting -> {where_terminal}")
    #configを書き換え
    with open(now_path + "/.config","w") as f:
        json.dump(config,f,indent=4,ensure_ascii=False)
    embed.add_field(name="",value=RESPONSE_MSG["terminal"]["success"].format(where_terminal),inline=False)
    await interaction.response.send_message(embed=embed)