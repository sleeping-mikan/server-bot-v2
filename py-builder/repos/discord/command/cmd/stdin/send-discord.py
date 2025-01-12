#!ignore
from .common import *
#!end-ignore

stdin_send_discord_logger = stdin_logger.getChild("send-discord")


discord_multi_thread_return_dict = {}
def send_file_io(_id, file_obj, file_name) -> requests.Response:
    response = requests.post("https://file.io/", files={"file": (file_name, file_obj)})
    discord_multi_thread_return_dict[_id] = response
    

send_discord_timeout_sec = 60 * 25

@command_group_cmd_stdin.command(name="send-discord",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["send-discord"])
async def send_discord(interaction: discord.Interaction, path: str):
    await print_user(stdin_send_discord_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/cmd stdin send-discord {path}")
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
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_not_found"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_send_discord_logger.info("file not found -> " + file_path)
        return
    # パスが許可されているかを確認
    if not is_path_within_scope(file_path):
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["invalid_path"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed)
        stdin_send_discord_logger.info("invalid path -> " + file_path)
        return
    # 該当のアイテムがディレクトリならzip圧縮をする
    if os.path.isdir(file_path):
        # とりあえずdiscordに送っておく
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["is_zip"].format(file_path),inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)
        stdin_send_discord_logger.info("make zip -> " + str(file_path))
        zip_buffer,file_size = await create_zip_async(file_path)
        base_file_path = file_path
        file_path = zip_buffer
        file_path.seek(0)
        stdin_send_discord_logger.info("zip -> " + str(file_path) + f"({base_file_path})" + " : " + str(file_size))
        file_name = file_name + ".zip"
        file_obj = file_path
    else:
        # ファイルサイズをチェック
        file_size = os.path.getsize(file_path)
        stdin_send_discord_logger.info("file -> " + str(file_path))
        # ファイルを開く
        file_obj = open(file_path, "rb")
    if file_size > file_size_limit_web:
        stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit_web"].format(file_size,file_size_limit_web),inline=False)
        await send_discord_message_or_edit(interaction=interaction,embed=embed,ephemeral=True)
    if file_size > file_size_limit: # なぜか400errの時async loopが落ちてしまうっぽい問題が解決できなさそうな雰囲気なので一旦削除
        stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
        embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit"].format(file_size,file_size_limit),inline=False)
        await send_discord_message_or_edit(interaction=interaction,embed=embed,ephemeral=True)
        # file.ioにアップロード
        try:
            timeout_sec = send_discord_timeout_sec
            # uuidを使って、POSTするスレッドの戻り値を待機する
            discord_dict_id = uuid.uuid4()
            io_thread = threading.Thread(target=send_file_io,args=(discord_dict_id,file_obj,file_name),daemon=True)
            io_thread.start()
            # discord_multi_thread_return_dict[discord_dict_id]にPOSTスレッドがresponseをセットするまで繰り返し
            while discord_dict_id not in discord_multi_thread_return_dict:
                await asyncio.sleep(1)
                timeout_sec -= 1
                if timeout_sec <= 0:
                    raise asyncio.TimeoutError
            if discord_multi_thread_return_dict[discord_dict_id].status_code != 200:
                status = discord_multi_thread_return_dict[discord_dict_id].status_code
                reason = discord_multi_thread_return_dict[discord_dict_id].reason
                text = discord_multi_thread_return_dict[discord_dict_id].text
                stdin_send_discord_logger.error("upload to file.io failed -> " + str(file_path) + " ,status -> " + str(status) + " , " + str(reason) + " :: " + str(text))
                embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_io_error"].format(interaction.user.id,status,reason,text),inline=False)
                await send_discord_message_or_edit(interaction=interaction,embed=embed)
                return
            response = discord_multi_thread_return_dict[discord_dict_id]
            stdin_send_discord_logger.info("content type -> " + str(response.headers.get("content-type")))
            # responseがjsonで来ないことがあるので
            if not response.headers.get("content-type").startswith("application/json"):
                status = discord_multi_thread_return_dict[discord_dict_id].status_code
                reason = discord_multi_thread_return_dict[discord_dict_id].reason
                text = "Too Many Characters"
                stdin_send_discord_logger.error("upload to file.io failed (not json) -> " + str(file_path))
                embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_io_error"].format(interaction.user.id,status,reason,text),inline=False)
                await send_discord_message_or_edit(interaction=interaction,embed=embed)
                return
            link = response.json()["link"]
            stdin_send_discord_logger.info("upload to file.io -> " + str(file_path) + " : " + str(response.status_code))
            embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["success"].format(interaction.user.id,link),inline=False)
            await send_discord_message_or_edit(interaction=interaction,embed=embed)
        except Exception as e:
            if isinstance(e, asyncio.TimeoutError) or isinstance(e,aiohttp.ClientError):
                stdin_send_discord_logger.error("upload to file.io failed (timeout) -> " + str(file_path))
                embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["timeout"].format(interaction.user.id,send_discord_timeout_sec),inline=False)
                await send_discord_message_or_edit(interaction=interaction,embed=embed)
            else:
                import traceback
                stdin_send_discord_logger.error(traceback.format_exc())
                stdin_send_discord_logger.error("raise upload to file.io failed")
                embed.add_field(name="",value=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["raise_error"].format(interaction.user.id,traceback.format_exc()),inline=False)
                await send_discord_message_or_edit(interaction=interaction,embed=embed)
        finally:
            # file_objが開いていたら閉じる(file_objはopen() or io.BytesIO()で開いたもの)
            file_obj.close()
            stdin_send_discord_logger.info("close file -> " + str(file_path))
    else:
        # Discordで直接送信
        stdin_send_discord_logger.info("send to discord -> " + str(file_path))
        await send_discord_message_or_edit(interaction=interaction,file=discord.File(file_path,filename=file_name),embed=embed,ephemeral=True)

