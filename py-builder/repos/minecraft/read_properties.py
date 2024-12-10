#!ignore
from ..imports import *
from ..constant import *
from ..config.read_config_minimum import *
from ..config.read_config_all import *
#!end-ignore


#java properties の読み込み
def properties_to_dict(filename):
    properties = {}
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith(' ') or line.startswith('\t'):
                        line = line[1:]
                    key, value = line.split('=', 1)
                    properties[key] = value
        return properties
    except Exception as e:#ファイルが存在しなければ存在しないことを出力して終了
        sys_logger.error(e)
        sys_logger.info("not exist server.properties file in " + server_path + ". if you are not using a minecraft server, please set mc to false in .config .if not, restart it and server.properties should be generated in the server hierarchy.")
        return {}

#minecraftサーバーであればpropertiesを読み込む
if config["mc"]:
    properties = properties_to_dict(server_path + "server.properties")
    sys_logger.info("read properties file -> " + server_path + "server.properties")

#コマンド利用ログ
use_stop = False