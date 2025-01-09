#!/usr/bin/env python

import csv
import io
import os.path
import subprocess
import sys
import tempfile
import unittest

# Simplified version of the one in Python's unit test support
# script_helpers module.
def spawn_python(*args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw):
    """Run a Python subprocess with the given arguments.

    kw is extra keyword args to pass to subprocess.Popen. Returns a Popen
    object.
    """
    cmd_line = [sys.executable]
    cmd_line.extend(args)
    return subprocess.Popen(cmd_line, stdin=subprocess.PIPE,
                            stdout=stdout, stderr=stderr,
                            **kw)

def kill_python(p):
    """Run the given Popen process until completion and return stdout."""
    p.stdin.close()
    data = p.stdout.read()
    p.stdout.close()
    # try to cleanup the child so we don't appear to leak when running
    # with regrtest -R.
    p.wait()
    subprocess._cleanup()
    return data

class XFormTest(unittest.TestCase):
    def test_basic_xform(self):
        input_list = [
            ["time", "close"],
            ["2015-04-15T15:00", "26.98"],
            ["2015-04-16T15:00", "27.04"],
            ["2015-04-17T15:00", "27.77"],
        ]

        modstring = """
from datetime import datetime, timedelta

def xform(row):
    t = datetime.strptime(row["time"], "%Y-%m-%dT%H:%M")
    pre_t = t - timedelta(seconds=1)
    pre = [{"time": pre_t.strftime("%Y-%m-%dT%H:%M:%S"),
            "close": row["close"] - 0.01}]
    return (pre, [])
"""

        expected = b"""\
time,close\r
2015-04-15T14:59:59,26.97\r
2015-04-15T15:00,26.98\r
2015-04-16T14:59:59,27.029999999999998\r
2015-04-16T15:00,27.04\r
2015-04-17T14:59:59,27.759999999999998\r
2015-04-17T15:00,27.77\r
"""

        cwd = os.getcwd()
        inp = io.StringIO()
        writer = csv.writer(inp)
        writer.writerows(input_list)
        raw_input = bytes(inp.getvalue(), encoding="ascii")
        with tempfile.NamedTemporaryFile(mode="w+", dir="/tmp",
                                         suffix=".py") as xfile:
            xfile.file.write(modstring)
            xfile.file.flush()
            xfile.seek(0)
            modname = os.path.splitext(os.path.split(xfile.name)[1])[0]
            env = dict(os.environ)
            env["PYTHONPATH"] = "/tmp"
            p = spawn_python(f"{cwd}/csvprogs/xform.py",
                             "-F", f"{modname}.xform", env=env)
            p.stdin.write(raw_input)
            data = kill_python(p)
            self.assertEqual(data, expected)

if __name__ == "__main__":
    unittest.main()
