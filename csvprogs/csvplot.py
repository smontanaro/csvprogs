#!/usr/bin/env python

"""
===========
{PROG}
===========

----------------------------------------------------
plot csv-ish input from stdin using matplotlib
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

{PROG} [ -f x,y[,a[,c[,l[s[,m]]]]]] [ -p file ] [ -F fmt ] [ -s sep ] \\
         [ -T title ] [ -r label ] [ -l label] [ -x label ] \\
         [ -b x,y,val,c ] [ -L ] [ -v ] [ -B bkend ] \\
         [ -X min:max ] [ -Y min:max[,min:max] ] [ --xkcd ]

OPTIONS
=======

* -f x,y[,axis[,color[,legend[,style[,marker]]]]] - plot field x vs.
  field y
* -b x,y,val,c - set background to c where field y value >= val at x
* -p file - if given, will save the plot to the named file and exit.
* -F fmt - plot the X axis using fmt (default varies)
* -s sep - use sep as the field separator (default is comma)
* -d dimension - specify dimensions in (I think) inches, default
  8 wide, 6 high
* -T title - set title of the plot
* -r label - set the label for the right y axis
* -l label - set the label for the left y axis
* -x label - set the label for the x axis
* -L - do not create a legend
* -X min:max (two floats) or min,max (two dates) - set the min and max
     values for the X axis - "today" or "yesterday" may be used as the max
     date
* -Y min:max[,min:max] - set the initial min and max values for the left (and
  optionally, right) Y axis
* -v - be a bit more verbose
* -B bkend - use the named backend
* -S - if a fieldname is not found, also try stripping leading and trailing
  whitespace
* --xkcd - mimic style of the XKCD cartoon.

LONG OPTION NAMES
-----------------

Long option names are supported. Supported long names and their
equivalent short names are:

* backend: B
* format : F
* skip_legend: L
* title: T
* xkcd: X
* y_range: Y
* background: b
* dimension: d
* field: f
* help: h
* left_label: l
* plot_file: p
* right_label: r
* separator: s
* verbose: v
* x_label: x

DESCRIPTION
===========

The {PROG} command takes a CSV-like file as input and generates one
or more plots.  Those plots can be displayed interactively (the
default) or written to an image file (if the -p option is given).

In its simplest form it displays a single plot of the values from a
CSV file in column 1 as a function of time (in column 0).  In this
case, the CSV file is assumed to not have a header.

The specification of the fields to plot and their attributes are given
using the -f option.  At its simplest, a single x,y pair is given,
resulting in a red line plot using the left Y axis.  If the CSV file
has a header, x and y can be column names as well.

The -f option is the most frequently used and most complicated:

* The first two fields (x, y) are always required, and specify the two
  columns to plot.
* The Y axis defaults to "left", but can be given explicitly as 'l'
  or 'r'.
* The color can be anything matplotlib accepts. Typically, a single
  letter suffices ('r' for red, etc), but the color name can also be
  spelled out or given using hex notation.
* A legend label can be specified, and defaults to the y column name.
* Consult the matplotlib documentation for details of acceptable styles
  (default '-').  By default, the line width is 1.0, but you can specify
  the linestyle as "s/w", where "s" is the basic style, and "w" is a
  floating point width.
* markers (default ''). You may use a ';' instead of ',', or quote the
  field and the full field string (to preserve the quoting around the
  field - it is split using Python's csv.reader class). By default, the
  marker size is 1.0, but you can define the marker as "m/s", where "m"
  is the marker, and "s" is a floating point scale value.

You can color the background of the plot based on one or more values using
the -b flag.  For example, if you have a value at offset 2 which toggles
between three values, -1, 0, and +1, you could color the background
accordingly::

  -b 0,2,-1,skyblue -b 0,2,0,pink -b 0,2,+1,lightgreen.

If you don't specify a format for the X axis, time is assumed, and a
hopefully reasonable format is chosen based on the current visible X
range:

* X range > 1.5 years ==> "%%Y-%%m-%%d"
* X range > two days ==> "%%m/%%d\\n%%H:%%M"
* X range < ten minutes ==> "%%H:%%M\\n%%S.%%f"
* X range < two hours ==> "%%H:%%M:%%S"
* otherwise ==> "%%H:%%M"

MODULE USAGE
============

This is also callable from Python:

  import mpl
  options = mpl.Options()
  options.title = "Hello World"
  options.fields = ["timestamp", "status"]
  options.plot_file = "uptime.png"
  reader = csv.DictReader("bhuptime.csv")
  mpl.plot(reader, options)


EXAMPLE
=======

Plot one hour of F:NQM12 trades, highlighting all trades of size 10
with a light green background::

  nt -S -s 2012-04-06T07:25 -e 2012-04-06T08:25 F:NQM12 \\
  | mpl -f 0,2,l,r -b 0,3,10,lightgreen

VERSION
=======

@@VERSION@@

SEE ALSO
========

* avg
* bars
* nt
* pt
* square
* take

"""

