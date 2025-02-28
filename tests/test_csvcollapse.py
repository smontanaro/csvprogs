import os
import subprocess
import tempfile

from tests import SPY_DAILY, VRTX_DAILY


def test_cli():
    # merge two CSV files, creating duplicate Date lines
    (fd1, tmp1) = tempfile.mkstemp()
    (fd2, tmp2) = tempfile.mkstemp()
    try:
        with open(SPY_DAILY, "r", encoding="utf-8") as inf:
            os.fdopen(fd1, "w", encoding="utf-8").writelines(inf.readlines()[0:100])
        with open(VRTX_DAILY, "r", encoding="utf-8") as inf:
            os.fdopen(fd2, "w", encoding="utf-8").writelines(inf.readlines()[0:100])

        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvmerge",
            "-k", "Date", "-d", "Date", tmp1, tmp2],
            stdout=subprocess.PIPE, stderr=None)
        assert result.returncode == 0
    finally:
        os.unlink(tmp1)
        os.unlink(tmp2)

    # now collapse them back together

    # we subtract 1 from the resulting lists to discard the file header
    in_count = len(result.stdout.decode("utf-8").strip().split("\r\n")) - 1
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvcollapse",
        "-k", "Date"],
        stdout=subprocess.PIPE, stderr=None, input=result.stdout)
    assert result.returncode == 0
    out_count = len(result.stdout.decode("utf-8").strip().split("\r\n")) - 1
    assert in_count // 2 == out_count, (in_count, out_count)
