
import subprocess

def applescript(cmd):
        proc = subprocess.Popen(["osascript", "-"],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate(input=cmd.encode("utf-8"), timeout=60)
        if proc.returncode != 0:
            raise Exception(f'Apple Script: {err.decode("utf-8")}')
        return out
