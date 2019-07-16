#!/bin/bash

for f in $(ls */inputs.txt); do
    l="$(grep S1 $f)"
    if [[ ! -z "$l" ]]; then
        ref="$(echo $l | sed 's/ S[1-8]//g')"
        ref="${ref%%;*}(Ref) ;${ref##*;}"
        sed -i "s/$l/$ref/g" $f
    fi
done
