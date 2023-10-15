"""
Some helper functions.
"""
from subprocess import Popen, PIPE


class AppleScriptException(Exception):
    pass


def applescript(cmd: str) -> bytes:
    """Execute an apple script command.

    Return the output of the command or raise an exception on failure.
    """
    command = ["osascript", "-"]

    with Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
        out, err = proc.communicate(input=cmd.encode("utf-8"), timeout=60)
        if proc.returncode != 0:
            raise AppleScriptException(f'{err.decode("utf-8")}')
        return out
