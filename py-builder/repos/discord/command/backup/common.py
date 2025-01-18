#!ignore
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
#!end-ignore

command_group_backup = app_commands.Group(name="backup",description="backup group")

#!open ./repos/discord/command/backup/create.py
#!open ./repos/discord/command/backup/apply.py