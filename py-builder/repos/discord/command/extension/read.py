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
    extension_path = normalize_path(now_path + "/mikanassets/extension")
    sys_logger.info("read extension commands ->" + extension_path)
    # 拡張moduleに追加コマンドが存在すればするだけ読み込む(mikanassets/extension/<拡張名>/commands.py)
    for file in os.listdir(extension_path):
        extension_file_path = normalize_path(extension_path + "/" + file)
        extension_command_file_path = normalize_path(extension_file_path + "/commands.py")
        if os.path.isdir(now_path + "/mikanassets/extension/" + file):
            sys_logger.info("read extension commands ->" + extension_file_path)
            if os.path.exists(extension_command_file_path):
                # <拡張名>コマンドグループを作成
                extension_commands_group = app_commands.Group(name="extension-" + file,description="This commands group is extention.\nUse this code at your own risk." + file)
                extension_commands_groups.append(extension_commands_group)
                # 拡張moduleが/mikanassets/extension/<拡張名>/commans.pyにある場合は読み込む
                try:
                    extension_logger = base_extension_logger.getChild(file)
                    importlib.import_module("mikanassets.extension." + file + ".commands")
                    # コマンドを追加
                    tree.add_command(extension_commands_group)
                    sys_logger.info("read extension commands success -> " + extension_command_file_path)
                except Exception as e:
                    sys_logger.info("cannot read extension commands " + extension_command_file_path + f"({e})")
            else:
                sys_logger.info("not exist extension commands file in " + extension_command_file_path)
        else:
            sys_logger.info("not directory -> " + extension_file_path)

    unti_GC_obj.append(extension_commands_groups)

extension_path = normalize_path(now_path + "/mikanassets/extension")
# mikanassets/extension/<extension_dir>にディレクトリが存在すれば
if os.path.exists(extension_path):
    if len(os.listdir(extension_path)) > 0:
        # 拡張コマンドを読み込む
        read_extension_commands()
    else:
        sys_logger.info("no extension commands in " + extension_path)
del extension_commands_group
del extension_path
