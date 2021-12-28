#/bin/bash

# Plot weight/o2/hr progression over the past year.

min () {
    if [ $1 -le $2 ] ; then
        echo $1
    else
        echo $2
    fi
}

LOOKBACK=${1:-365}
LOOKBACK=$(min $LOOKBACK $(( $(wc -l < ~/misc/weight.csv) - 1 )) )

(head -1 ~/misc/weight.csv ;
 tail -$LOOKBACK ~/misc/weight.csv) \
    | mvavg -n 7 -f weight -o 'weight (7d avg)' \
    | mvavg -n 7 -f O2 -o 'O2 (7d avg)' \
    | mvavg -n 7 -f hr -o 'HR (7d avg)' \
    | mpl -T "Weight/HR/O2 Progression" \
          -f date,O2,r,blue,'',dotted \
          -f date,'O2 (7d avg)',r,blue,'O2 (r)' \
          -f date,hr,r,green,'',dotted \
          -f date,'HR (7d avg)',r,g,'HR (r)' \
          -f date,weight,l,r,'',dotted \
          -f date,'weight (7d avg)',l,r,'Weight (l)' \
          -Y 165:190,40:100 \
          -F %m/%d \
          "$@"
