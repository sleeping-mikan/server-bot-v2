#!ignore
from ....entry.standard_imports import *
from ....entry.variable import *
from ....entry.thirdparty_imports import *
from ....entry.thirdparty_imports import *
from ....assets.text_dat import *
from ....assets.utils import *
from ....logger.logger_create import *
#!end-ignore

async def get_process_memory(process: subprocess.Popen | None) -> dict:
    MB = 1024**2
    # このプログラムの利用メモリを取得する
    origin_process = psutil.Process(os.getpid())
    origin_mem = origin_process.memory_info().rss / MB
    # サーバープロセスの利用メモリを取得する
    if process is not None:
        childs = psutil.Process(process.pid).children(recursive=True)
        server_mem = sum([psutil.Process(child.pid).memory_info().wset for child in childs]) / MB
        server_mem += (psutil.Process(process.pid)).memory_info().wset / MB
    else:
        server_mem = 0
    return {
        "origin_mem": origin_mem,
        "server_mem": server_mem
    }

async def get_process_cpu(process: subprocess.Popen) -> float:
    return psutil.cpu_percent(interval=1.0)

async def get_thread_cpu_usage(pid : int, interval=1.0, is_self = False):
    # 全てのスレッドを取得
    process = psutil.Process(pid)
    # 初回のCPU時間を取得
    thread_cpu_times = {t.id: t.user_time + t.system_time for t in process.threads()}
    # 1秒間のCPU使用率を取得
    await asyncio.sleep(interval)
    # CPU時間の差分を取得
    tmp_cpu_times = {t.id: t.user_time + t.system_time for t in process.threads()}
    for tid in thread_cpu_times:
        try:
            thread_cpu_times[tid] = tmp_cpu_times[tid] - thread_cpu_times[tid]
        except KeyError:
            thread_cpu_times[tid] = 0
    # 全体のCPU時間を取得
    sum_cpu_times = sum(thread_cpu_times.values())
    # is_selfがtrueであれば、自身の名前に置き換える
    if is_self:
        items = threading.enumerate()
        for thread in items:
            if thread.ident in thread_cpu_times:
                thread_cpu_times[thread.name] = thread_cpu_times.pop(thread.ident)
    # 全体のCPU時間を取得
    sum_cpu_times = sum(thread_cpu_times.values())

    status_logger.debug(f"thread_cpu_times: {thread_cpu_times}")
    status_logger.debug(f"sum_cpu_times: {sum_cpu_times}")

    # threadごとのパーセントを計算
    cpu_usage = {
        tid: (thread_cpu_times[tid] / sum_cpu_times) * 100 if sum_cpu_times != 0 else 0
        for tid in thread_cpu_times
    }

    status_logger.debug(f"cpu_usage: {cpu_usage}")
    
    process_cpu = await get_process_cpu(process)

    status_logger.debug(f"process_cpu: {process_cpu}")

    # CPU使用率を計算
    cpu_usage = {
        tid : cpu_usage[tid] / 100 * process_cpu
        for tid in cpu_usage
    }

    status_logger.debug(f"cpu_usage: {cpu_usage}")

    return cpu_usage

async def check_response(url:str = "http://127.0.0.1"):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    sys_logger.info("Waitress server is running.")
                    return True
                else:
                    sys_logger.info(f"Server returned status code: {response.status}")
                    return False
    except aiohttp.ClientError as e:
        sys_logger.info(f"Server is not running: {e}")
        return False

#/status
@tree.command(name="status",description=COMMAND_DESCRIPTION[lang]["status"])
async def status(interaction: discord.Interaction):
    await print_user(status_logger,interaction.user)
    await interaction.response.defer()
    embed = ModifiedEmbeds.DefaultEmbed(title= f"/status")
    
    # プログラムの利用メモリを取得する
    memorys = await get_process_memory(process)
    embed.add_field(name=RESPONSE_MSG["status"]["mem_title"],value=RESPONSE_MSG["status"]["mem_value"].format(round(memorys["origin_mem"],2)) + "\n" + RESPONSE_MSG["status"]["mem_server_value"].format(round(memorys["server_mem"],2)))

    status_logger.info(f"get memory -> process {memorys['origin_mem']}, server {memorys["server_mem"]}")

    # online状態を取得する
    is_server_online = "🟢" if process is not None and process.poll() is None else "🔴"
    is_waitress_online = "🟢" if await check_response(f"http://127.0.0.1:{web_port}") else "🔴"
    is_bot_online = "🟢"
    embed.add_field(name=RESPONSE_MSG["status"]["online_title"],value=RESPONSE_MSG["status"]["online_value"].format(is_server_online, is_waitress_online, is_bot_online))

    # SERVER PROCESS CPUの利用率を取得する
    if process is not None:
        cpu_usage = {server_name :(await get_process_cpu(process.pid))}
    else:
        cpu_usage = {"NULL": "NULL"}
    send_str = ["Server"]
    send_str += [RESPONSE_MSG["status"]["cpu_value_proc"].format(cpu_usage[key], key) for key in cpu_usage]
    # BOT PROCESS CPUの利用率を取得する
    cpu_usage = await get_thread_cpu_usage(os.getpid(), is_self=True)
    send_str += ["Main"]
    send_str += [RESPONSE_MSG["status"]["cpu_value_thread"].format(cpu_usage[key], key) for key in cpu_usage]
    embed.add_field(name=RESPONSE_MSG["status"]["cpu_title"],value="\n".join(send_str), inline=False)

    status_logger.info(f"get cpu usage -> {' '.join(send_str)}")

    # 基本情報を記載
    embed.add_field(name=RESPONSE_MSG["status"]["base_title"],value=RESPONSE_MSG["status"]["base_value"].format(platform.system() + " " + platform.release() + " " + platform.version(), sys.version, __version__), inline=True)

    await interaction.edit_original_response(embed=embed)
    status_logger.info('status command end')