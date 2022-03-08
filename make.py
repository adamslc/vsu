import os
import hashlib
import subprocess

def make(config):
    if config["from_sdf"]:
        make_step(config, "pre", "sdf", generate_pre)
    make_step(config, "ppp", "pre", generate_ppp)
    make_step(config, "in", "ppp", generate_in)

def make_step(config, ext, parent_ext, make_func):
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

    if do_make:
        print(f"    Generating {basename}.{ext}.generated")
        make_func(config)
        print(f"    Updating hashes")
        update_hash(config, f"{build_dir}/{basename}.{ext}.generated", f"{basename}.{parent_ext}")
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

    cmd_str = f"rm -f {build_dir}/{basename}Vars.py {build_dir}/{basename}.pppVars.py "
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
    data_dir = config["data_dir"]

    options = " -nc "
    if config["start_dump"]:
        options += " -sd "

    os.makedirs(data_dir, exist_ok=True)
    run_cmd(f"source {VSC}; vorpalser -i {basename}.in -o {data_dir}/{basename} {options}", capture_output=False)

def update_patches(config):
    for ext in ["pre", "ppp", "in"]:
        make_patch(config, ext)

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
            contents = "\n".join(contents.splitlines()[2:])
    else:
        contents = ""

    returncode, patch = compute_patch(config, ext)
    patch = "\n".join(patch.splitlines()[2:])

    if patch == contents:
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

def generate_pre(config):
    VSC = config["VSC"]
    S2P = config["S2P"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    run_cmd(f"source {VSC}; {S2P} -s {basename}.sdf -p {build_dir}/{basename}.pre.generated")

def generate_ppp(config):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    run_cmd(f"source {VSC}; txpp.py -S . -q -p {basename}.pre -o {build_dir}/{basename}.ppp.generated")

def generate_in(config):
    VSC = config["VSC"]
    basename = config["basename"]
    build_dir = config["build_dir"]
    run_cmd(f"source {VSC}; txpp.py -q -p {basename}.ppp -o {build_dir}/{basename}.in.generated")
