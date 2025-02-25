
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
VRTX_MISSING_CSV = "./tests/data/VRTX-missing.csv"
RANDOM_CSV = "./tests/data/RANDOM.csv"
SPY_DAILY = "./tests/data/SPY-daily.csv"

# Excel file with date column explicitly defined as dates
XLS_DATE = "./tests/data/xl-date.xls"

IWY_CSVS = glob.glob("./tests/data/IWY-?.csv")

BATCH_EX = "./tests/data/batch-example.csv"

HTML_TABLE = "./tests/data/cal.html"
HTML_CSV = "./tests/data/cal.csv"

SPLIT_IN = "./tests/data/split-in.csv"
SPLIT_EXP = "./tests/data/split-exp.csv"

FIRST = "./tests/data/first.csv"
SECOND = "./tests/data/second.csv"
SECOND_SHORT = "./tests/data/second-short.csv"
EMPTY = "./tests/data/empty.csv"
MERGED = "./tests/data/merged.csv"
MERGED_SHORT = "./tests/data/merged-short.csv"
FILLED = "./tests/data/filled.csv"

# invalid characters in timestamp
BAD_DATE_1 = "./tests/data/bad-date-1.csv"
# Feb 29th in non-leap year
BAD_DATE_2 = "./tests/data/bad-date-2.csv"
