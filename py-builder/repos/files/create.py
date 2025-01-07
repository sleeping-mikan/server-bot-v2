#!ignore
from ..imports import *
from ..constant import *
from ..logger.logger_create import *
#!end-ignore

def get_self_commit_id():
    repos = f"{repository['user']}/{repository['name']}"
    branch = repository["branch"]
    url = "https://api.github.com/repos/" + repos + "/commits/" + branch

    response = requests.get(url)
    commit_id = response.json()["sha"]
    return commit_id

args = sys.argv[1:]
do_init = False

#引数を処理する。
for i in args:
    arg = i.split("=")
    if arg[0] == "-init":
        do_init = True
        # pass

is_first_run = False

# mikanassets/extensionフォルダを作成
if not os.path.exists(now_path + "/mikanassets/extension"):
    # 最初の起動の場合にはフラグを立てておく
    is_first_run = True
    os.makedirs(now_path + "/mikanassets/extension")

#updateプログラムが存在しなければdropboxから./update.pyにコピーする
if not os.path.exists(now_path + "/mikanassets"):
    os.makedirs(now_path + "/mikanassets")
if not os.path.exists(now_path + "/mikanassets/" + "update.py") or do_init:
    url='https://www.dropbox.com/scl/fi/zo824cfk88uj52sospwo6/update_v2.2.py?rlkey=vwkh78smhdbm2pnfyegyxjpgf&st=6wdv9o5w&dl=1'
    filename= now_path + '/mikanassets/' + 'update.py'

    urlData = requests.get(url).content

    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)
if not os.path.exists(os.path.join(now_path, "mikanassets", ".dat")):
    # 存在しなければデータファイルを作成する(現状 commit id 保管用)
    file = open(os.path.join(now_path, "mikanassets", ".dat"), "w")
    file.write('{"commit_id":' + f'"{get_self_commit_id()}"' + '}')
    file.close()
    #os.system("curl https://www.dropbox.com/scl/fi/w93o5sndwaiuie0otorm4/update.py?rlkey=gh3gqbt39iwg4afey11p99okp&st=2i9a9dzp&dl=1 -o ./update.py")
if not os.path.exists(now_path + "/mikanassets/web"):
    os.makedirs(now_path + "/mikanassets/web")
if not os.path.exists(now_path + "/mikanassets/web/index.html") or do_init:
    url='https://www.dropbox.com/scl/fi/04to7yrstmgdz9j09ljy2/index.html?rlkey=7q8eu0nooj8zy34dguwwsbkjd&st=4cb6y9sr&dl=1'
    filename= now_path + '/mikanassets/web/index.html'
    urlData = requests.get(url).content
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)
if not os.path.exists(now_path + "/mikanassets/web/login.html") or do_init:
    url='https://www.dropbox.com/scl/fi/6yuq2dhqozxeh8vxj8wgy/login.html?rlkey=9w9tbevra7r9vwjeofslb8j0x&st=sxtayji2&dl=1'
    filename= now_path + '/mikanassets/web/login.html'
    urlData = requests.get(url).content
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)
#mikanassets/web/usr/tokens.jsonを作成
if not os.path.exists(now_path + "/mikanassets/web/usr"):
    os.makedirs(now_path + "/mikanassets/web/usr")
if not os.path.exists(now_path + "/mikanassets/web/usr/tokens.json"):
    #ファイルを作成
    tokenfile_items = {"tokens":[]}
    file = open(now_path + "/mikanassets/web/usr/tokens.json","w",encoding="utf-8")
    file.write(json.dumps(tokenfile_items,indent=4))
    file.close()
    del tokenfile_items
if not os.path.exists(now_path + "/mikanassets/web/pictures"):
    os.makedirs(now_path + "/mikanassets/web/pictures")
if not os.path.exists(now_path + "/mikanassets/web/pictures/icon.png") or do_init:
    url = 'https://www.dropbox.com/scl/fi/cr6uejk7s2vk4zevm8zc6/boticon.png?rlkey=szuisf29w1rnynz9xs9ucr24l&st=a8kuy1fd&dl=1'
    filename= now_path + '/mikanassets/web/pictures/icon.png'
    urlData = requests.get(url).content
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)

def read_web_tokens():
    file = open(now_path + "/mikanassets/web/usr/tokens.json","r",encoding="utf-8")
    tokens = json.load(file)["tokens"]
    file.close()
    return tokens

web_tokens = read_web_tokens()

def make_token_file():
    global token
    #./.tokenが存在しなければ.tokenを作成する
    if not os.path.exists(now_path + "/" + ".token"):
        file = open(now_path + "/" + ".token","w",encoding="utf-8")
        file.write("ここにtokenを入力")
        file.close()
        sys_logger.error("please write token in" + now_path + "/" +".token")
        #ブロッキングする
        wait_for_keypress()
    #存在するならtokenを読み込む(json形式)
    else:
        token = open(now_path + "/" + ".token","r",encoding="utf-8").read()

def make_temp():
    global temp_path
    #tempファイルの作成場所
    if platform.system() == 'Windows':
        # %temp%/mcserver を作成
        temp_path = os.environ.get('TEMP') + "/mcserver"
    else:
        # /tmp/mcserver を作成
        temp_path = "/tmp/mcserver"

    #tempファイルの作成
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

def update_self_if_commit_changed():
    file = open(os.path.join(now_path, "mikanassets", ".dat"))
    try:
        data = json.load(file)
        commit = data["commit_id"]
    except:
        sys_logger.error("json load error (mikanassets/.dat). delete file and retry.")
    file.close()
    if commit == get_self_commit_id(): return

    sys_logger.info("commit changed. update self.")
    url='https://raw.githubusercontent.com/' + repository['user'] + '/' + repository['name'] + '/' + repository['branch'] + "/" + "server.py"
    # temp_path + "/new_source.py にダウンロード
    response = requests.get(url)
    with open(temp_path + "/new_source.py", "wb") as f:
        f.write(response.content.decode("utf-8").replace("\r\n","\n"))
    # discordにコードを置き換える
    replace_logger.info('replace done')
    replace_logger.info("call update.py")
    replace_logger.info('replace args : ' +  "None None")
    os.execv(sys.executable,["python3",now_path + "/mikanassets/" + "update.py",temp_path + "/new_source.py",None,None,now_file])

make_token_file()
make_temp()
update_self_if_commit_changed()