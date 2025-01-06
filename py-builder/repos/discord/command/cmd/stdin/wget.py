#!ignore
from .common import *
#!end-ignore

stdin_wget_logger = stdin_logger.getChild("wget")

@command_group_cmd_stdin.command(name="wget",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["wget"])
async def wget(interaction: discord.Interaction,url:str,path:str = "mi_dl_file.tmp"):
    await print_user(stdin_wget_logger,interaction.user)
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin wget"]: 
        await not_enough_permission(interaction,stdin_wget_logger)
        return
    save_path = os.path.abspath(os.path.join(server_path,path))
    # 既にファイルが存在しているか確認
    if os.path.exists(save_path):
        stdin_wget_logger.info("file already exists -> " + save_path)
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["wget"]["already_exists"].format(path))
        return
    # pathが操作可能か確認
    if not is_path_within_scope(save_path):
        stdin_wget_logger.info("invalid path -> " + save_path)
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(save_path))
        return
    # 管理者権限を持っていなくて、重要ファイルをダウンロードする場合は拒否
    if not await is_administrator(interaction.user) and await is_important_bot_file(save_path):
        stdin_wget_logger.info("permission denied -> " + save_path)
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["permission_denied"].format(save_path))
        return
    # URLからファイルをダウンロード
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                stdin_wget_logger.info("download failed -> " + url)
                await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["wget"]["download_failed"].format(url))
                return

            # ファイルを保存
            with open(save_path, 'wb') as file:
                file.write(await response.read())
    stdin_wget_logger.info("download success -> " + url + " to " + save_path)
    await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["wget"]["download_success"].format(url,save_path))