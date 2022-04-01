import os

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

    os.makedirs(output_dir, exist_ok=True)
    if config["run_parallel"]:
        utilities.run_cmd(f"source {VSC}; mpiexec -n {num_procs} vorpal -i {basename}.in -o {output_dir}/{basename} {run_args}", capture_output=False)
    else:
        utilities.run_cmd(f"source {VSC}; vorpalser -i {basename}.in -o {output_dir}/{basename} {run_args}", capture_output=False)
