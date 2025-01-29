import csv
import json
from locale import setlocale, LC_ALL, atof, atoi
import subprocess

from tests import VRTX_CSV


setlocale(LC_ALL, "en_US.UTF-8")


def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2json",
        "-f", 'Date,Open,High,Low,Close,% Change,% Change vs Average,Volume',
        "-t", "datetime,float,float,float,float,float,float,int",
        VRTX_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0
    with open(VRTX_CSV, "r", encoding="utf-8") as inf:
        vrtx = csv.DictReader(inf)
        converted = json.loads(result.stdout.decode("utf-8"))
        for (v, j) in zip(vrtx, converted):
            assert atof(v["Open"]) == j["Open"], (v["Open"] == j["Open"])
            assert atof(v["Close"]) == j["Close"], (v["Close"] == j["Close"])
            assert atoi(v["Volume"]) == j["Volume"], (v["Volume"] == j["Volume"])


def test_cli_array():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2json",
        "-t", "datetime,float,float,float,float,float,float,int",
        "-a", "-H", VRTX_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0
    converted = json.loads(result.stdout.decode("utf-8"))
    assert converted[0][3] == "Low"
    assert converted[-1][-1] == 790881
