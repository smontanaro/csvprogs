import csv
import io
import subprocess

from csvprogs.common import type_convert
from tests import RANDOM_CSV


def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvsort",
            '-k', 'random', RANDOM_CSV],
            stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    output = io.StringIO(result.stdout.decode("utf-8"))
    rdr = csv.DictReader(output)
    values = []
    for row in rdr:
        values.append(row["random"])
    assert values == sorted(values)
