#!/usr/bin/env python3
import sys

import make
import config
import history

def get_txpp_args():
    if len(sys.argv) == 3:
        txpp_args = sys.argv[2]
    elif len(sys.argv) > 3:
        print("Too many args!")
        exit()
    else:
        txpp_args = ""

    return txpp_args

vsu_config = config.read_config()
if vsu_config == None:
    vsu_config = config.startup_wizzard()
config.write_config(vsu_config)

if len(sys.argv) < 2:
    print("No command given")
elif sys.argv[1] == "make":
    make.make(vsu_config, get_txpp_args())
    config.write_config(vsu_config)
elif sys.argv[1] == "run":
    make.make(vsu_config, get_txpp_args())
    config.write_config(vsu_config)
    make.run(vsu_config)
elif sys.argv[1] == "params":
    make.params(vsu_config)
elif sys.argv[1] == "update":
    make.update_patches(vsu_config)
    config.write_config(vsu_config)
elif sys.argv[1] == "clean":
    make.clean(vsu_config)
elif sys.argv[1] == "cleanall":
    make.cleanall(vsu_config)
elif sys.argv[1] == "history":
    history.history(vsu_config)
else:
    print("Unrecognized command")

