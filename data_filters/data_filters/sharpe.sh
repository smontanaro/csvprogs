#!/bin/bash

# Take in output of mean(1) on stdin and optional intervals per year
# (on command line, default: 253), produce Sharpe Ratio on stdout.

usage () {
    cat 1>&2 <<EOF
===========
sharpe
===========

----------------------------------------------------
compute sharpe ratio from output of mean(1)
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2016-08-16
:Copyright: TradeLink LLC 2016
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  sharpe [ -h ] [ -s char ] [ N ]

OPTIONS
=======

-h       print this and exit
-s char  use char as the input separator

DESCRIPTION
===========

Data are read from stdin. An optional number of measurements per year
(default: 253) are read from the command line. The Sharpe Ratio is printed
on stdout.

SEE ALSO
========

* mean
EOF
}

sep=','
while getopts hs: name ; do
    case $name in
	h) usage ; exit 0 ;;
	s) sep=$OPTARG ;;
    esac
done
shift $(($OPTIND - 1))

days=$1
if [ "x${days}" = "x" ] ; then
    days=253
fi
awk -F"${sep}" '{print $2 / $4 * sqrt('${days}')}'
