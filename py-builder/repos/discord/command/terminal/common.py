#!ignore
from ....imports import *
from ....constant import *
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
#!end-ignore

command_group_terminal = app_commands.Group(name="terminal",description="terminal group")

async def change_terminal_ch(channel: int | bool, logger: logging.Logger):    
    global where_terminal
    #terminalを無効化
    where_terminal = channel
    config["discord_commands"]["terminal"]["discord"] = where_terminal
    logger.info(f"terminal setting -> {where_terminal}")
    await rewrite_config(config=config)

#!open ./repos/discord/command/terminal/set.py
#!ignore
from .set import *
#!end-ignore
#!open ./repos/discord/command/terminal/delete.py
#!ignore
from .delete import *
#!end-ignore

tree.add_command(command_group_terminal)
