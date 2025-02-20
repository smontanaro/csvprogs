#/bin/bash

# Plot weight/o2/hr progression over the past year.

usage () {
cat <<EOF

Plot, weight, O2 saturation, and/or resting heart rate.

weight [ -d ] [ -e ] [ -w ] [ -o ] [ -p ] [ LOOKBACK ]

-d   - debug: use git repo versions of csv progs (must be first option!)
-w   - exclude weight
-o   - exclude O2 saturation
-p   - exclude heart rate
-h   - print this message
-e N - use ewma with N-day max gap instead of simple moving average

At least one of weight, O2 and HR must be plotted.

Lookback is in days, defaulting to 365. Suffixes of "y" or "m" are
understood to me years (365 days) or months (30 days).

EOF
}

WTCSV=$HOME/misc/weight.csv

min () {
    if [ $1 -le $2 ] ; then
        echo $1
    else
        echo $2
    fi
}

strjoin () {
    local IFS="$1"
    shift
    echo "$*"
}

cvtdays () {
    if [ "${1}" = "all" ] ; then
        echo $(wc -l < $WTCSV)
    elif [ "${1}" = "ytd" ] ; then
        echo $(date +%j)
    else
        local days=1
        case "${1}" in
            *y)
                days=365
                ;;
            *m)
                days=30
                ;;
            *)
                days=1
                ;;
        esac
        coeff=$(sed -e 's/[a-z]*//g' <<< $1)
        echo $((days * coeff))
    fi
}

CSV2CSV=csv2csv
CSVPLOT=csvplot
DSPLIT=dsplit
EWMA=ewma
MVAVG=mvavg

COLORS=( "black" "orange" "cyan" "magenta" "red" "green" "blue" )
O2="-f date,O2,r,blue,'',dotted -f date,'O2 (avg)',r,blue,'O2 (r)'"
HR="-f date,hr,r,green,'',dotted -f date,'HR (avg)',r,green,'HR (r)'"
WT="-f date,weight,l,red,'',dotted -f date,'weight (avg)',l,red,'Weight (l)'"
tO2=O2
tHR=HR
tWT=Weight
AVG="${MVAVG} -n 7"
MISSING=2

while getopts 'de:opwh' OPTION; do
    case "$OPTION" in
        d)
            dbgpfx="python ${HOME}/src/csvprogs/csvprogs"
            CSV2CSV=${dbgpfx}/${CSV2CSV}.py
            CSVPLOT=${dbgpfx}/${CSVPLOT}.py
            DSPLIT=${dbgpfx}/${DSPLIT}.py
            EWMA=${dbgpfx}/${EWMA}.py
            MVAVG=${dbgpfx}/${MVAVG}.py
            ;;
        e)
            MISSING=${OPTARG}
            AVG="${EWMA} -m ${MISSING}"
            ;;
        o)
            O2=
            tO2=
            ;;
        p)
            HR=
            tHR=
            ;;
        w)
            WT=
            tWT=
            ;;
        h)
            usage 1>&2
            exit 0
            ;;
    esac
done
shift "$(($OPTIND -1))"

# Chicken-and-egg situation dictates a last-minute patch-up. If -d was
# given but -e wasn't, ${AVG} won't reference the uninstalled version
# of mvavg.
if [ "x{dbgpfx}" != "x" ] ; then
    if [ "x${AVG}" = "xmvavg -n 7" ] ; then
        AVG="${MVAVG} -n 7"
    fi
fi

if [ "x${O2}${WT}${HR}" = "x" ] ; then
    echo
    usage 1>&2
    exit 1
fi

LOOKBACK=$(cvtdays ${1:-365})
LOOKBACK=$(min $LOOKBACK $(( $(wc -l < $WTCSV) - 1 )) )

if [ $LOOKBACK -gt 365 ] ; then
    FMT=%m/%y
else
    FMT=%m/%d
fi

title="$(strjoin / ${tWT} ${tHR} ${tO2}) Progression"

# Shells have issues when evaluating args containing spaces. I gave up
# fussing around and simply write the generated mpl command line to a
# temp file which is then executed at the end of the pipeline.

scr=$(mktemp /tmp/mpltmp.XXXXX)
csv=$(mktemp /tmp/mpltmp.XXXXX)
trap "rm -f ${scr} ${csv}" EXIT

# The data we want to plot...
(head -1 $WTCSV ; tail -$LOOKBACK $WTCSV) > ${csv}

# The years present in the data...
years=( $(for y in $( ${CSV2CSV} -n -f date < ${csv} | tail -n +2 | awk -F- '{print $1}' | sort -u) ; do
printf "$y "
done) )

cat > ${scr} <<EOF
${AVG} -f weight --outcol 'weight (avg)' < ${csv} \
    | ${AVG} -f O2 --outcol 'O2 (avg)' \
    | ${AVG} -f hr --outcol 'HR (avg)' \
    | ${CSVPLOT} -T "${title}" \
           ${WT} ${O2} ${HR} \
           -Y 165:200,40:100 \
           -F $FMT \
           &
EOF

# EWMA for each of the years to be plotted...
MA="$(for ((i=0; i<${#years[@]}; i++)); do
    printf " | ${EWMA} -m ${MISSING} -f ${years[i]} --outcol e${years[i]}"
done)"

# Plot one line for each year...
MPL="${CSVPLOT} -F %b -T 'Stacked Weight' $(for ((i=0; i<${#years[@]}; i++)); do
    printf " -f day,e${years[i]},l,${COLORS[i]}"
done)"

cat >> ${scr} <<EOF
${DSPLIT} -c weight < ${csv} \
    ${MA} \
    | ${MPL} &

wait
EOF

bash ${scr}
