import csv
import io
import subprocess

from tests import VRTX_DAILY

EPS = 1e-7


def test_cli():
    with open(VRTX_DAILY, "rb") as vrtx:
        vrtx_data = vrtx.read()

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.hull",
        "-f", "Close", "-o", "hull", "-n", "100"],
        stdout=subprocess.PIPE, stderr=None, input=vrtx_data)
    assert result.returncode == 0
    rdr = csv.DictReader(io.StringIO(result.stdout.decode("utf-8")))
    # 100-day hull needs an extra few days to start generating values
    for i, row in enumerate(rdr):
        if i < 108:
            assert row["hull"] == "", (i, row)
        elif i == 108:
            assert (float(row["hull"]) - 44.0918114 < EPS), row
        elif i == 109:
            assert (float(row["hull"]) - 44.09282435 < EPS), row
        elif i == 3877:
            assert (float(row["hull"]) - 444.24192568 < EPS), row
