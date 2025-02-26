import csv
import io
import subprocess

from tests import SPY_CSV, RANDOM_CSV

exp = [448.10995923176694,
448.01075535803784,
447.9128076185481,
447.81658059816033,
447.7225388867971,
447.63114706596474,
447.54286972214874,
447.45808533254325,
448.1675201475151,
448.16568746624375,
448.1618262229229,
448.15588449507646,
448.1478103590426,
448.13755499595766,
448.1250819895869,
448.1103580260942,
448.0933497909789,
448.07402397155926,
448.0523472533485,
448.02863571825424,
448.004603051368,
447.98231232768916,
447.96382662459393,
447.951209020589,
447.94652259315745,
447.95125736432817,
447.96461113174075,
447.985208636735,
448.0116746210093,
448.0426338268471,
448.07671099499726,
448.1125308678253,
448.1487181885223,
448.1838976953906,
448.21669413182855,
448.2457322398247,
448.2696367608217,
448.28728793029137,
448.298587958225,
448.30369454854184,
448.3027654047778,
448.295958230774,
448.2834307303066,
448.2653406073009,
448.2418455619583,
448.21310330333785,
448.1792715341728,
447.92665351709496,
448.2594563454089]

EPS = 1e-7

def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.spline",
                            "-f", "Close", "-x", "Date", "-s", "1",
                            SPY_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0

    inf = csv.DictReader(io.StringIO(result.stdout.decode("utf-8")))
    act = [float(row["spline"]) for row in inf]
    assert len(act) == len(exp)

    eps = [x-y for (x, y) in zip(act, exp)]
    assert max(eps) <= EPS, eps

def test_non_dt():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.spline",
                            "-f", "random", "-x", "i", "--x-not-time",
        "-s", "1", RANDOM_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0
