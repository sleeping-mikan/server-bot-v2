#!ignore
from .common import *
#!end-ignore

@command_group_cmd_stdin.command(name="send-discord",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["send-discord"])
async def send_discord(interaction: discord.Interaction, path: str):
    await print_user(cmd_logger,interaction.user)
    file_path = os.path.abspath(os.path.join(server_path,path))  # ファイルのパス
    file_size_limit = 9 * 1024 * 1024  # 9MB
    # 権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin send-discord"]:
        await not_enough_permission(interaction,cmd_logger)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_not_found"].format(file_path))
        cmd_logger.info("file not found -> " + file_path)
        return
    # 該当のアイテムがファイルか
    if not os.path.isfile(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["not_file"].format(file_path))
        cmd_logger.info("not file -> " + file_path)
        return
    # 操作可能なパスか確認
    if not is_path_within_scope(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        cmd_logger.info("invalid path -> " + file_path)
        return

    # ファイルサイズをチェック
    file_size = os.path.getsize(file_path)
    if file_size > file_size_limit:
        cmd_logger.info("file size over limit -> " + file_path + " : " + str(file_size))
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["file_size_limit"].format(file_size,file_size_limit))

        # file.ioにアップロード
        async with aiohttp.ClientSession() as session:
            async with session.post("https://file.io", data={"file": open(file_path, 'rb')}) as response:
                if response.status == 200:
                    response_json = await response.json()
                    download_link = response_json.get("link")
                    cmd_logger.info("upload to file.io -> " + file_path + " : " + download_link)
                    await interaction.followup.send(content=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["success"].format(interaction.user.id,download_link))
                else:
                    cmd_logger.info("upload to file.io failed -> " + file_path)
                    await interaction.followup.send(content=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_io_error"].format(interaction.user.id))
    else:
        # Discordで直接送信
        cmd_logger.info("send to discord -> " + file_path)
        await interaction.response.send_message(file=discord.File(file_path))