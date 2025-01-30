import csv
import io
import subprocess

from tests import IWY_CSVS


def test_cli():
    old_dates = []
    for f in IWY_CSVS:
        with open(f) as inf:
            rdr = csv.DictReader(inf)
            old_dates.extend([row["Date"] for row in rdr])

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvcat",
            '-k', 'Date'] + IWY_CSVS,
            stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    output = io.StringIO(result.stdout.decode("utf-8"))
    rdr = csv.DictReader(output)
    new_dates = [row["Date"] for row in rdr]

    assert len(old_dates) > len(new_dates) and len(new_dates) == len(set(new_dates))
