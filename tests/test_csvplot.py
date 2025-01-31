import csv
import time

from matplotlib import pyplot
from csvprogs.csvplot import plot, Options
from tests import NVDA

def test_plot():
    options = Options()
    options.fields = [["time", "last", "l", "red", "legend", "-", ""]]

    with open(NVDA, "r", encoding="utf-8") as inp:
        rdr = csv.DictReader(inp)
        plot(options, rdr, block=False)
        time.sleep(0.25)
        pyplot.close()
