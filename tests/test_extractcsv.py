import csv
import io
import subprocess
import sys

from tests import NVDA


def test_cli():
    with open(NVDA, "rb") as nvda:
        nvda_data = nvda.read()

    # bid >= ask
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.extractcsv",
        '(', 'bid', '>=', 'ask', ')', "or", "bid", "match", "99"],
        stdout=subprocess.PIPE, stderr=None, input=nvda_data)
    assert result.returncode == 0
    grt_eq = io.StringIO(result.stdout.decode("utf-8"))

    # bid < ask
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.extractcsv",
        "-v", '(', 'bid', '<', 'ask', ')', "or", "bid", "match", "99"],
        stdout=subprocess.PIPE, stderr=None, input=nvda_data)
    assert result.returncode == 0
    less = io.StringIO(result.stdout.decode("utf-8"))

    # The two extractions should be disjoint (the "or bid match 99" is just to
    # improve code coverage -- it doesn't ever match

    grt_eq_set = set()
    rdr = csv.DictReader(grt_eq)
    for row in rdr:
        grt_eq_set.add(tuple(row.items()))

    less_set = set()
    rdr = csv.DictReader(less)
    for row in rdr:
        less_set.add(tuple(row.items()))

    assert not grt_eq_set & less_set
