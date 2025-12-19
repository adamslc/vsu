import utilities
import patch

def clean(config):
    basename = config["basename"]
    build_dir = config["build_dir"]

    cmd_str = f"rm -f {build_dir}/{basename}Vars.py {build_dir}/{basename}.pppVars.py {build_dir}/txpp_args "
    for ext in ["pre", "ppp", "in"]:
        patch.check_patch_up_to_date(config, ext)
        if not (config["from_sdf"] == False and ext == "pre"):
            cmd_str += f"{build_dir}/{basename}.{ext}.generated {basename}.{ext} "

    utilities.run_cmd(cmd_str)

def cleanall(config):
    build_dir = config["build_dir"]
    clean(config)
    utilities.run_cmd(f"rm -r {build_dir}")
