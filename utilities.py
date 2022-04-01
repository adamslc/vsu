import subprocess

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
