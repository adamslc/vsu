import os

import utilities
import config as cfg
import hash
import patch

def make(config):
    build_dir = config["build_dir"]
    txpp_args = config["txpp_args"]

    with open(f"{build_dir}/txpp_args", "w") as file:
        if txpp_args == None:
            txpp_args = ""

        file.write(txpp_args)

    if config["from_sdf"]:
        make_step(config, "pre", "sdf", generate_pre)
    make_step(config, "ppp", "pre", generate_ppp)
    make_step(config, "in", "ppp", generate_in)

def make_step(config, ext, parent_ext, make_func):
    basename = config["basename"]
    build_dir = config["build_dir"]

    hashes = hash.read_hashes(config)

    print(f"Making {basename}.{ext}...")
    print(f"  Checking if {basename}.{ext}.patch is up to date")
    patch.check_patch_up_to_date(config, ext)

    print(f"  Checking if {basename}.{ext} needs to be generated")
    do_make = False
    if hash.check_if_file_changed(hashes, f"{build_dir}/{basename}.{ext}.generated", f"{basename}.{parent_ext}"):
        print(f"    {basename}.{parent_ext} has changed")
        do_make = True
    if not os.path.exists(f"{build_dir}/{basename}.{ext}.generated"):
        print(f"    {basename}.{ext}.generated does not exist")
        do_make = True
    if hash.check_if_file_changed(hashes, f"{build_dir}/{basename}.{ext}.generated", f"{build_dir}/txpp_args"):
        print(f"    Build args for {basename}.{ext}.generated have changed")
        do_make = True

    if do_make:
        print(f"    Generating {basename}.{ext}.generated")
        make_func(config)
        print(f"    Updating hashes")
        hash.update_hash(config, f"{build_dir}/{basename}.{ext}.generated", f"{basename}.{parent_ext}")
        hash.update_hash(config, f"{build_dir}/{basename}.{ext}.generated", f"{build_dir}/txpp_args")
    else:
        print(f"    Skipping generation")

    print(f"  Checking if {basename}.{ext} needs to be patched")
    do_patch = False
    if hash.check_if_file_changed(hashes, f"{basename}.{ext}", f"{build_dir}/{basename}.{ext}.generated"):
        print(f"    {basename}.{ext}.generated has changed")
        do_patch = True
    if hash.check_if_file_changed(hashes, f"{basename}.{ext}", f"{basename}.{ext}.patch"):
        print(f"    {basename}.{ext}.patch has changed")
        do_patch = True
    if not os.path.exists(f"{basename}.{ext}"):
        print(f"    {basename}.{ext} does not exist")
        do_patch = True

    if do_patch:
        print(f"    Patching {basename}.{ext}")
        patch.apply_patch(config, ext)
        print(f"    Updating hashes")
        hash.update_hash(config, f"{basename}.{ext}", f"{build_dir}/{basename}.{ext}.generated")
        hash.update_hash(config, f"{basename}.{ext}", f"{basename}.{ext}.patch")
    else:
        print(f"    Skipping patching")

    hash.write_hashes(config, hashes)

def clean(config):
    basename = config["basename"]
    build_dir = config["build_dir"]

    cmd_str = f"rm -f {build_dir}/{basename}Vars.py {build_dir}/{basename}.pppVars.py {build_dir}/txpp_args "
    for ext in ["pre", "ppp", "in"]:
        patch.check_patch_up_to_date(config, ext)
        cmd_str += f"{build_dir}/{basename}.{ext}.generated {basename}.{ext} "

    utilities.run_cmd(cmd_str)

def cleanall(config):
    build_dir = config["build_dir"]
    clean(config)
    utilities.run_cmd(f"rm -r {build_dir}")

def run(config):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    data_dir = config["data_dir"]

    if os.path.exists(f"{build_dir}/txpp_args"):
        with open(f"{build_dir}/txpp_args", "r") as file:
            txpp_args = file.read()
    else:
        txpp_args = ""

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

def update_patches(config):
    for ext in ["pre", "ppp", "in"]:
        patch.make_patch(config, ext)

def params(config):
    build_dir = config["build_dir"]

    if os.path.exists(f"{build_dir}/txpp_args"):
        with open(f"{build_dir}/txpp_args", "r") as file:
            args = file.read()
            print(args)
    else:
        print("Something went wrong!")

# File generation

def generate_pre(config):
    VSC = config["VSC"]
    S2P = config["S2P"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    utilities.run_cmd(f"source {VSC}; {S2P} -s {basename}.sdf -p {build_dir}/{basename}.pre.generated")

def generate_ppp(config):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    utilities.run_cmd(f"source {VSC}; txpp.py -S . -q -p {basename}.pre -o {build_dir}/{basename}.ppp.generated")

def generate_in(config):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    txpp_args = config["txpp_args"]
    utilities.run_cmd(f"source {VSC}; txpp.py -q -p {basename}.ppp -o {build_dir}/{basename}.in.generated {txpp_args}")
