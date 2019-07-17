#!/bin/bash

for f in $(ls */inputs.txt); do
    l="$(grep S1 $f)"
    if [[ ! -z "$l" ]]; then
        ref="$(echo $l | sed 's/ S[1-8]//g')"
        ref="${ref%%;*}(Ref) ;${ref##*;}"
        sed -i "s/$l/$ref/g" $f
    fi
done

for f in $(ls -d *); do
    d=$(echo $f | grep "S7\|S8")
    if [[ ! -z $d ]]; then
        echo "title = Discharge ; To appear on the title of the graph" >> $f/inputs.txt
    fi

    r=$(echo $f | grep "S2\|S3")
    if [[ ! -z $r ]]; then
        echo "title = Roughness ; To appear on the title of the graph" >> $f/inputs.txt
    fi

    s=$(echo $f | grep "S5")
    if [[ ! -z $s ]]; then
        echo "title = Surge ; To appear on the title of the graph" >> $f/inputs.txt
    fi

    r=$(echo $f | grep "S1")
    if [[ ! -z $r ]]; then
        echo "title = Ref ; To appear on the title of the graph" >> $f/inputs.txt
    fi
done

for f in $(ls -d *); do
    d=$(echo $f | grep "S7\|S8")
    if [[ ! -z $d ]]; then
        text=$(echo $f | sed 's/_A8.*/A_Discharge/g')
        echo "output = ${text} ; Name of the folder to store the outputs" >> $f/inputs.txt
    fi

    r=$(echo $f | grep "S2\|S3")
    if [[ ! -z $r ]]; then
        text=$(echo $f | sed 's/_A8.*/A_Roughness/g')
        echo "output = ${text} ; Name of the folder to store the outputs" >> $f/inputs.txt
    fi

    s=$(echo $f | grep "S5")
    if [[ ! -z $s ]]; then
        text=$(echo $f | sed 's/_A8.*/A_Surge/g')
        echo "output = ${text} ; Name of the folder to store the outputs" >> $f/inputs.txt
    fi

    r=$(echo $f | grep "S1")
    if [[ ! -z $r ]]; then
        text=$(echo $f | sed 's/_A8.*/A_Ref/g')
        echo "output = ${text} ; Name of the folder to store the outputs" >> $f/inputs.txt
    fi
done
