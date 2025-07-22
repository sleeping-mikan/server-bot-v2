#!ignore 
import sys
#!end-ignore

args = sys.argv[1:]
do_init = False
#引数を処理する。
for i in args:
    arg = i.split("=")
    if arg[0] == "-init":
        do_init = True