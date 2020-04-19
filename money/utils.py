"""
Some helper functions.
"""
import subprocess

def applescript(cmd):
    """Execute an apple script command.

    Return the output of the command or raise an exception on failure.
    """
    proc = subprocess.Popen(["osascript", "-"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate(input=cmd.encode("utf-8"), timeout=60)
    if proc.returncode != 0:
        raise Exception(f'Apple Script: {err.decode("utf-8")}')
    return out