import sys
import csv
import dataclasses
import datetime
import os
import re
import io

import dateutil.parser
import numpy
import matplotlib.dates
from  matplotlib import pyplot
import matplotlib.ticker
from public import public, private

from csvprogs.common import CSVArgParser, openi, usage


PROG = os.path.splitext(os.path.basename(sys.argv[0]))[0]

ONE_MINUTE = datetime.timedelta(minutes=1)
ONE_DAY = datetime.timedelta(days=1)
ONE_HOUR = datetime.timedelta(minutes=60)

@public
@dataclasses.dataclass
class Options:
    "container for all the flags"
    backend: str = ""
    background: list = dataclasses.field(default_factory=list)
    block: bool = True
    dims: tuple = (8, 6)
    do_legend: bool = True
    fields: list = dataclasses.field(default_factory=list)
    left_label: str = ""
    plot_file: str = ""
    right_label: str = ""
    sep: str = ","
    title: str = ""
    xkcd: bool = False
    verbose: bool = False
    xfmt: str = ""
    x_label: str = ""
    x_min_max: list = dataclasses.field(default_factory=list)
    xtime: bool = True
    y_min_max: list = dataclasses.field(default_factory=list)

    def debug_print(self):
        print("fields:", file=sys.stderr)
        # pylint: disable=E1101
        for attr in self.__class__.__dataclass_fields__:
            print(f"  {attr}: {getattr(self, attr)}", file=sys.stderr)

@public
def main():
    "see __doc__"
    # see comment in common.usage()
    docstring = __doc__.format(**globals())
    parser = CSVArgParser(usage=usage(docstring, {}))
    parser.add_argument("-B", "--backend", default="",
                        help="Matplotlib backend renderer")
    parser.add_argument("-F", "--format", "--xfmt", dest="xfmt", default="",
                        help="X axis format")
    parser.add_argument("-L", "--skip_legend", dest="do_legend", default=True,
                        action="store_true", help="Suppress display of legend")
    parser.add_argument("-T", "--title", default="",
                        help="plot title")
    parser.add_argument("-d", "--dimension", default="8.0, 6.0", dest="dims",
                        help="plot dimensions")
    parser.add_argument("-p", "--plot_file", default="",
                        help="output plotter file")
    parser.add_argument("--left_label", default="",
                        help="lefthand Y axis label")
    parser.add_argument("--right_label", default="",
                        help="righthand Y axis label")
    parser.add_argument("-x", "--x_label", default="",
                        help="X axis label")
    parser.add_argument("--xkcd", default=False, action="store_true",
                        help="Use XKCD fonts")
    parser.add_argument("-b", "--background", action="append",
                        help="background color definition(s)")
    parser.add_argument("-f", "--field", dest="fields", action="append",
                        required=True, help="plot field specs")
    parser.add_argument("--block", default=True, dest="block", action="store_true",
                        help="block after plot display (testing only)")
    parser.add_argument("--noblock", dest="block", action="store_false",
                        help="don't block after plot display (testing only)")
    parser.add_argument("-Y", "--y_range", default="",
                        help="min/max ranges for left (and right) Y axes")
    parser.add_argument("-X", "--x_range", default="",
                        help="min/max range X axis")
    options, args = parser.parse_known_args()

    options.xtime = (options.xfmt == "" or
        "%H" in options.xfmt or
        "%M" in options.xfmt or
        "%m" in options.xfmt or
        "%b" in options.xfmt or
        "%d" in options.xfmt
        )
    options.dims = tuple(float(v.strip()) for v in re.split("[x,]", options.dims,
                         maxsplit=1))
    options.background = parse_background_specs(options.background)
    options.fields = parse_plot_specs(options.fields)

    options.y_min_max = parse_y_range(options.y_range)
    options.x_min_max = parse_x_range(options.x_range)

    if not options.backend:
        if not os.environ.get("DISPLAY"):
            # Allow non-interactive use (e.g. running with -p from cron)
            matplotlib.use("Agg")
    else:
        matplotlib.use(options.backend)

    if options.verbose:
        print("Using", matplotlib.get_backend(), file=sys.stderr)

    if options.xkcd:
        pyplot.xkcd()
        if options.verbose:
            print("Using XKCD style.", file=sys.stderr)

    with openi(args[0] if len(args) >= 1 else sys.stdin, "r",
               encoding=options.encoding) as inf:
        rdr = csv.DictReader(inf, delimiter=options.insep)

        # if options.verbose:
        #     options.debug_print()

        # callable module function goes here...

        plot(options, rdr, block=options.block)

