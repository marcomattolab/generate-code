import subprocess
import os

def run_cmd(cmd, cwd=None):
    process = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {cmd}\n{stderr.decode()}")
    return stdout.decode()