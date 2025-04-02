"""
configの読み込みと最小限の変数へのロードを行う
"""
#!ignore
from ..entry.standard_imports import *
from ..entry.variable import *
from ..wait_for_keypress import *
#!end-ignore


config_file_place = now_path + "/" + ".config"

def delete_config(config_dict):
    changed = False
    # v2.2.0まで存在した -> 現在はupdate keyに複数要素が存在している
    if "auto_update" in config_dict:
        del config_dict["auto_update"]
        changed = True
    return changed

def make_config():
    if not os.path.exists(config_file_place):
        file = open(config_file_place,"w")
        server_path = now_path
        default_backup_path = server_path + "/../backup/" + server_path.replace("\\","/").split("/")[-1]
        if not os.path.exists(default_backup_path):
            os.makedirs(default_backup_path)
        default_backup_path = os.path.realpath(default_backup_path) + "/"
        print("default backup path: " + default_backup_path)
        config_dict = {\
                            "allow":{"ip":True,"replace":False},\
                            "update":{
                                "auto":True,\
                                "branch":"main",\
                            },\
                            "server_path":now_path + "/",\
                            "server_name":"bedrock_server.exe",\
                            "server_args":"",\
                            "log":{"server":True,"all":False},\
                            
                            "mc":True,\
                            "web":{"secret_key":"YOURSECRETKEY","port":80},\
                            "discord_commands":{\
                                "cmd":{\
                                    "stdin":{\
                                        "sys_files": [".config",".token","logs","mikanassets"]
                                    },
                                    "serverin":{\
                                        "allow_mccmd":["list","whitelist","tellraw","w","tell"]\
                                    }\
                                },\
                                "terminal":{"discord":False,"capacity":"inf"},\
                                "stop":{"submit":"stop"},\
                                "backup":{"path": default_backup_path,},\
                                "admin":{"members":{}},\
                                "lang":"en",\
                            },\
                            "enable_advanced_features":False,\
                        }
        json.dump(config_dict,file,indent=4)
        config_changed = True
    else:
        try:
            config_dict = json.load(open(now_path + "/"  + ".config","r"))
            # 不要な要素があれば削除
            changed = delete_config(config_dict)
        except json.decoder.JSONDecodeError:
            print("config file is broken. please delete .config and try again.")
            wait_for_keypress()
        #要素がそろっているかのチェック
        def check(cfg):
            if "allow" not in cfg:
                cfg["allow"] = {"ip":True,"replace":False}
            if "ip" not in cfg["allow"]:
                cfg["allow"]["ip"] = True
            if "replace" not in cfg["allow"]:
                cfg["allow"]["replace"] = False

            if "update" not in cfg:
                cfg["update"] = {"auto":True,"branch":"main"}
            if "auto" not in cfg["update"]:
                cfg["update"]["auto"] = True
            if "branch" not in cfg["update"]:
                cfg["update"]["branch"] = "main"
            elif "ip" not in cfg["allow"]:
                cfg["allow"]["ip"] = True
            if "server_path" not in cfg:
                cfg["server_path"] = now_path + "/"
            if "server_args" not in cfg:
                cfg["server_args"] = ""
            if "discord_commands" not in cfg:
                cfg["discord_commands"] = {}
            if "cmd" not in cfg["discord_commands"]:
                cfg["discord_commands"]["cmd"] = {}
            if "stdin" not in cfg["discord_commands"]["cmd"]:
                cfg["discord_commands"]["cmd"]["stdin"] = {}
            if "sys_files" not in cfg["discord_commands"]["cmd"]["stdin"]:
                cfg["discord_commands"]["cmd"]["stdin"]["sys_files"] = [".config",".token","logs","mikanassets"]
            if "serverin" not in cfg["discord_commands"]["cmd"]:
                cfg["discord_commands"]["cmd"]["serverin"] = {}
            if "allow_mccmd" not in cfg["discord_commands"]["cmd"]["serverin"]:
                cfg["discord_commands"]["cmd"]["serverin"]["allow_mccmd"] = ["list","whitelist","tellraw","w","tell"]
            if "terminal" not in cfg["discord_commands"]:
                cfg["discord_commands"]["terminal"] = {"discord":False,"capacity":"inf"}
            if "discord" not in cfg["discord_commands"]["terminal"]:
                cfg["discord_commands"]["terminal"]["discord"] = False
            if "capacity" not in cfg["discord_commands"]["terminal"]:
                cfg["discord_commands"]["terminal"]["capacity"] = "inf"
            if "stop" not in cfg["discord_commands"]:
                cfg["discord_commands"]["stop"] = {"submit":"stop"}
            elif "submit" not in cfg["discord_commands"]["stop"]:
                cfg["discord_commands"]["stop"]["submit"] = "stop"
            if "admin" not in cfg["discord_commands"]:
                cfg["discord_commands"]["admin"] = {"members":{}}
            elif "members" not in cfg["discord_commands"]["admin"]:
                cfg["discord_commands"]["admin"]["members"] = {}
            if "lang" not in cfg["discord_commands"]:
                cfg["discord_commands"]["lang"] = "en"
            if "mc" not in cfg:
                cfg["mc"] = True
            if "server_name" not in cfg:
                cfg["server_name"] = "bedrock_server.exe"
            if "log" not in cfg:
                cfg["log"] = {"server":True,"all":False}
            else:
                if "server" not in cfg["log"]:
                    cfg["log"]["server"] = True
                if "all" not in cfg["log"]:
                    cfg["log"]["all"] = False
            if "backup" not in cfg["discord_commands"]:
                try:
                    server_name = cfg["server_path"].replace("\\","/").split("/")[-2]
                except IndexError:
                    print(f"server_path is broken. please check config file and try again.\ninput : {cfg['server_path']}")
                    wait_for_keypress()
                if server_name == "":
                    print("server_path is broken. please check config file and try again.")
                    wait_for_keypress()
                cfg["discord_commands"]["backup"] = {}
                cfg["discord_commands"]["backup"]["path"] = cfg["server_path"] + "../backup/" + server_name
                cfg["discord_commands"]["backup"]["path"] = os.path.realpath(cfg["discord_commands"]["backup"]["path"]) + "/"
                if not os.path.exists(cfg["discord_commands"]["backup"]["path"]):
                    os.makedirs(cfg["discord_commands"]["backup"]["path"])
            if "mc" not in cfg:
                cfg["mc"] = True
            if "web" not in cfg:
                cfg["web"] = {"secret_key":"YOURSECRETKEY","port":80}
            if "port" not in cfg["web"]:
                cfg["web"]["port"] = 80
            if "secret_key" not in cfg["web"]:
                cfg["web"]["secret_key"] = "YOURSECRETKEY"
            if "enable_advanced_features" not in cfg:
                cfg["enable_advanced_features"] = False
            # バージョン移行処理
            # v2.0.0までは、admin.membersがlistで管理されていた(当時の権限レベルは現在の1に該当する。)
            if type(cfg["discord_commands"]["admin"]["members"]) == list:
                users = {}
                for user in cfg["discord_commands"]["admin"]["members"]:
                    users[str(user)] = 1
                cfg["discord_commands"]["admin"]["members"] = users
                print("admin.members is list. format changed to dict.(this version isv2.1.0 or later)")
            return cfg
        checked_config = check(deepcopy(config_dict))
        if config_dict != checked_config or changed:
            config_dict = checked_config
            file = open(now_path + "/"  + ".config","w")
            #ログ
            config_changed = True
            json.dump(config_dict,file,indent=4)
            file.close()
            print("config file is changed.")
        else: config_changed = False
    return config_dict,config_changed
def to_config_safe(config):
    #"force_admin"に重複があれば削除する
    save = False
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