#!ignore
from ..common import *
#!end-ignore

discord_multi_thread_return_dict = {}
def send_file_io(_id, file_obj, file_name) -> requests.Response:
    headers = {"Accept": "application/json"}  # ask server for JSON
    files = {"file": (file_name, file_obj, "application/octet-stream")}
    response = requests.post("https://file.io/", files=files, headers=headers)
    discord_multi_thread_return_dict[_id] = response

async def send_discord_fileio(interaction: discord.Interaction, embed: discord.Embed, stdin_send_discord_logger: logging.Logger, \
                            file_size_limit_web: int, file_size_limit: int, file_path: str, file_name: str):
    send_discord_timeout_sec = 60 * 25
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
        return
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
                # print(discord_multi_thread_return_dict[discord_dict_id].text)
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
