import os
import hashlib
import subprocess

def make(config, txpp_args):
    build_dir = config["build_dir"]

    if os.path.exists(f"{build_dir}/txpp_args"):
        os.remove(f"{build_dir}/txpp_args")

    if config["from_sdf"]:
        make_step(config, "pre", "sdf", generate_pre, None)
    make_step(config, "ppp", "pre", generate_ppp, None)
    make_step(config, "in", "ppp", generate_in, txpp_args)

    with open(f"{build_dir}/txpp_args", "w") as file:
        file.write(txpp_args)

def make_step(config, ext, parent_ext, make_func, args):
    basename = config["basename"]
    build_dir = config["build_dir"]

    print(f"Making {basename}.{ext}...")
    print(f"  Checking if {basename}.{ext}.patch is up to date")
    check_patch_up_to_date(config, ext)

    print(f"  Checking if {basename}.{ext} needs to be generated")
    do_make = False
    if check_if_file_changed(config, f"{build_dir}/{basename}.{ext}.generated", f"{basename}.{parent_ext}"):
        print(f"    {basename}.{parent_ext} has changed")
        do_make = True
    if not os.path.exists(f"{build_dir}/{basename}.{ext}.generated"):
        print(f"    {basename}.{ext}.generated does not exist")
        do_make = True
    if f"{build_dir}/{basename}.{ext}.generated" in config["hashes"]:
        if "args" in config["hashes"][f"{build_dir}/{basename}.{ext}.generated"]:
            if config["hashes"][f"{build_dir}/{basename}.{ext}.generated"]["args"] != args:
                print(f"    Build args for {basename}.{ext}.generated have changed")
                do_make = True
        else:
            print(f"    Args hash not recorded for {basename}.{ext}.generated")
            do_make = True
    else:
        print(f"    No hashes for product {basename}.{ext}.generated")
        do_make = True


    if do_make:
        print(f"    Generating {basename}.{ext}.generated")
        make_func(config, args)
        print(f"    Updating hashes")
        update_hash(config, f"{build_dir}/{basename}.{ext}.generated", f"{basename}.{parent_ext}")
        config["hashes"][f"{build_dir}/{basename}.{ext}.generated"]["args"] = args
    else:
        print(f"    Skipping generation")

    print(f"  Checking if {basename}.{ext} needs to be patched")
    do_patch = False
    if check_if_file_changed(config, f"{basename}.{ext}", f"{build_dir}/{basename}.{ext}.generated"):
        print(f"    {basename}.{ext}.generated has changed")
        do_patch = True
    if check_if_file_changed(config, f"{basename}.{ext}", f"{basename}.{ext}.patch"):
        print(f"    {basename}.{ext}.patch has changed")
        do_patch = True
    if not os.path.exists(f"{basename}.{ext}"):
        print(f"    {basename}.{ext} does not exist")
        do_patch = True

    if do_patch:
        print(f"    Patching {basename}.{ext}")
        apply_patch(config, ext)
        print(f"    Updating hashes")
        update_hash(config, f"{basename}.{ext}", f"{build_dir}/{basename}.{ext}.generated")
        update_hash(config, f"{basename}.{ext}", f"{basename}.{ext}.patch")
    else:
        print(f"    Skipping patching")

def clean(config):
    basename = config["basename"]
    build_dir = config["build_dir"]

    cmd_str = f"rm -f {build_dir}/{basename}Vars.py {build_dir}/{basename}.pppVars.py {build_dir}/txpp_args "
    for ext in ["pre", "ppp", "in"]:
        check_patch_up_to_date(config, ext)
        cmd_str += f"{build_dir}/{basename}.{ext}.generated {basename}.{ext} "

    run_cmd(cmd_str)

def cleanall(config):
    build_dir = config["build_dir"]
    clean(config)
    run_cmd(f"rm -r {build_dir}")

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

    options = " -nc "
    if config["start_dump"]:
        options += " -sd "

    os.makedirs(output_dir, exist_ok=True)
    run_cmd(f"source {VSC}; vorpalser -i {basename}.in -o {output_dir}/{basename} {options}", capture_output=False)

def update_patches(config):
    for ext in ["pre", "ppp", "in"]:
        make_patch(config, ext)