@public
def plot(options, rdr, block=False):
    "guts of the plotter"
    raw = list(rdr)
    left = []
    right = []
    min_y = 1e99
    max_y = -1e99

    if options.xtime:
        min_x = datetime.datetime(9999, 12, 31, 23, 59, 59)
        max_x = datetime.datetime(1970, 1, 1, 0, 0, 0)
        def parse_x(x_val):
            try:
                return dateutil.parser.parse(x_val)
            except dateutil.parser.ParserError as err:
                if err.args:
                    msg = err.args[0]
                    if msg.startswith("day is out of range for month"):
                        # Maybe Feb 29 in non-leap year? Unfortunately, I can't
                        # tell more about the date's structure.
                        if re.search(r"[- ]29(\b|[^0-9]|$)", x_val) is not None:
                            return ""
                    else:
                        print(f"Can't parse {x_val!r} as a timestamp.",
                              file=sys.stderr)
                raise

        def fmt_date(tick_val, _=None, xfmt=options.xfmt):
            date = matplotlib.dates.num2date(tick_val)
            if not xfmt:
                # Calculate X format dynamically based on the visible
                # range.
                left, right = [matplotlib.dates.num2date(x) for x in pyplot.xlim()]
                x_delta = right - left
                if x_delta > int(5 * 365) * ONE_DAY:
                    xfmt = "%Y"
                elif x_delta > int(2 * 365) * ONE_DAY:
                    xfmt = "%Y-%m"
                elif x_delta > int(1.5 * 365) * ONE_DAY:
                    xfmt = "%Y-%m-%d"
                elif x_delta > 2 * ONE_DAY:
                    xfmt = "%m/%d\n%H:%M"
                elif x_delta < 10 * ONE_MINUTE:
                    xfmt = "%H:%M\n%S.%f"
                elif x_delta < 2 * ONE_HOUR:
                    xfmt = "%H:%M:%S"
                else:
                    xfmt = "%H:%M"
            return date.strftime(xfmt)

        formatter = matplotlib.ticker.FuncFormatter(fmt_date)
    else:
        min_x = 1e99
        max_x = -1e99
        def parse_x(x_val):
            return float(x_val)

        def fmt_float(x_val, _=None):
            return options.xfmt % x_val
        formatter = matplotlib.ticker.FuncFormatter(fmt_float)

    lt_y_range = [min_y, max_y]
    rt_y_range = [min_y, max_y]
    x_range = [min_x, max_x]
    for (col1, col2, side, color, legend, style, marker) in options.fields:
        if "/" in style:
            style, width = style.split("/", 1)
            width = float(width)
        else:
            width = 1.0
        if "/" in marker:
            marker, m_scale = marker.split("/", 1)
            m_scale = float(m_scale)
        else:
            m_scale = 1.0
        if marker == ";":
            marker = ","
        data = ([], color, legend, (style, width), (marker, m_scale))
        if side == "l":
            left.append(data)
            y_range = lt_y_range
        else:
            right.append(data)
            y_range = rt_y_range
        for values in raw:
            x_val, y_val = (values.get(col1, ""), values.get(col2, ""))
            # Rows don't need to be completely filled.
            if x_val == "":
                continue
            y_val = 'nan' if y_val.strip() == "" else y_val
            x_val = parse_x(x_val)
            if x_val == "":
                continue
            # floats might contain separators
            y_val = float(re.sub("[_, ]", "", y_val))
            # If we get inputs with timezone info, convert. This
            # is likely only to be executed once, as if one
            # timestamp has tzinfo, all are likely to.
            if options.xtime and x_range[0].tzinfo != x_val.tzinfo:
                zone = x_val.tzinfo
                x_range = [dt.replace(tzinfo=zone) for dt in x_range]
            y_range[:] = [min(y_range[0], y_val),
                          max(y_range[1], y_val)]
            data[0].append((x_val, y_val))
        if data[0]:
            x_range = [min([x for (x, _y) in data[0]]+[x_range[0]]),
                       max([x for (x, _y) in data[0]]+[x_range[1]])]
        else:
            print("No data for x range!", file=sys.stderr)
    if sum(len(x) for x in left) == 0 and sum(len(x) for x in right) == 0:
        print("No points to plot!", file=sys.stderr)
        return 1

    figure = pyplot.figure(figsize=options.dims)
    if options.xtime:
        figure.autofmt_xdate()

    left_plot = figure.add_subplot(111)
    left_plot.set_title(options.title)
    left_plot.set_axisbelow(True)
    left_plot.yaxis.set_major_formatter(pyplot.FormatStrFormatter('%g'))
    left_plot.xaxis.set_major_formatter(formatter)

    lines = []
    if left:
        if options.left_label:
            left_plot.set_ylabel(options.left_label, color=left[0][1])
        if options.x_label:
            left_plot.set_xlabel(options.x_label, color=left[0][1])
        for data in left:
            points, color, legend, style, marker = data
            lines.extend(left_plot.plot([x for x, y in points],
                                        [y for x, y in points],
                                        color=color,
                                        linestyle=style[0],
                                        linewidth=style[1],
                                        label=legend,
                                        marker=marker[0],
                                        markersize=marker[1]))
        for tick_label in left_plot.get_yticklabels():
            tick_label.set_color(left[0][1])

        extra = 0.02 * (lt_y_range[1]-lt_y_range[0])
        lt_y_range = [lt_y_range[0] - extra, lt_y_range[1] + extra]
        if options.y_min_max:
            left_plot.set_ylim(options.y_min_max[0])
        else:
            left_plot.set_ylim(lt_y_range)

    if right:
        right_plot = left_plot.twinx()
        right_plot.set_axisbelow(True)
        right_plot.yaxis.set_major_formatter(pyplot.FormatStrFormatter('%g'))
        right_plot.xaxis.set_major_formatter(formatter)
        if options.right_label:
            right_plot.set_ylabel(options.right_label, color=right[0][1])
        if options.x_label and not left:
            right_plot.set_xlabel(options.x_label, color=left[0][1])

        for data in right:
            points, color, legend, style, marker = data
            lines.extend(right_plot.plot([x for x, y in points],
                                         [y for x, y in points],
                                         color=color,
                                         linestyle=style[0],
                                         linewidth=style[1],
                                         label=legend,
                                         marker=marker[0],
                                         markersize=marker[1]))
        for tick_label in right_plot.get_yticklabels():
            tick_label.set_color(right[0][1])

        extra = 0.02 * (rt_y_range[1]-rt_y_range[0])
        rt_y_range = [rt_y_range[0] - extra, rt_y_range[1] + extra]
        if len(options.y_min_max) == 2:
            right_plot.set_ylim(options.y_min_max[1])
        else:
            right_plot.set_ylim(rt_y_range)

    color_background(options.background, left and left_plot or right_plot,
                     left and lt_y_range or rt_y_range, raw, parse_x)

    if options.x_min_max:
        left_plot.set_xlim(options.x_min_max[0])
    else:
        extra = (x_range[1]-x_range[0]) * 2 // 100
        try:
            x_range = [x_range[0] - extra, x_range[1] + extra]
        except OverflowError:
            print("overflow:", x_range, extra, file=sys.stderr)
            raise
        left_plot.set_xlim(x_range)

    if options.do_legend:
        # Suppress empty labels
        new_lines = []
        new_labels = []
        for line in lines:
            label = line.get_label()
            if not label or label[0] == "_":
                continue
            new_labels.append("" if label.startswith("_") else label)
            new_lines.append(line)
        if right:
            right_plot.legend(new_lines, new_labels,
                              loc='best').set_draggable(True)
        else:
            left_plot.legend(new_lines, new_labels,
                             loc='best').set_draggable(True)

    figure.tight_layout()
    if options.plot_file:
        pyplot.savefig(options.plot_file)
    else:
        pyplot.show(block=block)

    return 0

