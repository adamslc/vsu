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
    # The ext check is a hack for now. It makes sure that updating txpp-args doesn't build more then required
    if ext == "in" and hash.check_if_file_changed(hashes, f"{build_dir}/{basename}.{ext}.generated", f"{build_dir}/txpp_args"):
        print(f"    Build args for {basename}.{ext}.generated have changed")
        do_make = True

    if do_make:
        print(f"    Generating {basename}.{ext}.generated")
        make_func(config)
        print(f"    Updating hashes")
        hash.update_hash(hashes, f"{build_dir}/{basename}.{ext}.generated", f"{basename}.{parent_ext}")
        hash.update_hash(hashes, f"{build_dir}/{basename}.{ext}.generated", f"{build_dir}/txpp_args")
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
        hash.update_hash(hashes, f"{basename}.{ext}", f"{build_dir}/{basename}.{ext}.generated")
        hash.update_hash(hashes, f"{basename}.{ext}", f"{basename}.{ext}.patch")
    else:
        print(f"    Skipping patching")

    hash.write_hashes(config, hashes)

def params(config):
    build_dir = config["build_dir"]

    if os.path.exists(f"{build_dir}/txpp_args"):
        with open(f"{build_dir}/txpp_args", "r") as file:
            args = file.read()
            print(args)
    else:
        print("Something went wrong!")

def get_params_str(config):
    build_dir = config["build_dir"]

    assert os.path.exists(f"{build_dir}/txpp_args")

    with open(f"{build_dir}/txpp_args", "r") as file:
        args = file.read()
        args = args.replace(" ", "_")
        # args = args.replace("=", "-")

    return args

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
