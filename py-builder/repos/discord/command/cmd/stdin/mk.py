#!ignore
from .common import *
#!end-ignore

# 以下のコマンドはserver_pathを起点としてそれ以下のファイルを操作する
# ファイル送信コマンドを追加
@command_group_cmd_stdin.command(name="mk",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["mk"])
async def mk(interaction: discord.Interaction, file_path: str,file:discord.Attachment|None = None):
    await print_user(cmd_logger,interaction.user)
    # 管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin mk"]:
        await not_enough_permission(interaction,cmd_logger)
        return
    #サーバー起動確認
    if is_running_server(cmd_logger): 
        await interaction.response.send_message(RESPONSE_MSG["other"]["is_running"])
        return
    # server_path + file_path にファイルを作成
    file_path = os.path.abspath(os.path.join(server_path,file_path))
    # 操作可能なパスか確認
    if not is_path_within_scope(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        cmd_logger.info("invalid path -> " + file_path)
        return
    # ファイルがリンクであれば拒否
    if os.path.islink(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["mk"]["is_link"].format(file_path))
        cmd_logger.info("file is link -> " + file_path)
        return
    # 全ての条件を満たすがサーバー管理者権限を持たず、重要ファイルを操作しようとしている場合
    if not await is_administrator(interaction.user) and await is_important_bot_file(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(file_path))
        cmd_logger.info("permission denied -> " + file_path)
        return
    else:
        # 空のファイルを作成
        open(file_path,"w").close()
        # ファイルをfile_pathに保存
        if file is not None:
            await file.save(file_path)
    cmd_logger.info("create file -> " + file_path)
    await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["mk"]["success"].format(file_path))
