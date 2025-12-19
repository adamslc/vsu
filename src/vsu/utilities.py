import subprocess
import os
import fcntl
import time

def touch(filename):
    with open(filename, 'a'):
        pass  # Just open and close the file to create or update timestamp

def force_symlink(target, link_name):
    # If the symlink or file already exists, remove it
    try:
        if os.path.islink(link_name) or os.path.exists(link_name):
            os.unlink(link_name)  # Remove existing symlink or file
    except OSError as e:
        print(f"Error removing existing link: {e}")

    # Create the new symlink
    try:
        os.symlink(target, link_name)
        print(f"Symlink created: {link_name} -> {target}")
    except OSError as e:
        print(f"Error creating symlink: {e}")

def set_nonblocking(fd):
    """Set the file descriptor to non-blocking mode."""
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

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

def run_cmd_with_logging(cmd_str, log_file_name, echo_to_stdout=True):
    log_file_handle = open(log_file_name, "w")

    process = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, bufsize=1)

    set_nonblocking(process.stdout.fileno())
    set_nonblocking(process.stderr.fileno())

    while True:
        try:
            line = process.stdout.readline()
            log_file_handle.write(line)

            if echo_to_stdout:
                print(line, end='')

        except BlockingIOError:
            pass

        try:
            line = process.stderr.readline()
            log_file_handle.write(line)

            if echo_to_stdout:
                print(line, end='')

        except BlockingIOError:
            pass

        if process.poll() is not None:
            print("Command finished with return code ", process.returncode)
            break

    process.wait()

def check_cmd_output(output):
    retcode = output[0]
    stdout = output[1]
