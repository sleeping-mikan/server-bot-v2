from os import getcwd, path, listdir
from logging import Logger, StreamHandler, Formatter
from json import load



builder_logger: Logger = Logger("builder")
builder_logger.setLevel("INFO")
builder_logger.addHandler(StreamHandler())
log_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
builder_logger.handlers[0].setFormatter(log_format)
mi_file = "code.mi"
mi = path.dirname(__file__) + "/code.mi"
mi.replace("\\", "/")
flgs = {"ignore":False}

config = load(open(path.dirname(__file__) + "/config.json","r",encoding="utf-8"))
output_path = getcwd() + "/" + config["out"]

def write_code(code: list[str | list],file):
    for i in range(len(code)):
        line = code[i]
        if type(line) == str:
            file.write(line)
        else:
            file.write("\n#--------------------\n\n")
            write_code(line, file)
            file.write("\n#--------------------\n\n")


def inter_code(code: list[str | list]):
    for i in range(len(code)):
        line = code[i]
        if line[-1] == "\n":
            line = line[:-1]
        if flgs["ignore"]:
            builder_logger.info(f"ignore line -> {line}({i + 1})")
            if "#!end-ignore" in line:
                builder_logger.info(f"found end ignore -> {line}({i + 1})")
                flgs["ignore"] = False
            code[i] = ""
            continue
        if "#!open" in line:
            builder_logger.info(f"found #!open -> {line}")
            item = line.split(" ")
            if len(item) <= 1:
                builder_logger.error("#!open need an argument -> #!open <filename>")
                exit(0)
            if len(item) >= 3:
                builder_logger.error("#!open need only one argument -> #!open <filename>")
            if item[1][0] == ".":
                item[1] = path.dirname(__file__) + item[1]
            builder_logger.info(f"open file -> {item[1]}")
            try:
                read = open(item[1], "r",encoding="utf-8") # ファイルを開く
            except FileNotFoundError:
                builder_logger.error(f"File not found -> {item[1]}")
                exit(0)
            code[i] = read.readlines() # ファイルを読み込む
            builder_logger.info(f"expansion file -> {item[1]}")
            inter_code(code[i]) # 再帰的に展開する
            builder_logger.info(f"end expansion file -> {item[1]}")
            read.close()
            builder_logger.info(f"copy file to line {[i]}")
        if "#!ignore" in line:
            builder_logger.info(f"ignore line -> {line}")
            flgs["ignore"] = True
            code[i] = ""


def search_files_starting_with(prefix, directory='.'):
    builder_logger.info(f"search files -> {prefix} in {directory} {listdir(directory)}")
    items = [f for f in listdir(directory) if f.startswith(prefix)]
    if len(items) > 1:
        builder_logger.warning(f"Multiple files found -> {items}")
    builder_logger.info(f"found files -> {items}")
    return items

def main():
    try:
        code = open(path.dirname(__file__) + "/" + search_files_starting_with(mi_file,path.dirname(__file__))[0], "r",encoding="utf-8")
        builder_logger.info(f"open file -> {search_files_starting_with(mi_file,path.dirname(__file__))[0]}")
    except FileNotFoundError as e: 
        builder_logger.error(f"File not found -> {mi}")
        builder_logger.error(e)
        exit(0)
    codes = code.readlines()
    code.close()
    inter_code(codes)
    write_file = open(output_path, "w", encoding="utf-8")
    # builder_logger.info(f"write data -> {codes}")
    write_code(codes,write_file)
    write_file.close()
    builder_logger.info(f"end write data")

if __name__ == "__main__":
    main()