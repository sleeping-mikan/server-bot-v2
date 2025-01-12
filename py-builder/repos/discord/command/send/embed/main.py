#!ignore
from .....imports import *
from .....constant import *
from .....logger.logger_create import *
from .....minecraft.read_properties import *
from .....assets.text_dat import *
from .....assets.utils import *
from ..common import *
#!end-ignore

@command_group_announce.command(name="embed",description=COMMAND_DESCRIPTION[lang]["announce"]["embed"])
async def embed(interaction: discord.Interaction, file: discord.Attachment|None = None, txt: str = ""):
    await print_user(announce_logger,interaction.user)
    return_embed = ModifiedEmbeds.DefaultEmbed(title= f"/embed {file.filename if file is not None else ''} {txt}")
    embed = ModifiedEmbeds.DefaultEmbed(title= f"")
    # 権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["announce embed"]: 
        await not_enough_permission(interaction,announce_logger)
        return
    # ファイルとテキストの両方が存在する場合はエラー
    if file is not None and txt != "":
        return_embed.add_field(name="",value=RESPONSE_MSG["cmd"]["announce"]["embed"]["exist_file_and_txt"],inline=False)
        await interaction.response.send_message(embed=return_embed)
        announce_logger.info("file and txt exist")
        return
    # ファイルがある場合はファイルを展開してtxtに代入
    if file is not None:
        try:
            txt = (await file.read()).decode("utf-8")
        except:
            return_embed.add_field(name="",value=RESPONSE_MSG["announce"]["embed"]["decode_error"],inline=False)
            await interaction.response.send_message(embed=return_embed)
            announce_logger.info("file decode error")
            return
    # テキストで送られてるなら\\nを改行に変換
    if txt:
        txt = txt.replace("\\n","\n")
        return_embed.add_field(name="",value=RESPONSE_MSG["announce"]["embed"]["replace_slash_n"],inline=False)
    # 内容が空なら
    if txt == "":
        return_embed.add_field(name="",value=RESPONSE_MSG["announce"]["embed"]["empty"],inline=False)
        await interaction.response.send_message(embed=return_embed)
        announce_logger.info("txt is empty")
        return
    send_data, other_dat = await parse_mimd(txt)
    announce_logger.info("parsed txt")
    # embedに追加
    embed.title = other_dat["title"]
    for items in send_data:
        embed.add_field(name=items["name"],value=items["value"],inline=False)
    return_embed.add_field(name="",value=RESPONSE_MSG["announce"]["embed"]["success"],inline=False)
    # embedを送信
    await interaction.response.send_message(embed=return_embed,ephemeral=True)
    # 同じchidにembedを送信
    await interaction.channel.send(embed=embed)
    announce_logger.info('embed sent')


