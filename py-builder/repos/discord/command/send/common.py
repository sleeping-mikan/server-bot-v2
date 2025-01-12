#!ignore
from ....constant import *
from ....logger.logger_create import *
#!end-ignore

# グループの設定
# root
command_group_announce = app_commands.Group(name="announce",description="send messege to discord")

#!open ./repos/discord/command/send/embed/main.py
#!ignore
from .embed.main import *
#!end-ignore

tree.add_command(command_group_announce)