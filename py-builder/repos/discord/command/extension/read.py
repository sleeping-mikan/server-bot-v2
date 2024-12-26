#!ignore
from ....imports import *
from ....constant import *
from ....logger.logger_create import *
from ....minecraft.read_properties import *
from ....assets.text_dat import *
from ....assets.utils import *
#!end-ignore
base_extension_logger.info("search extension commands")
extension_commands_group = None
extension_logger = None
def read_extension_commands():
    global extension_commands_group,extension_logger
    extension_commands_groups = deque()
    sys_logger.info("read extension commands ->" + now_path + "/mikanassets/extension")
    # 拡張moduleに追加コマンドが存在すればするだけ読み込む(mikanassets/extension/<拡張名>/commands.py)
    for file in os.listdir(now_path + "/mikanassets/extension"):
        if os.path.isdir(now_path + "/mikanassets/extension/" + file):
            sys_logger.info("read extension commands ->" + now_path + "/mikanassets/extension/" + file)
            if os.path.exists(now_path + "/mikanassets/extension/" + file + "/commands.py"):
                # <拡張名>コマンドグループを作成
                extension_commands_group = app_commands.Group(name=file,description="This commands group is extention.\nUse this code at your own risk." + file)
                extension_commands_groups.append(extension_commands_group)
                # 拡張moduleが/mikanassets/extension/<拡張名>/commans.pyにある場合は読み込む
                try:
                    extension_logger = base_extension_logger.getChild(file)
                    importlib.import_module("mikanassets.extension." + file + ".commands")
                    # コマンドを追加
                    tree.add_command(extension_commands_group)
                    sys_logger.info("read extension commands success -> " + now_path + "/mikanassets/extension/" + file + "/commands.py")
                except Exception as e:
                    sys_logger.info("cannot read extension commands " + now_path + "/mikanassets/extension/" + file + "/commands.py" + f"({e})")
            else:
                sys_logger.info("not exist extension commands file in " + now_path + "/mikanassets/extension/" + file + "/commands.py")
        else:
            sys_logger.info("not directory -> " + now_path + "/mikanassets/extension/" + file)

    unti_GC_obj.append(extension_commands_groups)

# mikanassets/extension/<extension_dir>にディレクトリが存在すれば
if os.path.exists(now_path + "/mikanassets/extension"):
    if len(os.listdir(now_path + "/mikanassets/extension")) > 0:
        # 拡張コマンドを読み込む
        read_extension_commands()
    else:
        sys_logger.info("no extension commands in " + now_path + "/mikanassets/extension")
del extension_commands_group

