#/bin/bash

# Plot weight/o2/hr progression over the past year.

usage () {
cat <<EOF

Plot, weight, O2 saturation, and/or resting heart rate.

weight [ -e ] [ -w ] [ -o ] [ -p ] [ LOOKBACK ]

-w - exclude weight
-o - exclude O2 saturation
-p - exclude heart rate
-h - print this message
-e - use ewma instead of simple moving average

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

O2="-f date,O2,r,blue,'',dotted -f date,'O2 (avg)',r,blue,'O2 (r)'"
HR="-f date,hr,r,green,'',dotted -f date,'HR (avg)',r,green,'HR (r)'"
WT="-f date,weight,l,red,'',dotted -f date,'weight (avg)',l,red,'Weight (l)'"
tO2=O2
tHR=HR
tWT=Weight
AVG="mvavg -n 7"

while getopts 'eopwh' OPTION; do
    case "$OPTION" in
        e)
            AVG=ewma
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
trap "rm -f ${scr}" EXIT

cat > ${scr} <<EOF
mpl -T "${title}" \
           ${WT} ${O2} ${HR} \
           -Y 165:200,40:100 \
           -F $FMT \
           "$@"
EOF

(head -1 $WTCSV ;
 tail -$LOOKBACK ~/misc/weight.csv) \
    | ${AVG} -f weight -o 'weight (avg)' \
    | ${AVG} -f O2 -o 'O2 (avg)' \
    | ${AVG} -f hr -o 'HR (avg)' \
    | bash ${scr}
