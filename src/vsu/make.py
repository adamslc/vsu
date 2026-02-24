import os

from vsu import utilities
from vsu import config as cfg
from vsu import hash
from vsu import patch

def make(config):
    build_dir = config["build_dir"]
    txpp_args = config["txpp_args"]
    basename = config["basename"]

    if 'prefix_dir' not in config:
        config['prefix_dir'] = '.'
    prefix_dir = config['prefix_dir']

    if prefix_dir != ".":
        if config["from_sdf"]:
            rotate_file(config, f"{prefix_dir}/{basename}.sdf")
            utilities.run_cmd(f"cp {basename}.sdf {prefix_dir}")
        else:
            rotate_file(config, f"{prefix_dir}/{basename}.pre")
            utilities.run_cmd(f"cp {basename}.pre {prefix_dir}")

        if os.path.exists(f"{basename}.sdf.patch"):
            utilities.run_cmd(f"cp {basename}.sdf.patch {prefix_dir}")
        if os.path.exists(f"{basename}.pre.patch"):
            utilities.run_cmd(f"cp {basename}.pre.patch {prefix_dir}")
        if os.path.exists(f"{basename}.ppp.patch"):
            utilities.run_cmd(f"cp {basename}.ppp.patch {prefix_dir}")
        if os.path.exists(f"{basename}.in.patch"):
            utilities.run_cmd(f"cp {basename}.in.patch {prefix_dir}")

    with open(f"{prefix_dir}/{build_dir}/txpp_args", "w") as file:
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
    prefix_dir = config["prefix_dir"]

    hashes = hash.read_hashes(config)

    if "force_make" not in config:
        config["force_make"] = False

    print(f"Making {prefix_dir}/{basename}.{ext}...")
    if prefix_dir == ".":
        print(f"  Checking if {basename}.{ext}.patch is up to date")
        patch.check_patch_up_to_date(config, ext)
    else:
        print(f"  Making at {prefix_dir}, so skipping patch check")

    print(f"  Checking if {prefix_dir}/{basename}.{ext} needs to be generated")
    do_make = config["force_make"]
    if hash.check_if_file_changed(hashes, f"{prefix_dir}/{build_dir}/{basename}.{ext}.generated", f"{prefix_dir}/{basename}.{parent_ext}"):
        print(f"    {prefix_dir}/{basename}.{parent_ext} has changed")
        do_make = True
    if not os.path.exists(f"{prefix_dir}/{build_dir}/{basename}.{ext}.generated"):
        print(f"    {prefix_dir}/{basename}.{ext}.generated does not exist")
        do_make = True
    # The ext check is a hack for now. It makes sure that updating txpp-args doesn't build more then required
    if ext == "in" and hash.check_if_file_changed(hashes, f"{prefix_dir}/{build_dir}/{basename}.{ext}.generated", f"{prefix_dir}/{build_dir}/txpp_args"):
        print(f"    Build args for {prefix_dir}/{build_dir}/{basename}.{ext}.generated have changed")
        do_make = True

    if do_make:
        print(f"    Rotating {prefix_dir}/{basename}.{ext} and {prefix_dir}/{build_dir}/{basename}.{ext}.generated")
        rotate_file(config, f"{prefix_dir}/{basename}.{ext}")
        rotate_file(config, f"{prefix_dir}/{build_dir}/{basename}.{ext}.generated")
        print(f"    Generating {prefix_dir}/{build_dir}/{basename}.{ext}.generated")
        make_func(config)
        print(f"    Updating hashes")
        hash.update_hash(hashes, f"{prefix_dir}/{build_dir}/{basename}.{ext}.generated", f"{prefix_dir}/{basename}.{parent_ext}")
        hash.update_hash(hashes, f"{prefix_dir}/{build_dir}/{basename}.{ext}.generated", f"{prefix_dir}/{build_dir}/txpp_args")
    else:
        print(f"    Skipping generation")

    print(f"  Checking if {prefix_dir}/{basename}.{ext} needs to be patched")
    do_patch = config["force_make"]
    if hash.check_if_file_changed(hashes, f"{prefix_dir}/{basename}.{ext}", f"{prefix_dir}/{build_dir}/{basename}.{ext}.generated"):
        print(f"    {prefix_dir}/{build_dir}/{basename}.{ext}.generated has changed")
        do_patch = True
    if hash.check_if_file_changed(hashes, f"{prefix_dir}/{basename}.{ext}", f"{prefix_dir}/{basename}.{ext}.patch"):
        print(f"    {prefix_dir}/{basename}.{ext}.patch has changed")
        do_patch = True
    if not os.path.exists(f"{prefix_dir}/{basename}.{ext}"):
        print(f"    {prefix_dir}/{basename}.{ext} does not exist")
        do_patch = True

    if do_patch:
        print(f"    Patching {prefix_dir}/{basename}.{ext}")
        patch.apply_patch(config, ext)
        print(f"    Updating hashes")
        print(f"      {prefix_dir}/{build_dir}/{basename}.{ext}.generated")
        print(f"      {prefix_dir}/{basename}.{ext}.patch")

        hash.update_hash(hashes, f"{prefix_dir}/{basename}.{ext}", f"{prefix_dir}/{build_dir}/{basename}.{ext}.generated")
        hash.update_hash(hashes, f"{prefix_dir}/{basename}.{ext}", f"{prefix_dir}/{basename}.{ext}.patch")
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

# Recursively renames files with the same name, but with a number appended to the end
def rotate_file(config, filename):
    if os.path.exists(f"{filename}.1"):
        rotate_file_recurse(config, filename, 1)
    if os.path.exists(filename):
        os.rename(filename, f"{filename}.1")

def rotate_file_recurse(config, filename, num):
    if os.path.exists(f"{filename}.{num + 1}"):
        rotate_file_recurse(config, filename, num + 1)
    os.rename(f"{filename}.{num}", f"{filename}.{num + 1}")

# File generation

def generate_pre(config):
    VSC = config["VSC"]
    S2P = config["S2P"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    prefix_dir = config["prefix_dir"]
    utilities.run_cmd(f"source {VSC}; {S2P} -s {prefix_dir}/{basename}.sdf -p {prefix_dir}/{build_dir}/{basename}.pre.generated")

def generate_ppp(config):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    prefix_dir = config["prefix_dir"]
    utilities.run_cmd(f"source {VSC}; txpp.py -S . -q -p {prefix_dir}/{basename}.pre -o {prefix_dir}/{build_dir}/{basename}.ppp.generated")

def generate_in(config):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    txpp_args = config["txpp_args"]
    extra_txpp_args = config["extra_txpp_args"]
    prefix_dir = config["prefix_dir"]
    utilities.run_cmd(f"source {VSC}; txpp.py -q -p {prefix_dir}/{basename}.ppp -o {prefix_dir}/{build_dir}/{basename}.in.generated {txpp_args} {extra_txpp_args}")
