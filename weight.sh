#/bin/bash

# Plot weight/o2/hr progression over the past year.

usage () {
cat <<EOF

Plot, weight, O2 saturation, and/or resting heart rate.

weight [ -w ] [ -o ] [ -p ] [ LOOKBACK ]

-w - exclude weight
-o - exclude O2 saturation
-p - exclude heart rate
-h - print this message

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

O2="-f date,O2,r,blue,'',dotted -f date,'O2 (7d avg)',r,blue,'O2 (r)'"
HR="-f date,hr,r,green,'',dotted -f date,'HR (7d avg)',r,green,'HR (r)'"
WT="-f date,weight,l,red,'',dotted -f date,'weight (7d avg)',l,red,'Weight (l)'"
tO2=O2
tHR=HR
tWT=Weight

while getopts 'opwh' OPTION; do
    case "$OPTION" in
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
    | mvavg -n 7 -f weight -o 'weight (7d avg)' \
    | mvavg -n 7 -f O2 -o 'O2 (7d avg)' \
    | mvavg -n 7 -f hr -o 'HR (7d avg)' \
    | bash ${scr}
