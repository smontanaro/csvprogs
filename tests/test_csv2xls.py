import os
import subprocess
import tempfile
import xml.etree.ElementTree
import zipfile

from tests import VRTX_CSV


def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2xls", VRTX_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0
    fd, fname = tempfile.mkstemp()
    try:
        with os.fdopen(fd, mode="wb") as fp:
            fp.write(result.stdout)
        with zipfile.ZipFile(fname, "r") as zf:
            with zf.open("xl/worksheets/sheet1.xml") as sheet:
                tree = xml.etree.ElementTree.parse(sheet)
                root = tree.getroot()
                sheet = root.findall(".")[0]
                assert list(sheet[4][0].itertext()) == ["Date","Open","High",
                                                        "Low","Close","% Change",
                                                        "% Change vs Average","Volume"]
    finally:
        os.unlink(fname)

def test_missing_file():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2xls",],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode != 0
