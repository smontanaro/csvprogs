import csv
import io
import subprocess

from tests import VRTX_DAILY

EPS = 1e-7


def test_cli():
    with open(VRTX_DAILY, "rb") as vrtx:
        vrtx_data = vrtx.read()

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.mean",
        "-f", "% Change-VRTX", "-m", "-10", "-M", "+10"],
        stdout=subprocess.PIPE, stderr=None, input=vrtx_data)
    assert result.returncode == 0
    values = [float(v) for v in result.stdout.decode("utf-8").split(",")]

    assert values == [3845.0, 0.043686, 0.049400, 2.095824]
