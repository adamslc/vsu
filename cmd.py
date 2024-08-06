import utilities

def cmd(config):
    VSC = config["VSC"]
    command = config["command"]

    cmd_str = f"source {VSC}; {command}"

    print(f"Running: {cmd_str}")
    utilities.run_cmd(cmd_str, capture_output=False)
