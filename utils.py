import subprocess
import os

def run_cmd(cmd, cwd=None):
    process = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        # FIXME TODO
        # raise Exception(f"Command failed: {cmd}\n{stderr.decode()}")
        print(f"Command failed: {cmd}\n{stderr.decode()}")
    else:
        print(stdout.decode())
    return stdout.decode()