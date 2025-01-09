=============
data_filters
=============

----------------------------------------------------
Miscellaneous data filters
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-19
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

DESCRIPTION
===========

The data_filters package contains a series of Unix-style filters for
reading, processing and displaying tabular data, by default, data
which are stored in CSV files.  This page provides a quick overview of
the various tools, organized by class.  Note that use of the name
"CSV" doesn't necessarily restrict the user to proper CSV files.  Most
of the tools allow the user to override the input/output field
separators, so tab-delimited files can be processed as easily as CSV
files in most cases.

DATA SOURCES
------------

Several tools function as data sources:

* xls2csv - convert a worksheet from an Excel spreadsheet into CSV form

DATA FILTERS
------------

* avg - compute a moving average of one column of input
* bars - generate bars from input ticks
* csv2csv - extracts specified fields from an input CSV file
* ewma - compute an exponentially weight moving average of one column of input
* filter - filter lines matching a user-defined lambda function (or add computed values to output)
* shuffle - shuffle input lines randomly
* sigavg - signal average by time
* spline - compute a parametric spline of one column of input
* square - "square up" an input stream of ticks
* take - emit every n-th row of input

DATA SINKS
----------

* mean - compute the mean, median, and standard deviation of one column of input (output is not in CSV format)
* mpl - display one or more plots of inputs using matplotlib
