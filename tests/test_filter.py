import csv
import io
import subprocess

from tests import BATCH_EX

def test_cli():
    with open(BATCH_EX, "rb") as ex:
        ex_data = ex.read()

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.filter",
        "-f", 'lambda row: row["batch"] != "b=1"', "-k", "lambda-key"],
        stdout=subprocess.PIPE, stderr=None, input=ex_data)
    assert result.returncode == 0
    rdr = csv.DictReader(io.StringIO(result.stdout.decode("utf-8")))
    for row in rdr:
        assert row["batch"] == "b=0" and row["lambda-key"] == "True", row

def test_bad_lambda_key():
    with open(BATCH_EX, "rb") as ex:
        ex_data = ex.read()

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.filter",
        "-f", 'lambda row: row["batch"] != "b=1"', "-k", "age"],
        stdout=subprocess.PIPE, stderr=None, input=ex_data)
    assert result.returncode != 0
