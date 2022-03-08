#!/usr/bin/env python3
import sys

import make
import config
import history

vsu_config = config.read_config()
if vsu_config == None:
    vsu_config = config.startup_wizzard()

if len(sys.argv) < 2:
    print("No command given")
elif sys.argv[1] == "make":
    make.make(vsu_config)
    config.write_config(vsu_config)
elif sys.argv[1] == "run":
    make.make(vsu_config)
    config.write_config(vsu_config)
    make.run(vsu_config)
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

