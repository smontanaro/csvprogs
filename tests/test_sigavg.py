import csv
import io
import subprocess

from tests import SPY_CSV


def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.sigavg",
                            "-x", "Date", "-y", "Close",
        "-m", "447.75", "-M", "448.75", SPY_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0

    inf = csv.DictReader(io.StringIO(result.stdout.decode("utf-8")))
    rows = list(inf)
    assert rows[0] == {
        "time": "13:30",
        "mean": "447.94",
        "sum": "895.88",
        "n": "2",
        }
    assert rows[-1] == {
        "time": "19:50",
        "mean": "447.95",
        "sum": "447.95",
        "n": "1",
        }
