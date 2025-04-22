#!ignore
from ....entry.standard_imports import *
from ....entry.variable import *
from ....entry.thirdparty_imports import *
from ....logger.logger_create import *
from ....assets.text_dat import *
from ....assets.utils import *
#!end-ignore


def get_process():
    return process

def append_tasks_func(func):
    extension_tasks_func.append(func)
    return

is_write_server_block = False
def write_server_in(command: str):
    global is_write_server_block
    if is_write_server_block:
        return False, "write_server_block"
    is_write_server_block = True
    # サーバーが動いていれば、コマンドを送る
    if is_stopped_server(sys_logger):
        is_write_server_block = False
        return False, "server_is_not_running"
    process.stdin.write(command + "\n")
    process.stdin.flush()
    is_write_server_block = False
    return True, "success"