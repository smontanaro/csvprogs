import csv
import io
import subprocess

from tests import HTML_TABLE, HTML_CSV

def test_cli():
    with open(HTML_TABLE, "rb") as inp:
        inp_data = inp.read()

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.html2csv", "-v"],
        stdout=subprocess.PIPE, stderr=None, input=inp_data)
    assert result.returncode == 0
    act = list(csv.DictReader(io.StringIO(result.stdout.decode("utf-8"))))
    with open(HTML_CSV) as inp:
        exp = list(csv.DictReader(inp))
    assert act == exp
