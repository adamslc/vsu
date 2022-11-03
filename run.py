import os
import shutil

import utilities
import make

def run(config):
    make.make(config)

    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    data_dir = config["data_dir"]

    txpp_args = config["txpp_args"]
    txpp_args = txpp_args.replace(" ", "_")
    txpp_args = txpp_args.replace("=", "-")

    if txpp_args != "":
        output_dir = f"{data_dir}/{txpp_args}"
    else:
        output_dir = data_dir

    run_args = config["vorpal_args"]

    if "license_path" in config:
        run_args += " --license-path " + config["license_path"]

    os.makedirs(output_dir, exist_ok=True)

    copy_runfiles(config, output_dir)

    print("Running simulation...", flush=True)
    if config["run_parallel"]:
        num_procs = 8
        utilities.run_cmd(f"source {VSC}; mpiexec -n {num_procs} vorpal -i {basename}.in -o {output_dir}/{basename} {run_args}", capture_output=False)
    else:
        utilities.run_cmd(f"source {VSC}; vorpalser -i {basename}.in -o {output_dir}/{basename} {run_args}", capture_output=False)

def copy_runfiles(config, output_dir):
    basename = config["basename"]
    build_dir = config["build_dir"]

    for ext in ["pre", "ppp", "in"]:
        shutil.copyfile(f"{build_dir}/{basename}.{ext}.generated", f"{output_dir}/{basename}.{ext}.generated")
        shutil.copyfile(f"{basename}.{ext}", f"{output_dir}/{basename}.{ext}")
