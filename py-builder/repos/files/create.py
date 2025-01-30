#!ignore
from ..entry.read_args import *
from ..entry.auto_pip import *
from ..entry.standard_imports import *
from ..entry.variable import *
from ..logger.logger_create import *
from ..config.read_config_all import *
#!end-ignore


repository = {
    "user": "sleeping-mikan",
    "name": "server-bot-v2",
    "branch": update_branch,#!debug else main
}

def get_self_commit_id():
    url = f'https://api.github.com/repos/{repository["user"]}/{repository["name"]}/contents/server.py?ref={repository["branch"]}'
    response = requests.get(url)
    if response.status_code != 200:
        sys_logger.error("github api error. status code: " + str(response.status_code))
        return None
    commit_id = response.json()["sha"]
    return commit_id




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
def save_mikanassets_dat():
    if not os.path.exists(now_path + "/mikanassets"):
        os.makedirs(now_path + "/mikanassets")
    if not os.path.exists(os.path.join(now_path, "mikanassets", ".dat")):
        # 存在しなければデータファイルを作成する(現状 commit id 保管用)
        file = open(os.path.join(now_path, "mikanassets", ".dat"), "w")
        file.write('{"commit_id":' + f'"{get_self_commit_id()}"' + '}')
        file.close()
    # 全てが記憶されているわけでないなら
    if packages:
        file = open(os.path.join(now_path, "mikanassets", ".dat"), "r")
        jfile = json.load(file)
        file.close()
        file = open(os.path.join(now_path, "mikanassets", ".dat"), "w")
        # 必要な全てのパッケージが入っていることを記憶
        jfile["installed_packages"] = all_packages
        file.write(json.dumps(jfile, indent=4))
        file.close()
save_mikanassets_dat()
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

async def update_self_if_commit_changed(interaction: discord.Interaction | None = None,embed: ModifiedEmbeds.DefaultEmbed | None = None, text_pack: dict | None = None, sender = None, is_force = False):
    # ファイルが存在しなければ作る
    if not os.path.exists(os.path.join(now_path, "mikanassets", ".dat")):
        save_mikanassets_dat()
    file = open(os.path.join(now_path, "mikanassets", ".dat"))
    # 現在のserver.pyのコミットidを取り出す
    try:
        data = json.load(file)
        commit = data["commit_id"]
    except:
        if interaction is not None and embed is not None:
            embed.add_field(name="error", value="json load error (mikanassets/.dat). delete file.", inline=False)
            await sender(interaction=interaction,embed=embed)
        update_logger.error("json load error (mikanassets/.dat). delete file.")
    file.close()
    # github/mainのコミットidを取り出す
    github_commit = get_self_commit_id()
    update_logger.info("github commit -> " + github_commit)
    update_logger.info(" local commit -> " + commit)
    # 戻り値が正常でない場合
    if github_commit == None:
        if interaction is not None and embed is not None:
            embed.add_field(name="error", value="github response error.", inline=False)
            await sender(interaction=interaction,embed=embed)
        update_logger.error("github commit is None.")
    # コミットid出力
    if interaction is not None and embed is not None:
        embed.add_field(name="github commit", value=github_commit, inline=False)
        embed.add_field(name="local commit", value=commit, inline=False)
        await sender(interaction=interaction,embed=embed)
    # 更新がない場合
    if commit == github_commit and not is_force: 
        if interaction is not None and embed is not None:
            embed.add_field(name="", value=text_pack["same"], inline=False)
            await sender(interaction=interaction,embed=embed)
        update_logger.info("commit is same. no update.")
        return
    # ファイルに新しいcommit id を書き込む
    data["commit_id"] = github_commit
    file = open(os.path.join(now_path, "mikanassets", ".dat"), "w")
    json.dump(data, file)
    file.close()
    # ローカルとgithubのコードが違ったことを出力
    if interaction is not None and embed is not None:
        if is_force:
            embed.add_field(name="", value=text_pack["force"], inline=False)
        else:
            embed.add_field(name="", value=text_pack["different"], inline=False)
        await sender(interaction=interaction,embed=embed)
    update_logger.info("commit changed. update self.")
    # コードを要求
    url=f'https://api.github.com/repos/{repository["user"]}/{repository["name"]}/contents/server.py?ref={repository["branch"]}'
    # temp_path + "/new_source.py にダウンロード
    response = requests.get(url)
    if response.status_code != 200:
        sys_logger.error("response error. status_code : " + str(response.status_code))
        if interaction is not None and embed is not None:
            embed.add_field(name="error : raw.githubusercontent.com response error", value="", inline=False)
            await sender(interaction=interaction,embed=embed)
        return
    # temp_path + "/new_source.py に書き換え予定ファイル(新しいserver.py)を作成
    with open(temp_path + "/new_source.py", "w", encoding="utf-8") as f:
        f.write(base64.b64decode(response.json()["content"]).decode('utf-8').replace("\r\n","\n"))
    # discordにコードを置き換える
    msg_id = str(0)
    channel_id = str(0)
    if interaction is not None and embed is not None:
        msg_id = str((await interaction.original_response()).id)
        channel_id = str(interaction.channel_id)
        embed.add_field(name="", value=text_pack["replace"].format(channel_id,msg_id), inline=False)
        await sender(interaction=interaction,embed=embed)
    replace_logger.info("call update.py")
    replace_logger.info('replace args : ' + msg_id + " " + channel_id)
    os.execv(sys.executable,["python3",now_path + "/mikanassets/" + "update.py",temp_path + "/new_source.py",msg_id,channel_id,now_file])



make_token_file()
make_temp()
if is_auto_update:
    asyncio.run(update_self_if_commit_changed())