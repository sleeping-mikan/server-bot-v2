#!ignore
from .common import *
#!end-ignore

stdin_mk_logger = stdin_logger.getChild("mk")

# 以下のコマンドはserver_pathを起点としてそれ以下のファイルを操作する
# ファイル送信コマンドを追加
@command_group_cmd_stdin.command(name="mk",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mk"])
async def mk(interaction: discord.Interaction, file_path: str,file:discord.Attachment|None = None):
    await print_user(stdin_mk_logger,interaction.user)
    embed = discord.Embed(color=bot_color,title= f"/cmd stdin mk {file_path} {file.filename if file is not None else ''}")
    embed.set_image(url = embed_under_line_url)
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin mk"]:
        await not_enough_permission(interaction,stdin_mk_logger)
        return
    #サーバー起動確認
    if is_running_server(stdin_mk_logger): 
        embed.add_field(name="",value=RESPONSE_MSG["other"]["is_running"],inline=False)
        await interaction.response.send_message(embed=embed)
        return
    # server_path + file_path にファイルを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mk_logger.info("invalid path -> " + file_path)
        return
    # ファイルがリンクであれば拒否
    if os.path.islink(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mk"]["is_link"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mk_logger.info("file is link -> " + file_path)
        return
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if not await is_administrator(interaction.user) and await is_important_bot_file(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_mk_logger.info("permission denied -> " + file_path)
        return
    else:
        # 空のファイルを作成
        open(file_path,"w").close()
        # ファイルをfile_pathに保存
        if file is not None:
            await file.save(file_path)
    stdin_mk_logger.info("create file -> " + file_path)
    embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["mk"]["success"].format(file_path),inline=False)
    await interaction.response.send_message(embed=embed)
