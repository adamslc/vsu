import os

import utilities

def compute_patch(config, ext):
    basename = config["basename"]
    build_dir = config["build_dir"]
    return utilities.run_cmd(f"diff -U3 --label generated --label modified {build_dir}/{basename}.{ext}.generated {basename}.{ext}", allow_failure=True)

def make_patch(config, ext):
    basename = config["basename"]
    returncode, patch = compute_patch(config, ext)

    patchfile = f"{basename}.{ext}.patch"
    if returncode == 1:
        print(f"Updating {patchfile}")
        with open(patchfile, "w") as output:
            output.write(patch)
    else:
        print(f"File {basename}.{ext} has no changes from generated file")

def apply_patch(config, ext):
    basename = config["basename"]
    build_dir = config["build_dir"]
    cmd_str = f"cp {build_dir}/{basename}.{ext}.generated {basename}.{ext}"
    if os.path.exists(f"{basename}.{ext}.patch"):
        cmd_str += f"; patch < {basename}.{ext}.patch"
    utilities.run_cmd(cmd_str)

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

def update_patches(config):
    for ext in ["pre", "ppp", "in"]:
        make_patch(config, ext)