@private
def parse_y_range(spec):
    y_min_max = []
    if spec:
        if "," in spec:
            left, right = spec.split(",")
            y_min_max = [[float(x) for x in left.split(":")],
                                 [float(x) for x in right.split(":")]]
        else:
            y_min_max = [[float(x) for x in spec.split(":")]]
    return y_min_max

@private
def parse_x_date_range(min_dt, max_dt):
    result = []
    for dt in (min_dt, max_dt):
        if dt == "today":
            date = datetime.datetime.now()
        elif dt == "yesterday":
            date = datetime.datetime.now() - datetime.timedelta(days=1)
        else:
            date = dateutil.parser.parse(dt)
        result.append(date)
    return result

@private
def parse_x_range(spec):
    if not spec:
        return []
    if spec == "today":
        return [datetime.datetime.now()] * 2
    if spec == "yesterday":
        return [datetime.datetime.now() - datetime.timedelta(days=1)] * 2

    # First try splitting at colon that produces too many values, try a
    # comma. Both might be floats or timestamps.
    for split_spec in (spec.split(":"), spec.split(",")):
        if len(split_spec) == 2:
            try:
                return [float(x) for x in split_spec]
            except ValueError:
                # hmmm... not two floats, reinterpret as two datetimes
                return parse_x_date_range(*split_spec)
    raise ValueError(f"Can't parse range: {repr(spec)}")

