import csv
import io
import pickle
import subprocess
import sys


from csvprogs.xls2csv import xls2csv
from tests import SPY_XLS, SPY_PCK, SPY_CSV


def test_xls2csv():
    rows = xls2csv(SPY_XLS, 0)
    with open(SPY_PCK, "rb") as pck:
        assert rows == pickle.load(pck)

def maybe_float(s):
    try:
        return float(s)
    except ValueError:
        return s

def test_cli():
    with (open(SPY_CSV, "r", encoding="utf-8") as csvf,
          open(SPY_XLS, "rb") as xlsf):
        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.xls2csv"],
            input=xlsf.read(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            act = list(csv.reader(io.StringIO(result.stdout.decode("utf-8"))))
            exp = list(csv.reader(csvf))
            for (i, row) in enumerate(act):
                act[i][:] = [maybe_float(s) for s in row]
            for (i, row) in enumerate(exp):
                exp[i][:] = [maybe_float(s) for s in row]
            assert act == exp
        else:
            print(result.stderr.decode("utf-8"), file=sys.stderr)
            raise SystemError
