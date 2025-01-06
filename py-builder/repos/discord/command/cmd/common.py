#!ignore
from ....constant import *
from ....logger.logger_create import *
#!end-ignore

# グループの設定
# root
command_group_cmd = app_commands.Group(name="cmd",description="cmd group")

serverin_logger = cmd_logger.getChild("serverin")