def params(config):
    build_dir = config["build_dir"]

    if os.path.exists(f"{build_dir}/txpp_args"):
        with open(f"{build_dir}/txpp_args", "r") as file:
            args = file.read()
            print(args)
    else:
        print("Something went wrong!")

# Utilities

def run_cmd(cmd_str, allow_failure=False, capture_output=True):
    output = subprocess.run(cmd_str, shell=True, capture_output=capture_output)
    if output.returncode != 0 and not allow_failure:
        if capture_output:
            stdout = output.stdout.decode()
            stderr = output.stderr.decode()

            print(f"ERROR [{output.returncode}]")
            print("===== STDOUT =====")
            for line in stdout.splitlines():
                print("  ", line)

            print("===== STDERR =====")
            for line in stderr.splitlines():
                print("  ", line)

        exit(output.returncode)

    if capture_output:
        return (output.returncode, output.stdout.decode())
    else:
        return (output.returncode, "")

def check_cmd_output(output):
    retcode = output[0]
    stdout = output[1]

def file_hash(filename):
    if not os.path.exists(filename):
        return ""

    with open(filename, "r") as file:
        hash = hashlib.md5(file.read().encode())
        return hash.hexdigest()

def update_hash(config, filename, parent_filename):
    if filename not in config["hashes"]:
        config["hashes"][filename] = {}

    config["hashes"][filename][parent_filename] = file_hash(parent_filename)

def check_if_file_changed(config, filename, parent_filename):
    if (not os.path.exists(filename)) or (filename not in config["hashes"]):
        return True

    return file_hash(parent_filename) != config["hashes"][filename][parent_filename]

# Patches

def compute_patch(config, ext):
    basename = config["basename"]
    build_dir = config["build_dir"]
    return run_cmd(f"diff -U3 {build_dir}/{basename}.{ext}.generated {basename}.{ext}", allow_failure=True)

def make_patch(config, ext):
    basename = config["basename"]
    returncode, patch = compute_patch(config, ext)

    patchfile = f"{basename}.{ext}.patch"
    if returncode == 1:
        with open(patchfile, "w") as output:
            output.write(patch)

def apply_patch(config, ext):
    basename = config["basename"]
    build_dir = config["build_dir"]
    cmd_str = f"cp {build_dir}/{basename}.{ext}.generated {basename}.{ext}"
    if os.path.exists(f"{basename}.{ext}.patch"):
        cmd_str += f"; patch < {basename}.{ext}.patch"
    run_cmd(cmd_str)

def check_patch_up_to_date(config, ext):
    basename = config["basename"]
    build_dir = config["build_dir"]

    if ((not os.path.exists(f"{build_dir}/{basename}.{ext}.generated")) or
            (not os.path.exists(f"{basename}.{ext}"))):
        return

    patchfile = f"{basename}.{ext}.patch"
    if os.path.exists(patchfile):
        with open(patchfile, "r") as file:
            contents = file.read()
            contents_cmp = "\n".join(contents.splitlines()[2:])
    else:
        contents = ""
        contents_cmp = ""

    returncode, patch = compute_patch(config, ext)
    patch_cmp = "\n".join(patch.splitlines()[2:])

    # The *_cmp variables strip off the patch header, which contains timestamps
    # that don't make sense to compare
    if patch_cmp == contents_cmp:
        return

    print(f"WARNING: Changes to {basename}.{ext} have not been recorded in {basename}.{ext}.patch and will be lost.")
    usr_in = input(f"Would you like to update {basename}.{ext}.patch first ([y]es/[n]o/[Q]uit)? ")

    if usr_in.lower() == "y":
        print(f"Writing updated patch file {basename}.{ext}.patch")
        with open(patchfile, "w") as file:
            file.write(patch)
        return
    elif usr_in.lower() == "n":
        return
    else:
        exit()

# File generation

def generate_pre(config, args):
    VSC = config["VSC"]
    S2P = config["S2P"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    run_cmd(f"source {VSC}; {S2P} -s {basename}.sdf -p {build_dir}/{basename}.pre.generated")

def generate_ppp(config, args):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    run_cmd(f"source {VSC}; txpp.py -S . -q -p {basename}.pre -o {build_dir}/{basename}.ppp.generated")

def generate_in(config, txpp_args):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    run_cmd(f"source {VSC}; txpp.py -q -p {basename}.ppp -o {build_dir}/{basename}.in.generated {txpp_args}")