@private
def color_background(backgrounds, plot_, y_range, raw_data, parse_x):
    "Add background fill colors."
    if not backgrounds:
        return

    for col1, col2, low, high, color in backgrounds:
        xdata = []
        ydata = []
        for values in raw_data:
            x_val, y_val = (values.get(col1, ""), values.get(col2, ""))
            if x_val == "" or y_val == "":
                continue
            try:
                x_val = parse_x(x_val)
            except ValueError as err:
                print(err, values, file=sys.stderr)
                raise
            y_val = float(re.sub("[_, ]", "", y_val))
            xdata.append(x_val)
            ydata.append(y_val)
        if low == high:
            mask = low == numpy.array(ydata)
        else:
            mask = (low <= numpy.array(ydata)) & (numpy.array(ydata) < high)
        plot_.fill_between(xdata, y_range[0], y_range[1],
                           edgecolor=color, facecolor=color,
                           where=mask, label="")

@private
def parse_background_specs(specs):
    parsed = []
    if specs:
        for bg_spec in specs:
            bg_spec = bg_spec.split(",")
            bg_spec[0] = bg_spec[0].strip()
            bg_spec[1] = bg_spec[1].strip()
            if ":" in bg_spec[2]:
                low, high = [float(x) for x in bg_spec[2].split(":")]
            else:
                low = high = float(bg_spec[2])
            parsed.append((bg_spec[0], bg_spec[1], low, high, bg_spec[3]))
    return parsed

@private
def parse_plot_specs(specs):
    parsed = []
    for spec in specs:
        quotechar = "'" if "'" in spec else '"'
        plarg = next(csv.reader(io.StringIO(spec), quotechar=quotechar))
        if len(plarg) == 2:
            # plot using left y axis by default
            plarg.append("l")
        if len(plarg) == 3:
            # plot using blue by default
            plarg.append("b")
        if len(plarg) == 4:
            # use the Y column name as the default legend name.
            plarg.append(plarg[1])
        if len(plarg) == 5:
            # plot with '-' line style by default
            plarg.append("-")
        if len(plarg) == 6:
            # no marker by default
            plarg.append("")
        parsed.append(plarg[0:2]+
                      [plarg[2][0].lower()]+
                      [plarg[3].lower()]+
                      plarg[4:])
    return parsed

if __name__ == "__main__":
    sys.exit(main())
