import os
import yaml

def find_basenames():
    files = os.listdir()

    basenames = []

    for file in files:
        ext = file.split(".")[-1]
        if ext == "sdf":
            basenames.append(".".join(file.split(".")[0:-1]))

    return basenames

def required_input(prompt):
    ans = ""
    while True:
        ans = input(prompt)
        if ans != "":
            return ans

def input_with_default(prompt, default):
    ans = input(prompt)
    if ans == "":
        return default
    else:
        return ans

def advanced_input(prompt, default, advanced):
    if not advanced:
        return default
    else:
        return input_with_default(prompt, default)

def find_exec_path(vsc_path, exec_name):
    if os.path.exists(vsc_path + "/engine/bin/" + exec_name):
        return vsc_path + "/engine/bin/" + exec_name
    elif os.path.exists(vsc_path + "/Contents/engine/bin/" + exec_name):
        return vsc_path + "/Contents/engine/bin/" + exec_name
    else:
        return ""

def startup_wizzard(advanced=False):
    config = {"config_version": 2}

    print("vsu setup wizzard")

    vsc_path_default = os.environ.get("VSC_PATH")
    if vsc_path_default == None:
        print("Consider defining the VSC_PATH enviroment variable")
        exit()
    config["VSC_PATH"] = input_with_default("VSimComposer.sh directory: ", vsc_path_default)

    basenames = find_basenames()
    if len(basenames) == 1:
        basename = input_with_default(f"Enter basename ({basenames[0]}): ", basenames[0])
    elif len(basenames) > 1:
        print("WARNING: multiple possible basenames found in the current directory")
        print("Basenames found:")
        for bn in basenames:
            print(bn)
        required_input("Select basename: ")
    else:
        basename = required_input("Enter basename: ")
    config["basename"] = basename

    config["data_dir"] = advanced_input("Enter data directory: ", "data", advanced)
    config["build_dir"] = advanced_input("Enter build directory: ", ".vsu", advanced)

    config["VSC"] = config["VSC_PATH"] + "/VSimComposer.sh"
    config["S2P"] = find_exec_path(config["VSC_PATH"], "sdf2vpre")

    config["from_sdf"] = bool(advanced_input("Build input file from SDF file? ", "True", advanced))

    config["start_dump"] = bool(advanced_input("Dump at the start of the simulation? ", "True", advanced))

    write_config(config)
    return config

def read_config():
    if not os.path.isdir(".vsu"):
        return

    with open(".vsu/config.yaml", "r") as file:
        return yaml.load(file, Loader=yaml.Loader)

def write_config(config):
    if not os.path.isdir(".vsu"):
        os.mkdir(".vsu")

    with open(".vsu/config.yaml", "w") as file:
        file.write(yaml.dump(config))
