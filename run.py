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
        if config["output_dir_override"] == "":
            output_dir = f"{data_dir}/{txpp_args}"
        else:
            output_dir = f"{data_dir}/{config['output_dir_override']}"
    else:
        output_dir = data_dir

    run_args = config["vorpal_args"]

    if "license_path" in config:
        run_args += " --license-path " + config["license_path"]

    os.makedirs(output_dir, exist_ok=True)

    copy_runfiles(config, output_dir)

    if config['restart_simulation'] == -1:
        restart_dump = find_last_dump(config, output_dir)
    elif config['restart_simulation'] > 0:
        restart_dump = config['restart_simulation']

    if config['restart_simulation'] >= -1:
        restart_str = f'-r {restart_dump}'
    else:
        restart_str = ' '


    print("Running simulation...", flush=True)
    if config["run_parallel"]:
        num_procs = 8
        utilities.run_cmd(f"source {VSC}; mpiexec -n {num_procs} vorpal -i {basename}.in -o {output_dir}/{basename} {restart_str} {run_args}", capture_output=False)
    else:
        utilities.run_cmd(f"source {VSC}; vorpalser -i {basename}.in -o {output_dir}/{basename} {restart_str} {run_args}", capture_output=False)

def copy_runfiles(config, output_dir):
    basename = config["basename"]
    build_dir = config["build_dir"]

    for ext in ["pre", "ppp", "in"]:
        if not (config["from_sdf"] == False and ext == "pre"):
            shutil.copyfile(f"{build_dir}/{basename}.{ext}.generated", f"{output_dir}/{basename}.{ext}.generated")

        if not (config["from_sdf"] == False and ext == "sdf"):
            shutil.copyfile(f"{basename}.{ext}", f"{output_dir}/{basename}.{ext}")

def find_last_dump(config, output_dir):
    files = os.listdir(output_dir)
    basename = config["basename"]
    filtered_files = filter( lambda file: file.startswith(f'{basename}_Globals_') , files)

    def isolate_num(file):
        num_and_ext = file.split('_')[-1]
        num_str = num_and_ext.split('.')[0]
        return int(num_str)

    isolated_nums = list(map(isolate_num, filtered_files))
    return max(isolated_nums)
