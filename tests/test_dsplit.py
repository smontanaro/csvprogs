import csv
import io
import subprocess

from tests import SPLIT_IN, SPLIT_EXP

def test_cli():
    with open(SPLIT_IN, "rb") as inp:
        inp_data = inp.read()

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.dsplit", "-c", "weight"],
        stdout=subprocess.PIPE, stderr=None, input=inp_data)
    assert result.returncode == 0
    act = list(csv.DictReader(io.StringIO(result.stdout.decode("utf-8"))))
    with open(SPLIT_EXP, "r", encoding="utf-8") as inp:
        exp = list(csv.DictReader(inp))
    assert act == exp
