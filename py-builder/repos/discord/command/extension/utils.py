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