#!ignore
from ....imports import *
from ....constant import *
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
from .common import *
#!end-ignore



@command_group_cmd.command(name="serverin",description=COMMAND_DESCRIPTION[lang]["cmd"]["serverin"])
async def cmd(interaction: discord.Interaction,command:str):
    await print_user(serverin_logger,interaction.user)
    global is_back_discord,cmd_logs
    #管理者権限を要求
    if await user_permission(interaction.user) < COMMAND_PERMISSION["cmd serverin"]: 
        await not_enough_permission(interaction,serverin_logger)
        return
    #サーバー起動確認
    if is_stopped_server(serverin_logger): 
        await interaction.response.send_message(RESPONSE_MSG["other"]["is_not_running"])
        return
    #コマンドの利用許可確認
    if command.split()[0] not in allow_cmd:
        serverin_logger.error('unknown command : ' + command)
        await interaction.response.send_message(RESPONSE_MSG["cmd"]["serverin"]["skipped_cmd"])
        return
    serverin_logger.info("run command : " + command)
    process.stdin.write(command + "\n")
    process.stdin.flush()
    #結果の返却を要求する
    is_back_discord = True
    #結果を送信できるまで待機
    while True:
        #何もなければ次を待つ
        if len(cmd_logs) == 0:
            await asyncio.sleep(0.1)
            continue
        await interaction.response.send_message(cmd_logs.popleft())
        break