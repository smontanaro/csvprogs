import csv
import json
from locale import setlocale, LC_ALL, atof, atoi
import subprocess

import dateutil.parser

from tests import VRTX_CSV, VRTX_MISSING_CSV, SPY_DAILY


setlocale(LC_ALL, "en_US.UTF-8")


def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2json",
        "-f", 'Date,Open,High,Low,Close,% Change,% Change vs Average,Volume',
        "-t", "datetime,float,float,float,float,float,float,int:0",
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


def test_missing_no_default():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2json",
        "-f", 'Date,Open,High,Low,Close,% Change,% Change vs Average,Volume',
        "-t", "datetime,float,float,float,float,float,float,int:0",
        VRTX_MISSING_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode != 0


def test_missing_with_default():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2json",
        "-f", 'Date,Open,High,Low,Close,% Change,% Change vs Average,Volume',
        "-t", "datetime,float,float,float,float:-1.0,float,float:-1,int:0",
        VRTX_MISSING_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0
    converted = json.loads(result.stdout.decode("utf-8"))
    assert (converted[-1]["% Change vs Average"] == -1.0 and
            converted[-1]["Close"] == -1.0)


def test_cli_array():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2json",
        "-t", "datetime,float,float,float,float,float,float,int",
        "--array", "-H", VRTX_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0
    converted = json.loads(result.stdout.decode("utf-8"))
    assert converted[0][3] == "Low", converted[0]
    assert converted[-1][-1] == 790881, converted[-1]


def test_bad_type_info():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2json",
        "-t", "datetime,float,float,float,float,float,int",
        "--array", "-H", VRTX_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode != 0


def test_cli_default():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2json",
        "-t", "datetime,float:0.0,float:0.0,float:0.0,float:0.0,float:0.0,float:0.0,int",
        SPY_DAILY],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0
    dts = set(dateutil.parser.parse(dt) for dt in
        [
         "2012-10-31T05:00:00.000Z",
         "2013-03-27T05:00:00.000Z",
         "2013-06-10T05:00:00.000Z",
         "2016-04-22T05:00:00.000Z",
         "2017-01-10T06:00:00.000Z",
         "2018-05-08T05:00:00.000Z",
         "2018-10-08T05:00:00.000Z",
         "2022-08-11T05:00:00.000Z",
         "2023-07-21T05:00:00.000Z",
        ]
    )
    def decode_dt(dct):
        if "Date" in dct:
            dct["Date"] = dateutil.parser.parse(dct["Date"])
        return dct

    converted = json.loads(result.stdout.decode("utf-8"), object_hook=decode_dt)
    for row in converted:
        if row["Date"] in dts:
            assert row["% Change-SPY"] == 0.0, row
