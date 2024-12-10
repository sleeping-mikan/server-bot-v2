"""
configの読み込みと最小限の変数へのロードを行う
"""
#!ignore
from ..imports import *
from ..constant import *
from ..wait_for_keypress import *
#!end-ignore


config_file_place = now_path + "/" + ".config"

def make_config():
    if not os.path.exists(config_file_place):
        file = open(config_file_place,"w")
        server_path = now_path
        default_backup_path = server_path + "/../backup/" + server_path.split("/")[-1]
        if not os.path.exists(default_backup_path):
            os.makedirs(default_backup_path)
        default_backup_path = os.path.realpath(default_backup_path) + "/"
        print("default backup path: " + default_backup_path)
        config_dict = {"allow":{"ip":True},"server_path":now_path + "/","allow_mccmd":["list","whitelist","tellraw","w","tell"],"server_name":"bedrock_server.exe","log":{"server":True,"all":False},"stop":{"submit":"stop"},"backup_path": default_backup_path,"mc":True,"lang":"en","force_admin":[],"web":{"secret_key":"YOURSECRETKEY","port":80},"terminal":{"discord":False,"capacity":"inf"}}
        json.dump(config_dict,file,indent=4)
        config_changed = True
    else:
        try:
            config_dict = json.load(open(now_path + "/"  + ".config","r"))
        except json.decoder.JSONDecodeError:
            print("config file is broken. please delete .config and try again.")
            wait_for_keypress()
        #要素がそろっているかのチェック
        def check(cfg):
            if "allow" not in cfg:
                cfg["allow"] = {"ip":True}
            elif "ip" not in cfg["allow"]:
                cfg["allow"]["ip"] = True
            if "server_path" not in cfg:
                cfg["server_path"] = now_path + "/"
            if "allow_mccmd" not in cfg:
                cfg["allow_mccmd"] = ["list","whitelist","tellraw","w","tell"]
            if "server_name" not in cfg:
                cfg["server_name"] = "bedrock_server.exe"
            if "log" not in cfg:
                cfg["log"] = {"server":True,"all":False}
            else:
                if "server" not in cfg["log"]:
                    cfg["log"]["server"] = True
                if "all" not in cfg["log"]:
                    cfg["log"]["all"] = False
            if "stop" not in cfg:
                cfg["stop"] = {"submit":"stop"}
            else:
                if "submit" not in cfg["stop"]:
                    cfg["stop"]["submit"] = "stop"
            if "backup_path" not in cfg:
                try:
                    server_name = cfg["server_path"].split("/")[-2]
                except IndexError:
                    print(f"server_path is broken. please check config file and try again.\ninput : {cfg['server_path']}")
                    wait_for_keypress()
                if server_name == "":
                    print("server_path is broken. please check config file and try again.")
                    wait_for_keypress()
                cfg["backup_path"] = cfg["server_path"] + "../backup/" + server_name
                cfg["backup_path"] = os.path.realpath(cfg["backup_path"]) + "/"
                if not os.path.exists(cfg["backup_path"]):
                    os.makedirs(cfg["backup_path"])
            if "mc" not in cfg:
                cfg["mc"] = True
            if "lang" not in cfg:
                cfg["lang"] = "en"
            if "force_admin" not in cfg:
                cfg["force_admin"] = []
            if "web" not in cfg:
                cfg["web"] = {"secret_key":"YOURSECRETKEY","port":80}
            if "port" not in cfg["web"]:
                cfg["web"]["port"] = 80
            if "secret_key" not in cfg["web"]:
                cfg["web"]["secret_key"] = "YOURSECRETKEY"
            if "terminal" not in cfg:
                cfg["terminal"] = {"discord":False,"capacity":"inf"}
            else:
                if "discord" not in cfg["terminal"]:
                    cfg["terminal"]["discord"] = False
                if "capacity" not in cfg["terminal"]:
                    cfg["terminal"]["capacity"] = "inf"
            return cfg
        if config_dict != check(config_dict.copy()):
            check(config_dict)
            file = open(now_path + "/"  + ".config","w")
            #ログ
            config_changed = True
            json.dump(config_dict,file,indent=4)
            file.close()
        else: config_changed = False
    return config_dict,config_changed
def to_config_safe(config):
    #"force_admin"に重複があれば削除する
    save = False
    if len(config["force_admin"]) > len(set(config["force_admin"])):
        config["force_admin"] = list(set(config["force_admin"]))
        save = True
    if save:
        file = open(config_file_place,"w")
        json.dump(config,file,indent=4)
        file.close()

config,config_changed = make_config()
#整合性チェック
to_config_safe(config)
#ロガー作成前なので最小限の読み込み
try:
    log = config["log"]
    server_path = config["server_path"]
    if not os.path.exists(server_path):
        print("not exist server_path dir")
        wait_for_keypress()
    #ログファイルの作成
    def make_logs_file():
        #./logsが存在しなければlogsを作成する
        if not os.path.exists(now_path + "/" + "logs"):
            os.makedirs(now_path + "/" + "logs")
        if not os.path.exists(server_path + "logs"):
            os.makedirs(server_path + "logs")
    make_logs_file()
except KeyError:
    print("(log or server_path) in config file is broken. please input true or false and try again.")
    wait_for_keypress()