
import glob


# All files relative to top of git repo
NVDA = "./tests/data/NVDA.csv"
SPY_ATR = "./tests/data/SPY-atr.csv"

# Same data, different formats
SPY_XLS = "./tests/data/SPY.xls"
SPY_PCK = "./tests/data/SPY.pck"
SPY_CSV = "./tests/data/SPY.csv"

VRTX_DAILY = "./tests/data/VRTX-daily.csv"
VRTX_CSV = "./tests/data/VRTX.csv"
RANDOM_CSV = "./tests/data/RANDOM.csv"

# Excel file with date column explicitly defined as dates
XLS_DATE = "./tests/data/xl-date.xls"

IWY_CSVS = glob.glob("./tests/data/IWY-?.csv")

BATCH_EX = "./tests/data/batch-example.csv"
