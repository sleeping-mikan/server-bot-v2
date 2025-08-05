#!ignore
from ..entry.standard_imports import *
from ..entry.variable import *
from ..logger.logger_create import *
from ..minecraft.read_properties import *
from ..assets.text_dat import *
from ..assets.utils import *
#!end-ignore
@tasks.loop(seconds=10)
async def update_loop():
    global discord_terminal_item, discord_terminal_send_length, discord_loop_is_run
    # discord_loop_is_runを確認(2回以上実行された場合は処理をしない)
    if discord_loop_is_run: return
    try:
        discord_loop_is_run = True
        with status_lock:
            if process is not None:
                await client.change_presence(activity=discord.Game(name=ACTIVITY_NAME["running"]))
            else:
                await client.change_presence(activity=discord.Game(name=ACTIVITY_NAME["ended"]))
            # discord_log_msgにデータがあれば送信
            # 送信が無効の場合
            if where_terminal == False:
                discord_log_msg.clear()
                discord_loop_is_run = False
                return
            pop_flg = False
            while len(discord_log_msg) > 0:
                while len(discord_log_msg) > terminal_capacity:
                    discord_log_msg.popleft()
                    pop_flg = True
                if pop_flg:
                    await client.get_channel(where_terminal).send(f"データ件数が{terminal_capacity}件を超えたため以前のデータを破棄しました。より多くのログを出力するには.config内のterminal.capacityを変更してください。")
                    pop_flg = False
                if len(discord_log_msg[0]) >= 1900:
                    discord_log_msg.popleft()
                    raise Exception("message is too long(skipped)")
                discord_terminal_send_length += len(discord_log_msg[0]) + 1
                if discord_terminal_send_length >= 1900:
                    # 送信処理(where_terminal chに送信)
                    await client.get_channel(where_terminal).send("```ansi\n" + ''.join(discord_terminal_item) + "\n```")
                    # discord_terminal_itemをリセット
                    discord_terminal_item = deque()
                    discord_terminal_send_length = len(discord_log_msg[0]) + 1
                    # 連投を避けるためにsleep
                    await asyncio.sleep(1)
                discord_terminal_item.append(discord_log_msg.popleft() + "\n")
            # 残っていれば送信
            if len(discord_terminal_item) > 0:
                await client.get_channel(where_terminal).send("```ansi\n" + ''.join(discord_terminal_item) + "\n```")
                discord_terminal_item = deque()
                discord_terminal_send_length = 0
        discord_loop_is_run = False
    except Exception as e:
        terminal_logger.error(e)
        discord_loop_is_run = False

# メッセージが送信されたときの処理
@client.event
async def on_message(message: discord.Message):
    try:
        # ボット自身のメッセージは無視する
        if message.author == client.user:
            return
        # terminal ch以外のメッセージは無視
        if message.channel.id != where_terminal:
            return
        # 管理者以外をはじく
        if not await is_administrator(message.author) and not await is_force_administrator(message.author):
            await message.reply("permission denied")
            return
        # サーバーが閉じていたらはじく
        if process is None or process.poll() is not None:
            await message.reply("server is not running")
            return
        # コマンドを処理
        cmd_list = message.content.split(" ")
        # 許可されないコマンドをはじく
        if message.author.bot is True: pass
        elif cmd_list[0] not in allow_cmd:
            sys_logger.error('unknown command : ' + " ".join(cmd_list))
            await message.reply("this command is not allowed")
            return
        else:
            process.stdin.write(message.content + "\n")
            process.stdin.flush()
    except Exception as e:
        sys_logger.error(e)

@client.event
async def on_ready():
    global process
    ready_logger.info('discord bot logging on')
    # update_loopを開始
    update_loop.start()
    # 拡張で読み込んだtasksを実行
    for task in extension_tasks_func:
        task.start()
    try:
        #サーバーの起動
        await client.change_presence(activity=discord.Game(ACTIVITY_NAME["starting"]))
        if process is  None:
            #server を実行する
            process = subprocess.Popen([server_path + server_name, *server_args],cwd=server_path,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,encoding="utf-8")
            threading.Thread(target=server_logger,args=(process,deque())).start()
            ready_logger.info('server starting')
        else:
            ready_logger.info('skip server starting because server already running')
        # アクティビティを設定 
        await client.change_presence(activity=discord.Game(ACTIVITY_NAME["running"])) 
        # スラッシュコマンドを同期 
        await tree.sync()
    except Exception as e:
        sys_logger.error(f"error on ready -> {e}")