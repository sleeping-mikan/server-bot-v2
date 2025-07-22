#!ignore
import uvicorn.config
from ..imports import *
from ..constant import *
from ..logger.logger_create import *
from ..config.read_config_minimum import *
from ..config.read_config_all import *
from ..assets.utils import *
from ..files.create import *
from ..assets.core._header import *
from ..discord.command.cmd.stdin.send_discord.selfserver import *
#!end-ignore


app = Flask(__name__,template_folder="mikanassets/web",static_folder="mikanassets/web")
app.secret_key = flask_secret_key
flask_logger = create_logger("werkzeug",Formatter.WebFormatter("FLASK",f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt),Formatter.WebConsoleFormatter("FLASK",'%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt=dt_fmt))
uvicorn_logger_err = create_logger("uvicorn.error",Formatter.WebFormatter("UVICORN",f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt),Formatter.WebConsoleFormatter("UVICORN",'%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt=dt_fmt))
uvicorn_logger = create_logger("uvicorn.access",Formatter.WebFormatter("UVICORN",f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt),Formatter.WebConsoleFormatter("UVICORN",'%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt=dt_fmt))

class ExcludeGetConsoleDataFilter(logging.Filter):
    def filter(self, record):
        # record.args はログ出力の引数、record.msg が生ログ文字列
        # "GET /get_console_data" を含むかどうかを確認
        return "/get_console_data" not in str(record.getMessage())
for logger in [flask_logger,uvicorn_logger_err,uvicorn_logger]:
    logger.addFilter(ExcludeGetConsoleDataFilter())
# def get_uvicorn_custom_log_config():
#     from uvicorn.config import LOGGING_CONFIG
#     uvicorn_custom_log_config = LOGGING_CONFIG.copy()
#     uvicorn_custom_log_config["formatters"]["default"]["fmt"] = f'{Color.BOLD + Color.BLACK}%(asctime)s {Color.BOLD + Color.CYAN}UVICORN  {Color.RESET.value}%(name)s: %(message)s'
#     uvicorn_custom_log_config["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
#     uvicorn_custom_log_config["formatters"]["access"]["fmt"] = f'{Color.BOLD + Color.BLACK}%(asctime)s {Color.BOLD + Color.CYAN}UVICORN  {Color.RESET.value}%(name)s: %(message)s'
#     uvicorn_custom_log_config["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

#     class ExcludeGetConsoleDataFilter(logging.Filter):
#         def filter(self, record):
#             # record.args はログ出力の引数、record.msg が生ログ文字列
#             # "GET /get_console_data" を含むかどうかを確認
#             return "/get_console_data" not in str(record.getMessage())

#     uvicorn_custom_log_config["filters"] = {
#         "exclude_get_console_data": {
#             "()": ExcludeGetConsoleDataFilter,
#         }
#     }
#     uvicorn_custom_log_config["handlers"]["access"]["filters"] = ["exclude_get_console_data"]
#     return uvicorn_custom_log_config

# fastapi_logger = [
#     create_logger("uvicorn.access", Formatter.WebFormatter("UVICORN",f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt), Formatter.WebConsoleFormatter("UVICORN",'%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt=dt_fmt)),
#     create_logger("uvicorn", Formatter.WebFormatter("UVICORN",f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt), Formatter.WebConsoleFormatter("UVICORN",'%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt=dt_fmt)),
#     create_logger("uvicorn.error", Formatter.WebFormatter("UVICORN",f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt), Formatter.WebConsoleFormatter("UVICORN",'%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt=dt_fmt)),

#     ]

class LogIPMiddleware:
    def __init__(self, app):
        self.app = app
        # self.before_log = {"Client IP": "", "Method": "", "URL": "", "Query": ""}

    def __call__(self, environ, start_response):
        # クライアントのIPアドレスを取得
        client_ip = environ.get('REMOTE_ADDR', '')
        # リクエストされたURLを取得
        request_method = environ.get('REQUEST_METHOD', '')
        request_uri = environ.get('PATH_INFO', '')
        query_string = environ.get('QUERY_STRING', '')

        # ログに記録
        if request_uri != "/get_console_data":
            flask_logger.info(f"Client IP: {client_ip}, Method: {request_method}, URL: {request_uri}, Query: {query_string}")

        return self.app(environ, start_response)
    
# class LogIPMiddlewareASGI:
#     def __init__(self, app):
#         self.app = app

#     async def __call__(self, scope, receive, send):
#         if scope["type"] == "http":
#             client = scope.get("client")
#             method = scope.get("method")
#             path = scope.get("path")
#             query_string = scope.get("query_string", b"").decode("utf-8")

#             if path != "/get_console_data":
#                 client_ip = client[0] if client else "unknown"
#                 flask_logger.info(
#                     f"Client IP: {client_ip}, Method: {method}, URL: {path}, Query: {query_string}"
#                 )

#         await self.app(scope, receive, send)

# ミドルウェアをアプリに適用
app.wsgi_app = LogIPMiddleware(app.wsgi_app)


# トークンをロードする
def load_tokens():
    tokens = set()
    try:
        items = web_tokens
        now = datetime.now()
        for token in items:
            if datetime.strptime(token["deadline"], "%Y-%m-%d %H:%M:%S") > now:
                tokens.add(token["token"])
        return tokens
    except FileNotFoundError:
        flask_logger.info(f"Token file not found: {WEB_TOKEN_FILE}")
        return {}

# トークンを検証する
def is_valid_token(token):
    tokens = load_tokens()
    return token in tokens

def is_valid_session(token):
    if 'token' not in session:
        # ログアウトにリダイレクトするためのフラグを返す
        return False
    if not is_valid_token(session['token']):
        #ログアウト
        # ログアウトにリダイレクトするためのフラグを返す
        return False
    return True


# クッキーからトークンを取得し、セッションにセット
@app.before_request
def load_token_from_cookie():
    token = request.cookies.get('token')
    if token and is_valid_token(token):
        session['token'] = token

@app.route('/', methods=['GET', 'POST'])
def index():
    # セッションにトークンがある場合、ログイン済み
    if 'token' in session:
        if is_valid_token(session['token']):
            return render_template('index.html', logs = log_msg)

    # ログアウトさせられた場合理由を表示
    if 'logout_reason' in session:
        flash(session['logout_reason'])
        session.pop('logout_reason') 

    if request.method == 'POST':
        token = request.form['token']
        if is_valid_token(token):
            # トークンをセッションとクッキーに保存
            session['token'] = token
            resp = make_response(redirect(url_for('index')))
            
            # クッキーにトークンを保存、有効期限を30日間に設定
            expires = datetime.now() + timedelta(days=30)
            resp.set_cookie('token', token, expires=expires)

            return resp
        else:
            flash('Invalid token, please try again.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # セッションとクッキーからトークンを削除してログアウト
    session.pop('token', None)
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('token', '', expires=0)  # クッキーを無効化
    return resp

# @app.route('/')
# def index():
#     return render_template('index.html', logs = log_msg)

@app.route('/get_console_data')
def get_console_data():
    if not is_valid_session(session['token']):
        # ログアウト
        session["logout_reason"] = "This token has expired. create new token."
        return jsonify({"redirect": url_for('logout')})
    
    converter = Ansi2HTMLConverter()
    html_string = converter.convert("\n".join(log_msg))

    try:
        server_online = process.poll() is None#サーバーが起動している = True
    except:
        if process is not None:
            process.kill()
        server_online = False

    bot_online = True

    return jsonify({"html_string": html_string, "online_status": {"server": server_online, "bot": bot_online}})


@app.route('/flask_start_server', methods=['POST'])
def flask_start_server():
    if not is_valid_session(session['token']):
        # ログアウト
        session["logout_reason"] = "This token has expired. create new token."
        return jsonify({"redirect": url_for('logout')})
    result = core_start()
    if result == RESPONSE_MSG["other"]["is_running"]:
        return jsonify(RESPONSE_MSG["other"]["is_running"])
    return jsonify(result)

@app.route('/flask_backup_server', methods=['POST'])
def flask_backup_server():
    if not is_valid_session(session['token']):
        # ログアウト
        session["logout_reason"] = "This token has expired. create new token."
        return jsonify({"redirect": url_for('logout')})
    world_name = request.form['fileName']
    if "\\" in world_name or "/" in world_name:
        return jsonify(RESPONSE_MSG["backup"]["not_allowed_path"] + ":" + server_path + world_name)
    if process is None:
        if os.path.exists(server_path + world_name):
            backup_logger.info("backup server")
            to = backup_path + "/" + datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
            copytree(server_path + world_name,to)
            backup_logger.info("backuped server to " + to)
            return jsonify("backuped server!! " + to)
        else:
            backup_logger.info('data not found : ' + server_path + world_name)
            return jsonify(RESPONSE_MSG["backup"]["data_not_found"] + ":" + server_path + world_name)
    else:
        return jsonify(RESPONSE_MSG["other"]["is_running"])

@app.route('/submit_data', methods=['POST'])
def submit_data():
    global use_stop
    if not is_valid_session(session['token']):
        # ログアウト
        session["logout_reason"] = "This token has expired. create new token."
        return jsonify({"redirect": url_for('logout')})
    user_input = request.form['userInput']
    #サーバーが起きてるかを確認
    if process is None:
        return jsonify("server is not running")
    #ifに引っかからない = サーバーが起動している

    #もし入力されたコマンドがstopだったら
    if user_input == STOP:
        use_stop = True

    #サーバーの標準入力に入力
    process.stdin.write(user_input + "\n")
    process.stdin.flush()

    # データを処理し、結果を返す（例: メッセージを返す）
    return jsonify(f"result: {user_input}")

def run_webservice_server():
    fastapi_app = SendDiscordSelfServer.create_app()
    if use_flask_server:
        fastapi_app.mount("/", WSGIMiddleware(app))
    # fastapi_app = LogIPMiddlewareASGI(fastapi_app)
    uvicorn.run(fastapi_app, host="0.0.0.0", port=web_port, log_config=None)

    
web_thread = threading.Thread(target=run_webservice_server, daemon=True)
web_thread.start()

