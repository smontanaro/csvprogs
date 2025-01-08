# csvprogs

This repo contains a number of Python scripts I've written over the
years, many dating back to my time at
[TradeLink](https://tradelinkllc.com/).  They come in three flavors:

  * CSV file transformers, which convert a CSV file on input to either
    another CSV file or a file in a different format (Excel spreadsheet,
    JSON file, etc)
  * data filters which modify the contents of an input CSV file,
    computing new columns from existing data (ewma, spline, etc)
  * Summarizers/plotters (mpl, sharpe, etc).


# MPL/CSVplot

MPL deserves special note. I worked with [John
Hunter](https://en.wikipedia.org/wiki/John_D._Hunter), the original
author of [Matplotlib](https://matplotlib.org/) for several years at
[TradeLink](https://tradelinkllc.com/). John, unfortunately, died much
too young. Though I never actually did anything with Matplotlib while
John was still alive, I used CSV files a fair amount and eventually
decided I needed to plot columns from time-to-time. Writing my plotter
using Matplotlib in rememberance of John seemed like a good thing.

I don't claim that this is a "good" example of Matplotlib. It grew
organically over time as the need arose, and I've never tried to get fancy
wth Matplotlib. It thus has a rather eclectic (baroque?  non-intuitive?)
command line interface. Its callable API is brand new as of September 2022
and is still pretty bug-ridden. *Caveat emptor*.
