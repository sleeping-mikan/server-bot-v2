#!ignore
from ....entry.standard_imports import *
from ....entry.variable import *
from ....entry.thirdparty_imports import *
from ....assets.text_dat import *
from ....assets.utils import *
from ....logger.logger_create import *
#!end-ignore

#/status
@tree.command(name="status",description=COMMAND_DESCRIPTION[lang]["status"])
async def status(interaction: discord.Interaction):
    await print_user(status_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/status")