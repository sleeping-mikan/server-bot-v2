#!ignore
from .....imports import *
from .....constant import *
from .....logger.logger_create import *
from .....minecraft.read_properties import *
from .....assets.text_dat import *
from .....assets.utils import *
from ..common import *
#!end-ignore

stdin_logger = cmd_logger.getChild("stdin")

#サブグループstdinを作成
command_group_cmd_stdin = app_commands.Group(name="stdin",description="stdin group")
# サブグループを設定
command_group_cmd.add_command(command_group_cmd_stdin)


important_bot_file = [
    pathlib.Path(os.path.abspath(os.path.join(os.path.dirname(__file__),i))).resolve() for i in sys_files
] + [
    pathlib.Path(os.path.join(server_path,i)).resolve() for i in sys_files
]



# 重要ファイルでないか(最高権限要求するようなファイルかを確認)
async def is_important_bot_file(path):
    # 絶対パスを取得
    path = pathlib.Path(os.path.abspath(path)).resolve()
    # 重要ファイルの場合はTrueを返す
    for f in important_bot_file:
        if path == f or path.is_relative_to(f):
            return True
    return False