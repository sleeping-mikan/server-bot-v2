#!ignore    
from ...logger.logger_create import *
from ...minecraft.read_properties import *
from ...assets.text_dat import *
from ...assets.utils import *
import traceback
#!end-ignore




def core_stop() -> str:
    global process,use_stop
    if is_stopped_server(stop_logger):
        return RESPONSE_MSG["other"]["is_not_running"]
    use_stop = True
    stop_logger.info('server stopping')
    process.stdin.write(STOP + "\n")
    process.stdin.flush()
    return RESPONSE_MSG["stop"]["success"]

def core_start() -> str:
    global process,use_stop
    if is_running_server(start_logger):
        return RESPONSE_MSG["other"]["is_running"]
    start_logger.info('server starting')
    process = subprocess.Popen([server_path + server_name],cwd=server_path,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,encoding="utf-8")
    threading.Thread(target=server_logger,args=(process,deque())).start()
    return RESPONSE_MSG["start"]["success"]
