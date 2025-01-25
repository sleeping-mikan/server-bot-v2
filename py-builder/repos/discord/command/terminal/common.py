#!ignore
from ....imports import *
from ....constant import *
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
#!end-ignore

command_group_terminal = app_commands.Group(name="terminal",description="terminal group")

async def change_terminal_ch(channel: int | bool):    
    global where_terminal
    #terminalを無効化
    where_terminal = channel
    config["discord_commands"]["terminal"]["discord"] = where_terminal
    terminal_logger.info(f"terminal setting -> {where_terminal}")
    #configを書き換え
    with open(now_path + "/.config","w") as f:
        json.dump(config,f,indent=4,ensure_ascii=False)

#!open ./repos/discord/command/terminal/set.py
#!ignore
from .set import *
#!end-ignore
#!open ./repos/discord/command/terminal/delete.py
#!ignore
from .delete import *
#!end-ignore

tree.add_command(command_group_terminal)
