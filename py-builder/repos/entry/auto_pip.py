#!ignore
from .standard_imports import *
from .read_args import *
#!end-ignore



# インストールしたいパッケージのリスト（パッケージ名: バージョン）
packages = {
    "discord.py": "2.3.2",
    "requests": "2.32.2",
    "Flask": "3.0.3",
    "ansi2html": "1.9.2",
    "waitress": "3.0.0",
    "aiohttp": "3.9.5",
    "psutil": "5.9.0"
}
all_packages = [f"{pkg}=={ver}" for pkg, ver in packages.items()]

def get_mikanassets_dat_lib():
    now_path = "/".join(__file__.replace("\\","/").split("/")[:-1])
    try:
        file = open(now_path + "/mikanassets/.dat", "r")
        jfile = json.load(file)
        file.close()
        return jfile["installed_packages"]
    except Exception as e:
        return []

already_install_packages = get_mikanassets_dat_lib()
if do_reinstall:
    already_install_packages = []
for item in already_install_packages: 
    pkg, ver = item.split("==")
    # バージョンが一致していれば、確認対象から削除
    if pkg not in packages:
        print(f"not exist package in need packages: {pkg}")
        continue
    if ver == packages[pkg]:
        del packages[pkg]


# パッケージがすでにインストールされているかを確認する関数
def is_package_installed(package, version):
    print(f"Checking if {package} is installed with version {version}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    installed_version = line.split(":", 1)[1].strip()
                    return installed_version == version
        return False
    except subprocess.CalledProcessError:
        return False

# インストールが必要なパッケージをリストアップ
install_packages = [f"{pkg}=={ver}" for pkg, ver in packages.items() if not is_package_installed(pkg, ver)]

# 必要なパッケージのみインストール
if install_packages:
    print(f"Installing the following packages: {', '.join(install_packages)}")
    subprocess.run([sys.executable, "-m", "pip", "install", *install_packages], check=True)