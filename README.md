# server-bot

## 対応言語

This bot supports English and Japanese.(このbotは英語と日本語をサポートしています。)

For the Readme, writing an English version is currently under consideration.(Readmeについては英語版を記述することを現在検討中です。)

## 目的

このbotはサーバーを管理するためのdiscord bot/webツールです。

discordを用いて特定のサーバーを管理できます。

ここでの管理とは起動/停止/ログ取得/入出力などを行うことを指します。

## コマンド一覧(できること)

プログラムに含まれるdiscord botコマンドは以下の通りです。

なお、必要権限レベルは同階層に生成される.configから変更できます。

|コマンド|実行結果|初期必要権限レベル|
|----|----|----|
|help|discord上にhelpとwebリンクを表示します。webサイトへ外部からアクセスするには追加のポート開放が必要です。 |0|
|ip|このbot(サーバー)を実行しているipアドレスを返します。|0(configにより有効/無効)|
|start|サーバーを開始します。但し、server.py起動時には自動的に開始されます。|1|
|stop|サーバーを停止します。但しserver.pyは実行状態から遷移しないため他のコマンドを使用できます。|1|
|exit|server.pyを終了します(このコマンドを利用すると次回サーバー管理者がserver.pyを起動するまでbotを利用できません)。サーバー停止中にのみ使用できます。|2|
|backup create <path(optional)>|サーバーデータをバックアップします。引数が与えられない場合`./worlds`をバックアップします。|1|
|backup apply <path(optional)>|バックアップを指定したディレクトリに展開します。引数が与えられない場合直下に展開します。|3|
|cmd serverin <server command>|サーバーに対してコマンドを送信します。|1|
|cmd stdin ls <path(optional)>|ディレクトリ内のファイル一覧を返します。rootディレクトリはサーバー直下になります。|2(*2)|
|cmd stdin mk <path> <file(optional)>|ファイルを作成または上書きします。file引数を渡さない場合空のファイルを作成します。|3(*1)|
|cmd stdin rm <path>|指定したファイルが存在する場合削除します。|2(*1)|
|cmd stdin rmdir <path>|指定したディレクトリが存在する場合削除します。このコマンドは指定したディレクトリ内に対して再帰的に適用されます。|2(*1)|
|cmd stdin mkdir <path>|指定したディレクトリを作成します。|2(*2)|
|cmd stdin send-discord <path>|指定したディレクトリをdiscordに送信します。使用するにはwebポートが解放されている必要があります。|2(*2)|
|cmd stdin wget <url> <path(optional)>|指定したパスのファイルをurlから得られるデータで上書きします。path引数を渡さない場合直下にファイルを生成します。|3(*1)|
|cmd stdin mv <src> <dest>|指定したpathをdestに移動させます。|3(*1)|
|logs <file(optional)>|サーバーログを表示します。引数が与えられる場合には該当のファイルを、与えられない場合には現在のサーバーログを表示できる限り表示します。|1|
|lang <"ja"/"en">|サーバーの言語を変更します。|2|
|permission change <level> <user>|ユーザーのbot利用権限を操作します。|4|
|permission view <user> <detail True/False>|プレイヤーの権限を表示します。|0|
|tokengen|webアクセスのためのtokenを生成します。webログイン画面で入力してください。|1|
|update <force True/False>|githubにアクセスして最新のserver.pyをダウンロードします。force引数を与えると強制的にダウンロードします。|3|
|announce <text/file>|通常のテキストまたは[mimd](https://github.com/sleeping-mikan/server-bot-v2/blob/main/py-builder/mimd.md)形式のテキストまたはファイルを指定してbotとしてdiscordにメッセージを送信します。テキストの場合改行には\nを利用してください|4|
|terminal set <ch(optional)>|discordのチャンネルIDを与えるとサーバーのログをdiscordに送信します。また標準入力を受け取ります|1|
|terminal del|ターミナルの紐づけを解除します|1|
|status|現在のサーバーの状態を表示します|0|

*1 : 一部のファイル/ディレクトリに対する操作は行えません。ただしdiscord管理者権限を保持した上で、config上のenable_advanced_featuresをtrueにすることで操作可能となります。

*2 : 一部のファイル/ディレクトリに対する操作は行えません。

これらコマンドの設定等は後述の使用方法を参照してください。

## 必要なもの

現在使用していないdiscord bot

> [!WARNING]
> [discord developers](https://discord.com/developers/applications)にて該当のbotからSettings>Bot>Privileged Gateway Intents>Message Content Intentを許可してください。

言語：python3.12.x

ライブラリ：requirements.txtを参照 (PowerShellや管理者権限のあるCmd/ubuntu+bashの場合は、server.pyが自動でインストール出来ることを確認済み。)

## 使用方法

### 配置

server.pyを任意の場所に配置します。

> [!note]
> 推奨ディレクトリは実行するserver.[exe/jar]が存在する階層です。この場所をrootディレクトリとして一部の権限を持ったdiscordユーザーはファイル操作を行えます。

> [!note]
> ただしserver.exeやserver.jar本体が存在する階層はroot(windowsの場合c:/直下など)でない必要があります。(何かのディレクトリの中に入れてください)これは初期状態では、`../backup/`内にbackupが生成されるためです。

### 実行

ライブラリのインストール(`pip install -r requirements.txt`)後、server.pyを実行します。

server.pyを実行するとserver.pyと同じ階層に`.config`と`.token`が生成されます。

コンソール引数(これらは任意であるため、エラーが発生した場合などに利用してください)
 - `-init` update.pyなどの一部server.pyがダウンロードするファイルを再度ダウンロード (update.pyなどの[server_path]/mikanassetsが破損している場合に有効です)

> [!note]
> この際.tokenが生成されない場合、.config内のserver_path+server_nameが存在していないので、サーバーが存在するパス+拡張子を含むサーバーの名前に変更してください


### 初期設定

.tokenにdiscord botのtokenを記述してください。

.configの操作は必須ではないので後述します。

このとき同時に`mikanassets`が生成されますが、これは`/repalce`を実行する際やwebにアクセスするために必要なファイルです。

tokenを記述し、configのserver_pathにserver.[exe/bat(jarを実行するファイル)]へのパスを記述後に再度server.pyを起動すると正常に起動するはずです。このプログラムはserver.pyがサーバー本体を呼び出すためserver.[exe/jar/bat]を自身で起動する必要はありません。

> [!WARNING]
> server.jar(java edition)を起動する場合基本的には`java -Xmx4048M -Xms1024M -Dfile.encoding=UTF-8 -jar server.jar nogui`と記述されたbatファイル(Windowsの場合)を作成しserver_pathに記載してください。

### .config

./configは初期生成では以下のような内容で構成されています。

```json
{
    "allow": {
        "ip": true
    },
    "auto_update": true,
    "server_path": "path/to/serverdir/",
    "server_name": "bedrock_server.exe",
    "server_args": "",
    "server_char_encoding": "utf-8",
    "log": {
        "server": true,
        "all": false
    },
    "mc": true,
    "web": {
        "secret_key": "****",
        "port": 80,
        "use_front_page": true
    },
    "discord_commands": {
        "permission": {
            "commands_level": {
                "stop": 1,
                "start": 1,
                "exit": 2,
                "cmd serverin": 1,
                "cmd stdin mk": 3,
                "cmd stdin rm": 2,
                "cmd stdin mkdir": 2,
                "cmd stdin rmdir": 2,
                "cmd stdin ls": 2,
                "cmd stdin mv": 3,
                "cmd stdin send-discord": 2,
                "cmd stdin wget": 3,
                "help": 0,
                "backup create": 1,
                "backup apply": 5,
                "ip": 5,
                "logs": 1,
                "permission view": 0,
                "permission change": 4,
                "lang": 2,
                "tokengen": 1,
                "terminal set": 1,
                "terminal del": 1,
                "update": 3,
                "announce embed": 4,
                "status": 0
            }
        },
        "cmd": {
            "stdin": {
                "sys_files": [
                    ".config",
                    ".token",
                    "logs",
                    "mikanassets"
                ],
                "send_discord": {
                    "bits_capacity": 2147483648
                }
            },
            "serverin": {
                "allow_mccmd": [
                    "to server",
                    "allow input commands",
                ]
            }
        },
        "terminal": {
            "discord": <(optional) output to discord channel id>,
            "capacity": "inf"
        },
        "stop": {
            "submit": "stop"
        },
        "backup": {
            "path": "path/to/backup/",
        },
        "admin": {
            "members": {}
        },
        "lang": "ja"
    }
    "enable_advanced_features": false
}
```

|項目|説明|
|---|---|
|allow|各コマンドの実行を許可するかどうか。(現在は/ipにのみ実装されています)|
|auto_update|サーバー本体を自動更新するか否か|
|server_path|server本体のパス(例えば`D:\\a\\server.jar`に配置されていれば`D:\\a\\`または`D:/a/`)|
|server_name|server本体の名前 java版minecraftの場合サーバ起動に利用される`server.bat`等を入力してください(GUI起動させないでください)|
|server_args|server起動時のコンソール引数。例えばTerrariaを起動する場合`-world /path/to/world.wld`を入力してください|
|server_char_encoding|serverのコンソール出力を受け取る際に使用する文字コードを入力します|
|log|各種ログを保存するか否か serverをtrueにするとmcサーバーの実行ログをmcserverと同じディレクトリに保存し、allをtrueにするとすべてのログをserver.pyと同じディレクトリに保存します|
|mc|サーバーがmcサーバーかどうかを記述します。現在trueに設定されている場合、/ip時にserver.propertiesからserver-portを読み出します|
|web.secret_key|Flaskで利用する鍵を設定します。(app.secret_key)十分に強固な文字列を設定してください。|
|web.port|webサーバーのポート番号を入力します。なお、/cmd stdin send-discordにおいてもこのポート番号を利用します|
|web.use_front_page|webサーバーページからの操作を許可するか否か(Falseの場合にもファイルをやり取りはできます。)|
|discord_commands.permission.commands_level|すべてのコマンドについて、必要な権限を定義するためのリスト(コマンド実行には書き込まれた値以上の権限が必要)|
|discord_commands.cmd.stdin.sys_files|/cmd stdin <mv/rmdir/rm/wget/mv>において、権限を持っていても操作を拒否するファイルのリスト|
|discord_commands.cmd.stdin.send_discord.bits_capacity|/cmd stdin send-discordにおいて、送信を許可するファイルの最大容量|
|discord_commands.cmd.serverin.allow_mccmd|/cmdで標準入力を許可するコマンド名のリスト|
|discord_commands.terminal.discord|コンソールとして扱うチャンネルidを指定します。通常configを直接操作しません。指定したチャンネルではサーバー起動中の入出力が可能になります(但し、allow_mccmdで許可されている命令のみ)。|
|discord_commands.terminal.capacity|discordにコンソール出力する予定の文字列長の最大を設定します。デフォルトでは送信に時間がかかったとしてもデータを捨てません。|
|discord_commands.stop.submit|/stopコマンドが入力された際にサーバーの標準入力へ送信するコマンドを設定します。|
|discord_commands.backup.path|ワールドデータのバックアップパス(例えば`D:\\server\\backup`に保存したければ`D:\\server\\backup\\`または`D:/server/backup/`)|
|discord_commands.admin.members|サーバー内の管理者権限を操作します。通常configを直接操作しません。permission changeコマンドを用いてbot管理者を設定できます。|
|discord_commands.lang|discordに送信するメッセージの言語を選択します。(en : 英語, ja : 日本語)|
|enable_advanced_features|discord上で管理者権限を持っている場合に、discord_commands.cmd.stdin.sys_filesに含まれるファイルを操作可能にするか否か|

server.pyはサーバ本体と同じ階層に配置することを推奨します。


## web上での操作

ホストipアドレス:<configで設定したport>を用いて操作することができます。

アクセス時にtokenを要求されるため、discordで`/tokengen`を実行しtokenを入手してください。

httpsを用いて実行する場合(推奨)リバースプロキシを利用してください。

## 動作確認済み環境(必要環境)
<details>
    <summary>クリックして確認済み環境例を表示</summary>
    <table>
        <thread>
            <th>確認バージョン</th>
            <th>日時</th>
            <th>確認時のOS</th>
            <th>python</th>
            <th>備考</th>
        </thread>
        <tbody>
            <tr>
                <td>Minecraft Java vanilla 1.9.4</td>
                <td>2024/06/26</td>
                <td>Windows 11</td>
                <td>python 3.12.1</td>
                <td>下記に示すbatを利用</td>
            </tr>
            <tr>
                <td>Minecraft Java vanilla 1.19</td>
                <td>2024/06/26</td>
                <td>Windows 11</td>
                <td>python 3.12.1</td>
                <td>下記に示すbatを利用</td>
            </tr>
            <tr>
                <td>Minecraft Java vanilla 1.19.4</td>
                <td>2024/07/31</td>
                <td>Windows 11</td>
                <td>python 3.12.1</td>
                <td>下記に示すbatを利用</td>
            </tr>
            <tr>
                <td>Minecraft Java fabric 1.20.1</td>
                <td>2024/06/26</td>
                <td>Windows 11</td>
                <td>python 3.12.1</td>
                <td>下記に示すbatを利用</td>
            </tr>
            <tr>
                <td>Minecraft Bedrock dedicated server 1.21</td>
                <td>2025/01/30</td>
                <td>Windows 11 & Ubuntu(wsl2)</td>
                <td>python 3.12.1</td>
                <td></td>
            </tr>
            <tr>
                <td>TShock-5.2.1-for-Terraria-1.4.4.9</td>
                <td>2025/01/25</td>
                <td>Windows 11</td>
                <td>python 3.12.1</td>
                <td>.configのserver_argsに`-world /path/to/world.wld`を指定</td>
            </tr>
        </tbody>
    </table>
</details>

 - 想定環境
   - os : ubuntu(wsl2) / windows11 / windows10
   - python : 3.12.x
   - server : 任意

なおテストを行ったわけではありませんが、python3.8台、python3.10台での動作も確認済みです。ただし、3.8を利用する場合configの相対パスは絶対パスに置き換えてください。

java版serverをWindowsで起動する際一般に利用されるような以下の内容のbatをconfigのserver_nameに設定しています。noguiオプションが無い場合現在/stop等が利用できません。(fabric : start.bat , forge : run.bat)

> [!WARNING]
> -Dfile.encoding=UTF-8が存在しない場合一部環境で特殊文字等が正常に表示されません。またpauseのようなコマンドを記載しないでください。(このプログラムはサーバーを制御するプログラムです。それ以外のコマンドを実行しないでください。)

`java -Xmx4048M -Xms1024M -Dfile.encoding=UTF-8 -jar server.jar nogui`
 
## 拡張機能

拡張機能を追加する場合server.pyと同じディレクトリのmikanassets/extensionに配置してください。

構造は`mikanassets/extension/拡張機能名/拡張機能を実装したファイル群`となります。

拡張機能の実装仕様は[server-bot-extensions](https://github.com/sleeping-mikan/server-bot-extensions)で確認できます。

### 動作画面

以下の動画はダウンロード後のserver.pyを起動し、コマンドを実行する動画です。

![server.mp4](https://github.com/mikatan-mikan/server-bot/assets/78290592/32df51eb-7166-40a8-b817-e1057d2aabd0)

以下の画像は、webアクセス時の画面です。(PC/スマホ)

![PCサイズ](https://github.com/user-attachments/assets/a1b09ad4-9fde-4df9-abd8-cb6628589a67)![スマホサイズ](https://github.com/user-attachments/assets/6b59139f-363d-4a92-b7c8-398ed9d03d78)