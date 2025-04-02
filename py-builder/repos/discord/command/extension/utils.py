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

def write_server_in(command: str):
    # サーバーが動いていれば、コマンドを送る
    if is_stopped_server(sys_logger):
        return
    process.stdin.write(command + "\n")
    process.stdin.flush()
    return