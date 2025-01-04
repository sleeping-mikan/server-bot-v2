#!ignore
from .common import *
#!end-ignore

stdin_send_discord_logger = stdin_logger.getChild("send-discord")

@command_group_cmd_stdin.command(name="send-discord",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["send-discord"])
async def send_discord(interaction: discord.Interaction, path: str):
    await print_user(stdin_send_discord_logger,interaction.user)
    file_path = os.path.abspath(os.path.join(server_path,path))  # ファイルのパス
    file_name = os.path.basename(file_path)
    file_size_limit = 9 * 1024 * 1024  # 9MB
    file_size_limit_web = 2 * 1024 * 1024 * 1024  # 2GBを超えた場合file.ioでも無理なのでエラー
    # 権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd stdin send-discord"]:
        await not_enough_permission(interaction,stdin_send_discord_logger)
        return
    # ファイルが存在しているかを確認
    if not os.path.exists(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_not_found"].format(file_path))
        stdin_send_discord_logger.info("file not found -> " + file_path)
        return
    # # 該当のアイテムがファイルか
    # if not os.path.isfile(file_path):
    #     await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["not_file"].format(file_path))
    #     stdin_send_discord_logger.info("not file -> " + file_path)
    #     return
    if not is_path_within_scope(file_path):
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path))
        stdin_send_discord_logger.info("invalid path -> " + file_path)
        return
    # 該当のアイテムがディレクトリならzip圧縮をする
    if os.path.isdir(file_path):
        # とりあえずdiscordに送っておく
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["is_zip"].format(file_path))
        stdin_send_discord_logger.info("make zip -> " + str(file_path))
        zip_buffer,file_size = await create_zip_async(file_path)
        base_file_path = file_path
        file_path = zip_buffer
        stdin_send_discord_logger.info("zip -> " + str(file_path) + f"({base_file_path})" + " : " + str(file_size))
        file_name = file_name + ".zip"
    else:
        # await interaction.response.send_message(RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["is_file"].format(file_path))
        # ファイルサイズをチェック
        file_size = os.path.getsize(file_path)
        stdin_send_discord_logger.info("file -> " + str(file_path))
    if file_size > file_size_limit_web:
        stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
        await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit_web"].format(file_size,file_size_limit_web))
    if file_size > file_size_limit:
        stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
        await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit"].format(file_size,file_size_limit))

        # file.ioにアップロード
        try:
            timeout_sec = 1500
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec)) as session:
                async with session.post("https://file.io", data={"file": open(file_path, 'rb') if isinstance(file_path, str) else file_path, "name": file_name}) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        download_link = response_json.get("link")
                        stdin_send_discord_logger.info("upload to file.io -> " + str(file_path) + " : " + download_link)
                        await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["success"].format(interaction.user.id,download_link))
                    else:
                        stdin_send_discord_logger.info("upload to file.io failed -> " + str(file_path) + ",reason -> " + str(response.reason) + "::" + str(response.text))
                        await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_io_error"].format(interaction.user.id,str(response.status),str(response.reason),str(response.text)))
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            stdin_send_discord_logger.info("upload to file.io failed (timeout) -> " + str(file_path))
            await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["timeout"].format(interaction.user.id))
    else:
        # Discordで直接送信
        stdin_send_discord_logger.info("send to discord -> " + str(file_path))
        await send_discord_message_or_followup(interaction=interaction,file=discord.File(file_path))