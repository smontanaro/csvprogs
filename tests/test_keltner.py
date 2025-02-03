import subprocess

from tests import SPY_CSV


def test_cli():
    # compute atr and ewma inputs to keltner
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.atr",
        "-c", "High,Low,Close", "--outcol", "atr", SPY_CSV],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.ewma",
        "-f", "Close", "--outcol", "ewma"],
        stdout=subprocess.PIPE, stderr=None, input=result.stdout)
    assert result.returncode == 0

    # now do the keltner thing.
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.keltner"],
        stdout=subprocess.PIPE, stderr=None, input=result.stdout)
    assert result.returncode == 0
