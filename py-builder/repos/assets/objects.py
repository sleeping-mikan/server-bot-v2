#!ignore
from ..entry.standard_imports import *
from ..entry.variable import *
from ..entry.thirdparty_imports import *
#!end-ignore

class ModifiedEmbeds():# 名前空間として
    class DefaultEmbed(discord.Embed):
        def __init__(self, title, description = None, color = bot_color):
            super().__init__(title=title, description=description, color=color)
            self.set_image(url=embed_under_line_url)
            self.set_thumbnail(url=embed_thumbnail_url)
    class ErrorEmbed(discord.Embed):
        def __init__(self, title, description = None, color = 0xff0000):
            super().__init__(title=title, description=description, color=color)
            self.set_image(url=embed_under_line_url)
            self.set_thumbnail(url=embed_thumbnail_url)