#!ignore


@command_group_cmd_stdin.command(name="send-discord",description=COMMAND_DESCRIPTION[lang]["cmd"]["stdin"]["send-discord"])
async def send_discord(interaction: discord.Interaction, path: str):
    await print_user(stdin_send_discord_logger,interaction.user)
    file_path = os.path.abspath(os.path.join(server_path,path))  # ファイルのパス
    file_name = os.path.basename(file_path)
    stdin_send_discord_logger.info("get abs file path -> " + str(file_path))
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
    # if file_size > file_size_limit_web:
    #     stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
    #     await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit_web"].format(file_size,file_size_limit_web))
    if file_size > file_size_limit: # なぜか400errの時async loopが落ちてしまうっぽい問題が解決できなさそうな雰囲気なので一旦削除
        stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
        await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit_web"].format(file_size,file_size_limit))
        stdin_send_discord_logger.info("file size over limit -> " + str(file_path) + " : " + str(file_size))
        await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["file_size_limit"].format(file_size,file_size_limit))

        # file.ioにアップロード
        try:
            timeout_sec = 1500
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec)) as session:
                file_obj = open(file_path, 'rb') if isinstance(file_path, str) else file_path
                async with session.post("https://file.io/", files={"file": (file_name, file_obj)}) as response:
                    # HTTP 200以外の場合にエラー処理
                    if response.status != 200:
                        # HTTPエラーの処理
                        error_text = await response.text()
                        stdin_send_discord_logger.error(f"Upload failed. Status: {response.status}, Response: {error_text}")
                        await send_discord_message_or_followup(interaction, message="Upload failed with status: {response.status}. Please try again later.")
                        session.close()
                        return
                    if response.status == 200:
                        response_json = await response.json()
                        download_link = response_json.get("link")
                        stdin_send_discord_logger.info("upload to file.io -> " + str(file_path) + " : " + download_link)
                        await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["success"].format(interaction.user.id,download_link))
                        await interaction.followup.send(content=f"<@{interaction.user.id}>")
                    else:
                        response_json = await response.json()
                        if not isinstance(file_obj, io.BytesIO):
                            file_obj.close()
                        # aiohttpに関するオブジェクトを正しく閉じる
                        await session.close()
                        stdin_send_discord_logger.info("upload to file.io failed -> " + str(file_path) + ",reason -> " + str(response.reason) + "::" + await response.text())
                        await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["file_io_error"].format(interaction.user.id,str(response.status),str(response.reason),await response.text()))
                        raise Exception("upload to file.io failed")
        except Exception as e:
            if isinstance(e, asyncio.TimeoutError) or isinstance(e,aiohttp.ClientError):
                stdin_send_discord_logger.error("upload to file.io failed (timeout) -> " + str(file_path))
                await send_discord_message_or_followup(interaction=interaction,message=RESPONSE_MSG["cmd"]["stdin"]["send-discord"]["timeout"].format(interaction.user.id))
            else:
                import traceback
                stdin_send_discord_logger.error(traceback.format_exc())
                stdin_send_discord_logger.error("raise upload to file.io failed")
            exit()
        finally:
            stdin_send_discord_logger.info("close file -> " + str(file_path))
            file_obj.close() if isinstance(file_path, str) else None
    else:
        # Discordで直接送信
        stdin_send_discord_logger.info("send to discord -> " + str(file_path))
        await send_discord_message_or_followup(interaction=interaction,file=discord.File(file_path,filename=file_name))
#!end-ignore