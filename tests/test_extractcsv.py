import csv
import io
import subprocess

from csvprogs.common import type_convert
from tests import NVDA


def test_cli():
    with open(NVDA, "rb") as nvda:
        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.extractcsv",
            '(', 'bid', '>=', 'ask', ')', "or", "bid", "match", "99"],
            stdout=subprocess.PIPE, stderr=None, input=nvda.read())
    assert result.returncode == 0
    output = io.StringIO(result.stdout.decode("utf-8"))
    rdr = csv.DictReader(output)
    for row in rdr:
        if type_convert(row["bid"]) < type_convert(row["ask"]):
            raise ValueError(f"constraint violation: {row}")
