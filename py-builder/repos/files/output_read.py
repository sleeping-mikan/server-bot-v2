#!ignore
from ..imports import *
from ..constant import *
from ..logger.logger_create import *
#!end-ignore

#ローカルファイルの読み込み結果出力
sys_logger.info("instance root -> " + now_path)
sys_logger.info("read token file -> " + now_path + "/" +".token")
sys_logger.info("read config file -> " + now_path + "/" +".config")
view_config = config.copy()
view_config["web"]["secret_key"] = "****"
sys_logger.info("config -> " + str(view_config))
if config_changed: sys_logger.info("added config because necessary elements were missing")